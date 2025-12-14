"""Implementation du triangulator."""
import struct

from triangulator.delaunay import bowyer_watson

# Il faut aussi simuler un problème de communication avec le PS


class InvalidPointSetBinary(Exception):
    """Classe permettant de gerer les expetions PointSet."""

    def __init__(self, message):
        """Init."""
        super().__init__(message)
        self.message = message


class Triangulator:
    """Classe permettant de trianguler un PointSet."""

    def __init__(self, pointset_manager):
        """Le triangulator dépend du pointset_manager.

        Mais ne connaît pas son implémentation réelle.
        """
        self.manager = pointset_manager

    def deserialize_pointset(self, binary):
        """1. DESERIALIZATION."""
        if len(binary) < 4:
            raise InvalidPointSetBinary("Binary too short: cannot read N")

        n = struct.unpack("!I", binary[:4])[0]

        if len(binary) != 4 + 8 * n:
            raise InvalidPointSetBinary(f"Inconsistent size: "
                                        f"expected {4 + 8 * n} bytes,"
                                        f" got {len(binary)}")

        points = []
        offset = 4
        for _i in range(n):
            x, y = struct.unpack("!ff", binary[offset:offset + 8])
            points.append((x, y))
            offset += 8

        return points

    def serialize_triangles(self, triangles):
        """2. SERIALIZATION."""
        binary = struct.pack("!I", len(triangles))
        for a, b, c in triangles:
            binary += struct.pack("!III", a, b, c)
        return binary

    def serialize_pointset(self, points):
        """Points : liste de tuples (x, y) -> ex: [(0.1, 0.2), (1.3, 1.4)].

        Retourne un flux binaire conforme à la spec.
        """
        nb_points = len(points)
        binary = struct.pack("!I", nb_points)

        for x, y in points:
            binary += struct.pack("!ff", x, y)

        return binary

    @staticmethod
    def is_segment(points):
        """Vérifie si tous les points sont alignés (forment un segment)."""
        n = len(points)

        # Choisir les deux premiers points pour définir la droite
        x0, y0 = points[0]
        x1, y1 = points[1]

        # Comparer tous les autres points
        for i in range(2, n):
            x, y = points[i]
            # Aire du triangle formé par (p0,p1,pi) = 0 si colinéaire
            if (x1 - x0) * (y - y0) - (y1 - y0) * (x - x0) != 0:
                return False
        return True

    def triangulate(self, pointset_id):
        """TRIANGULATION (simple ear clipping or placeholder)."""
        # --- Communication avec le PointSetManager ---
        try:
            db_result = self.manager.get_point_set(pointset_id)
        except Exception:
            # Communication failure (timeout, connection error, etc.)
            return {
                "status": 503,
                "error": "Service unavailable: "
                         "communication with PointSetManager failed"
            }

        if db_result["status"] == 404:
            return {
                "status": 404,
                "error": "PointSet not found (as reported by the PointSetManager)"
            }

        """
        Les erreurs du manager : par exemple :
         {Bad request, e.g., invalid PointSetID format, "The PointSet storage
        """
        # layer (database) is unavailable"}
        if db_result["status"] != 200:
            return db_result

        try:
            points = self.deserialize_pointset(db_result["PointSet"])
        except InvalidPointSetBinary as e:
            return {"status": 400, "error": str(e)}

        if len(points) < 3:
            return {
                "status": 400,
                "error": "Not enough points to triangulate"
            }

        if Triangulator.is_segment(points):
            return {"status": 400,
                    "error": " The pointSet points form a segment"
                    }

        # Triangulation
        # --- Internal failure can occur here ---
        try:
            triangles = bowyer_watson(points)
        except Exception:

            return {"status": 500,
                    "error": "Internal triangulation failure"
                    }

        # Serialization
        tri_bin = self.serialize_triangles(triangles)
        ps_bin = self.serialize_pointset(points)

        return {
            "status": 200,
            "Triangles": tri_bin,
            "PointSet": ps_bin,
        }