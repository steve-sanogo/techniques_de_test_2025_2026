import struct
import uuid


def make_pointset_binary(points):
    """Construit un binaire valide pour N points."""
    N = len(points)
    data = struct.pack("!I", N)
    for x, y in points:
        data += struct.pack("!ff", x, y)
    return data


def test_point_set_structure(mock_pointset_manager):
    """
    Test des cas d'erreur du check_point_set_format :
    -Binaire trop court (< 4 bytes)
    -Impossible de lire le nombre de points
    - Longueur incorrecte par rapport à N
    """

    # Binaire trop court
    binary = b'\x00\x01'
    res = mock_pointset_manager.register_point_set(binary)
    assert res["status"] == 400

    # Impossible de lire le nombre de points
    bad_header = b'\xff' * 4  # tente de lire un entier énorme
    res = mock_pointset_manager.register_point_set(bad_header)
    assert res["status"] == 400

    # Longueur incorrecte : N=1 mais pas assez de données pour 1 point (8 bytes)
    wrong_length = struct.pack("!I", 1) + b'\x00\x00\x00\x00'  # 4 bytes au lieu de 8
    res = mock_pointset_manager.register_point_set(wrong_length)
    assert res["status"] == 400


def test_register_point_set_valid(mock_pointset_manager):
    points = [(0.0, 0.0), (1.0, 1.0)]
    binary = make_pointset_binary(points)

    res = mock_pointset_manager.register_point_set(binary)

    assert res["status"] == 201
    assert "pointSetId" in res
    uuid.UUID(res["pointSetId"])


def test_register_point_set_invalid_format(mock_pointset_manager):
    bad_binary = b"\x00\x00\x00\x02\x00\x00\x00"  # trop court

    res = mock_pointset_manager.register_point_set(bad_binary)

    assert res["status"] == 400
    assert "Invalid binary format" in res["error"]


def test_register_point_set_db_unavailable(mock_pointset_manager):
    # Simulation d'indisponibilité de la base de données
    mock_pointset_manager.set_db_available(False)

    points = [(0.0, 0.0), (1.0, 1.0)]
    binary = make_pointset_binary(points)

    res = mock_pointset_manager.register_point_set(binary)

    assert res["status"] == 503
    assert "storage layer (database) is unavailable" in res["error"].lower()


def test_get_point_set_valid(mock_pointset_manager):
    # On enregistre un pointSet
    points = [(1.0, 2.0), (3.0, 4.0)]
    binary = make_pointset_binary(points)

    reg = mock_pointset_manager.register_point_set(binary)
    pointset_id = reg["pointSetId"]

    # On le récupère
    res = mock_pointset_manager.get_point_set(pointset_id)

    assert res["status"] == 200
    assert res["PointSet"] == binary


def test_get_point_set_invalid_uuid(mock_pointset_manager):
    res = mock_pointset_manager.get_point_set("not-a-uuid")
    assert res["status"] == 400


def test_get_point_set_not_found(mock_pointset_manager):
    random_id = str(uuid.uuid4())
    res = mock_pointset_manager.get_point_set(random_id)

    assert res["status"] == 404
    assert "not found" in res["error"].lower()


def test_get_point_set_db_unavailable(mock_pointset_manager):
    mock_pointset_manager.set_db_available(False)

    random_id = str(uuid.uuid4())
    res = mock_pointset_manager.get_point_set(random_id)

    assert res["status"] == 503
    assert "database" in res["error"].lower()


def test_stressPointSetManager(mock_pointset_manager):
    """
        Simulation d'un enregistement simultanné de plusieurs pointset
    """
    mock_pointset_manager.set_db_available(True)

    for i in range(1000):
        points = [(0.0, 0.0), (1.0, 1.0)]
        binary = make_pointset_binary(points)
        mock_pointset_manager.register_point_set(binary)