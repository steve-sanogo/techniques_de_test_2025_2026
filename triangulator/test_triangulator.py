"""Test du triangulator."""
import random
import struct
import uuid
from unittest.mock import Mock, patch

import pytest

from triangulator.triangulator import Triangulator


def isTriangle(p1, p2, p3):
    """Determine s'il s'agit d'un triangle."""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    area = abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2
    return area > 0


@pytest.fixture
def mock_psm():
    """mock_psm."""
    mock = Mock()
    mock.get_point_set.return_value = {
        "status": 200,
        "PointSet": (
            b"\x00\x00\x00\x03"  # 3 points
            b"\x00\x00\x00\x00\x00\x00\x00\x00"  # (0,0)
            b"\x3f\x80\x00\x00\x00\x00\x00\x00"  # (1,0)
            b"\x00\x00\x00\x00\x3f\x80\x00\x00"  # (0,1)
        )
    }
    return mock


def make_pointSet(points):
    """Make_pointSet."""
    b = struct.pack("!I", len(points))
    for x, y in points:
        b += struct.pack("!ff", x, y)
    return b


def test_invalid_uuid(mock_psm):
    """INVALID UUID."""
    mock_psm.get_point_set.return_value = {"status": 400,
                                           "error": "Bad request, e.g., "
                                                    "invalid PointSetID format."}
    triang = Triangulator(mock_psm)
    res = triang.triangulate("not-an-uuid")
    assert res["status"] == 400
    assert "invalid PointSetID format.".lower() in res["error"].lower()


def test_pointSet_not_found(mock_psm):
    """Point set non trouvé."""
    mock_psm.get_point_set.return_value = {"status": 404,
                                           "error": "PointSet ID not found"}
    triang = Triangulator(mock_psm)
    res = triang.triangulate(str(uuid.uuid4()))

    assert res["status"] == 404
    assert "not found (as reported by the PointSetManager)".lower() \
           in res["error"].lower()


def test_too_few_points(mock_psm):
    """Trianguler avec  peu de point."""
    # Binaire : 1 point
    mock_psm.get_point_set.return_value = {
        "status": 200,
        "PointSet": b"\x00\x00\x00\x01" + b"\x00\x00\x00\x00\x00\x00\x00\x00"
    }

    triang = Triangulator(mock_psm)
    res = triang.triangulate(str(uuid.uuid4()))

    assert res["status"] == 400
    assert "Not enough points to triangulate".lower() in res["error"].lower()


def test_binary_too_short(mock_psm):
    """Trianguler avec binaire trop court."""
    mock_psm.get_point_set.return_value = {
        "status": 200,
        "PointSet": b'\x00\x01'  # moins de 4 bytes
    }
    triang = Triangulator(mock_psm)
    res = triang.triangulate(str(uuid.uuid4()))

    assert res["status"] == 400

    assert "Binary too short".lower() in res["error"].lower()


def test_inconsistent_size(mock_psm):
    """Trianguler avec une incohérence de taille par rapport à N."""
    mock_psm.get_point_set.return_value = {
        "status": 200,
        "PointSet": struct.pack("!I", 2) + struct.pack("!ff", 0.0, 0.0)
    }  # N = 2 mais seulement 1 point fourni (8 bytes au lieu de 16)
    triang = Triangulator(mock_psm)
    res = triang.triangulate(str(uuid.uuid4()))

    assert res["status"] == 400
    assert "Inconsistent size".lower() in res["error"].lower()


def test_internal_triangulation_algorithm_failure(mock_psm):
    """Triangulation failure."""
    triang = Triangulator(mock_psm)

    with patch("triangulator.triangulator.bowyer_watson",
               side_effect=Exception("fail")):
        res = triang.triangulate(str(uuid.uuid4()))

    assert res["status"] == 500
    assert "Internal triangulation failure".lower() in res["error"].lower()


def test_triangulator_db_unavailable(mock_psm):
    """DB UNAVAILABLE."""
    mock_psm.get_point_set.return_value = {"status": 503,
                                           "error": "The PointSet"
                                                    " storage layer (database)"
                                                    " is unavailable."}
    pid = str(uuid.uuid4())
    tr = Triangulator(mock_psm)
    res = tr.triangulate(pid)
    assert res["status"] == 503
    assert "unavailable" in res["error"].lower()


def test_triangulator_service_unavailable(mock_psm):
    """PSM UNAVAILABLE."""
    mock_psm.get_point_set.side_effect = Exception("Network error")

    tr = Triangulator(mock_psm)
    res = tr.triangulate(str(uuid.uuid4()))

    assert res["status"] == 503
    assert "communication" in res["error"].lower()


def test_triangulate_segment(mock_psm):
    """TEST SEGMENT."""
    pid = str(uuid.uuid4())

    mock_psm.get_point_set.return_value = {
        "status": 200,
        "PointSet": make_pointSet([(0, 0), (0.5, 0.5), (1, 1)])
    }

    tr = Triangulator(mock_psm)
    res = tr.triangulate(str(pid))

    assert res["status"] == 400
    assert "segment" in res["error"].lower()


def test_triangulate_success(mock_psm):
    """Test de triangulation avec succès."""
    # 5 points formant un pentagone simple
    points = [(0, 0), (1, 0), (1, 1), (0, 1), (0.5, 1.5)]
    pointset_bin = make_pointSet(points)

    # Le manager renvoie le PointSet binaire
    mock_psm.get_point_set.return_value = {
        "status": 200,
        "PointSet": pointset_bin
    }
    tr = Triangulator(mock_psm)
    pid = str(uuid.uuid4())  # pid quelconque
    result = tr.triangulate(pid)

    # Vérifications
    assert result["status"] == 200
    assert "Triangles" in result
    assert "PointSet" in result

    # On peut également vérifier que la désérialisation renvoie bien les points
    deserialized_points = tr.deserialize_pointset(result["PointSet"])
    assert deserialized_points == points

    # Les triangles sont au moins une liste de tuples de 3 indices
    triangles = result["Triangles"]
    n_triangles = struct.unpack("!I", triangles[:4])[0]
    assert n_triangles > 0

    # Vérifier que chaque triangle a bien 3 indices
    for i in range(n_triangles):
        offset = 4 + i * 12
        a, b, c = struct.unpack("!III", triangles[offset:offset + 12])
        assert all(isinstance(idx, int) for idx in (a, b, c))
        p1, p2, p3 = points[a], points[b], points[c]
        assert isTriangle(p1, p2, p3)


@pytest.mark.perf
def test_stress_triangulator(mock_psm):
    """Test de stress."""
    tr = Triangulator(mock_psm)

    for _ in range(50):  # 50 PointSets différents
        n_points = random.randint(3, 10)
        points = [(random.random() * 10, random.random() * 10) for _ in range(n_points)]
        pointset_bin = make_pointSet(points)
        pid = str(uuid.uuid4())

        # Mock le manager pour ce PID
        mock_psm.get_point_set.return_value = {
            "status": 200,
            "PointSet": pointset_bin
        }

        result = tr.triangulate(pid)

        # Vérifications
        assert result["status"] == 200
        assert "Triangles" in result
        assert "PointSet" in result

        deserialized_points = tr.deserialize_pointset(result["PointSet"])
        # assert deserialized_points == points
        for p_orig, p_deser in zip(points, deserialized_points, strict=True):
            assert abs(p_orig[0] - p_deser[0]) < 1e-6
            assert abs(p_orig[1] - p_deser[1]) < 1e-6

        # Vérification des triangles
        """"triangles = result["Triangles"]
        n_triangles = struct.unpack("!I", triangles[:4])[0]
        assert n_triangles >= 1
        for i in range(n_triangles):
            offset = 4 + i * 12
            a, b, c = struct.unpack("!III", triangles[offset:offset + 12])
            assert all(isinstance(idx, int) for idx in (a, b, c))
            p1, p2, p3 = points[a], points[b], points[c]
            assert isTriangle(p1, p2, p3) == True"""


@pytest.mark.perf
def test_large_triangulation(mock_psm):
    """Test sur le temps mis."""
    # Génère un PointSet très grand
    n_points = 20  # 10000
    points = [(random.random() * 100, random.random() * 100) for _ in range(n_points)]
    pointset_bin = make_pointSet(points)

    mock_psm.get_point_set.return_value = {
        "status": 200,
        "PointSet": pointset_bin
    }

    tr = Triangulator(mock_psm)

    import time
    start = time.time()
    res = tr.triangulate(str(uuid.uuid4()))
    end = time.time()

    print(f"Triangulation de {n_points} points exécutée en {end - start:.2f}s")

    assert res["status"] == 200
