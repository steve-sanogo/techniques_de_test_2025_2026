import pytest
from unittest.mock import Mock
import uuid
import random
import struct


# ===============================
# FIXTURE : Mock du la DB
# ===============================
@pytest.fixture
def mock_db():
    db = {}
    mock = Mock()

    # Enregistrement d'un PointSet
    def save_point_set(pointset_id, points):
        db[pointset_id] = points

    # Récupération d'un PointSet
    def get_point_set(pointset_id):
        return db.get(pointset_id)

    mock.save_point_set.side_effect = save_point_set
    mock.get_point_set.side_effect = get_point_set
    return mock


# ===============================
# FIXTURE : Mock du PointSetManager
# ===============================
@pytest.fixture
def mock_pointset_manager(mock_db):
    mock = Mock()

    def check_point_set_format(binary_data):
        """
        Vérifie qu'un pointSet binaire respecte le format :
          - 4 premiers bytes : nombre de points
          - N * 8 bytes : coordonnées X,Y (floats)
        """

        # Le binaire doit faire au moins 4 bytes (pour N)
        if len(binary_data) < 4:
            return False

        # Lire le nombre de points
        (nb_points,) = struct.unpack("!I", binary_data[:4])

        # Taille attendue totale
        expected_length = 4 + nb_points * 8

        # Vérification stricte
        if len(binary_data) != expected_length:
            return False

        # Vérifier que chaque bloc X,Y est déchiffrable
        offset = 4
        for _ in range(nb_points):
            struct.unpack("!ff", binary_data[offset: offset + 8])
            offset += 8

        return True

    # Comme défini dans la documentation de l'API du PointSetManager
    def create_point_set_id():
        return str(uuid.uuid4())

    # On s'intéresse au format du point_set_id pas à son existance
    def check_point_set_id(point_set_id):
        try:
            uuid.UUID(point_set_id)
            return True
        except ValueError:
            return False

    mock.db_available = True  # Permet de similer des tests avec le scénario “DB non disponible"

    def check_connexion_to_db():
        return mock.db_available

    # Fonction d'enregistrement via la DB
    def register_point_set(points):

        if not check_point_set_format(points):
            return {"status": 400, "error": "Invalid binary format"}

        if not check_connexion_to_db():
            return {"status": 503, "error": "The PointSet storage layer (database) is unavailable."}

        point_set_id = create_point_set_id()
        mock_db.save_point_set(point_set_id, points)

        return {"status": 201, "pointSetId": point_set_id}

    def get_point_set(point_set_id):
        if not check_point_set_id(point_set_id):
            return {"status": 400, "error": "Bad request, e.g., invalid PointSetID format."}

        if not check_connexion_to_db():
            return {"status": 503, "error": "The PointSet storage layer (database) is unavailable."}

        point_set = mock_db.get_point_set(point_set_id)
        if point_set is None:
            return {"status": 404, "error": "PointSet ID not found"}

        return {"status": 200, "PointSet": point_set}

    mock.register_point_set.side_effect = register_point_set
    mock.get_point_set.side_effect = get_point_set
    mock.check_point_set_format = check_point_set_format
    mock.check_point_set_id = check_point_set_id

    mock.check_connection_to_db = check_connexion_to_db
    mock.set_db_available = lambda val: setattr(mock, "db_available", val)
    return mock


# ===============================
# FIXTURE : Mock du Triangulator
# ===============================
@pytest.fixture
def triangulate_point_set(mock_pointset_manager):
    mock = Mock()

    # Sérialiser un PointSet
    mock.serialize_pointset.side_effect = lambda points: b'\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00?\x80\x00' \
                                                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00?\x80\x00\x00 '

    # Sérialiser des triangles
    mock.serialize_triangles.side_effect = lambda \
        triangles: b'\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00?\x80\x00' \
                   b'\x00\x00\x00\x00\x00\x00\x00\x00\x00?\x80\x00\x00'

    def deserialize_point_set(binary_data):
        """Convertit un PointSet binaire en liste de tuples (x, y)"""
        nb_points = struct.unpack("!I", binary_data[:4])[0]
        points = []
        offset = 4
        for _ in range(nb_points):
            x, y = struct.unpack("!ff", binary_data[offset:offset + 8])
            points.append((x, y))
            offset += 8
        return points

    def triangulate(pointset_id):

        # Cas ou les points formes
        if pointset_id == "pointset_segment":
            return {"status": 400, "error": "PointSet is a segment."}

        # appel au PointSetManager
        result = mock_pointset_manager.get_point_set(pointset_id)

        # Le pointset n’existe pas
        if result["status"] == 404:
            return {
                "status": 404,
                "error": "The specified PointSetID was not found (as reported by the PointSetManager)."
            }
        # Les erreurs du manager
        if result["status"] != 200:
            return result

        points = deserialize_point_set(result["PointSet"])
        n = len(points)

        # Triangulation impossible
        if n < 3:
            return {"status": 400, "error": "PointSet too small to be triangulated."}

        # Simulation d'une panne interne aléatoire
        if random.random() < 0.1:  # 10% failure
            return {"status": 500, "error": "Internal server error: triangulation algorithm failed."}

        # Construire un triangle bidon + sérialisation
        triangles = [(0, 1, 2)]  # dummy
        triangles_bin = mock.serialize_triangles(triangles)
        pointset_bin = mock.serialize_pointset(points)

        return {"status": 200, "Triangles": triangles_bin, "PointSet": pointset_bin}

    mock.triangulate.side_effect = triangulate
    mock.deserialize_pointset.side_effect = deserialize_point_set
    return mock
