import struct
import uuid


def make_pointset_binary(points):
    """Construit un binaire valide pour N points."""
    N = len(points)
    data = struct.pack("!I", N)  # Longueur sur 4 bytes
    for x, y in points:
        data += struct.pack("!ff", x, y)
    return data


def test_triangulate_success(monkeypatch, mock_pointset_manager, triangulate_point_set):
    """Force random.random() à renvoyer 1 pour ne pas simuler une erreur interne."""

    monkeypatch.setattr("random.random", lambda: 1)
    # Créer un pointset valide
    points = [(0, 0), (1, 0), (0, 1)]
    binary = make_pointset_binary(points)

    reg = mock_pointset_manager.register_point_set(binary)
    psid = reg["pointSetId"]

    res = triangulate_point_set.triangulate(psid)

    assert res["status"] == 200
    assert "Triangles" in res
    assert "PointSet" in res


def test_triangulate_pointset_not_found(triangulate_point_set):
    faux_id = str(uuid.uuid4())
    res = triangulate_point_set.triangulate(faux_id)

    assert res["status"] == 404
    assert "not found" in res["error"].lower()


# test avec un format incorrect de PointSetId
def test_triangulate_invalid_uuid(triangulate_point_set):
    res = triangulate_point_set.triangulate("bad-id")
    assert res["status"] == 400


# test de Triangulation avec une db non accessible
def test_triangulate_db_unavailable(mock_pointset_manager, triangulate_point_set):
    mock_pointset_manager.set_db_available(False)

    random_id = str(uuid.uuid4())  # l'existance du PointSet nous importe peu
    res = triangulate_point_set.triangulate(random_id)

    assert res["status"] == 503


def test_triangulate_few_points(mock_pointset_manager, triangulate_point_set):
    points = [(0, 0), (1, 1)]  # seulement 2 points
    binary = make_pointset_binary(points)

    reg = mock_pointset_manager.register_point_set(binary)
    psid = reg["pointSetId"]

    res = triangulate_point_set.triangulate(psid)

    assert res["status"] == 400
    assert "too small" in res["error"].lower()


def test_triangulate_segment(triangulate_point_set):
    psid = "pointset_segment"

    res = triangulate_point_set.triangulate(psid)
    assert res["status"] == 400
    assert "is a segment" in res["error"].lower()


def test_triangulate_internal_error(monkeypatch, mock_pointset_manager, triangulate_point_set):
    """Force random.random() à renvoyer 0 pour simuler une erreur interne."""
    monkeypatch.setattr("random.random", lambda: 0.01)

    points = [(0, 0), (1, 0), (0, 1)]
    binary = make_pointset_binary(points)

    reg = mock_pointset_manager.register_point_set(binary)
    psid = reg["pointSetId"]

    res = triangulate_point_set.triangulate(psid)

    assert res["status"] == 500
    assert "internal" in res["error"].lower()


def test_stressTriangulator(monkeypatch, mock_pointset_manager, triangulate_point_set):
    """
    :param mock_pointset_manager:
    :return:
    """
    monkeypatch.setattr("random.random", lambda: 1)
    for i in range(1000):

        # Créer un pointset valide
        points = [(0 + i, 0), (1 + i, 0), (0 + i, 1)]
        binary = make_pointset_binary(points)

        reg = mock_pointset_manager.register_point_set(binary)
        psid = reg["pointSetId"]

        res = triangulate_point_set.triangulate(psid)

        assert res["status"] == 200
        assert "Triangles" in res
        assert "PointSet" in res