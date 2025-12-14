"""Utile pour la triangulation."""
import math


def circumcircle(p1, p2, p3):
    """Retourne (xc, yc, r) le cercle circonscrit au triangle (p1, p2, p3)."""
    (x1, y1), (x2, y2), (x3, y3) = p1, p2, p3

    d = 2 * (x1 * (y2 - y3) +
             x2 * (y3 - y1) +
             x3 * (y1 - y2))

    if d == 0:
        return None  # points alignés

    ux = (
                 (x1 ** 2 + y1 ** 2) * (y2 - y3) +
                 (x2 ** 2 + y2 ** 2) * (y3 - y1) +
                 (x3 ** 2 + y3 ** 2) * (y1 - y2)
         ) / d

    uy = (
                 (x1 ** 2 + y1 ** 2) * (x3 - x2) +
                 (x2 ** 2 + y2 ** 2) * (x1 - x3) +
                 (x3 ** 2 + y3 ** 2) * (x2 - x1)
         ) / d

    r = math.dist((ux, uy), (x1, y1))

    return ux, uy, r


def point_in_circumcircle(p, circle):
    """Point_in_circumcircle."""
    xc, yc, r = circle
    return math.dist((xc, yc), p) <= r
