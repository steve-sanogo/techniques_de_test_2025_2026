"""Module de triangulation utilisant l'algorithme de Bowyer-Watson."""
from triangulator.geometry import circumcircle, point_in_circumcircle


def bowyer_watson(points):
    """Construit un super triangle très large pour l'algorithme de Bowyer-Watson."""
    super_triangle = [
        (-1e9, -1e9),
        (1e9, -1e9),
        (0,     1e9)
    ]

    triangles = [(0, 1, 2)]
    pts = super_triangle + points  # index shift

    for i in range(3, len(pts)):
        p = pts[i]
        bad_triangles = []

        # Trouver les triangles dont le cercle contient p
        for tri in triangles:
            c = circumcircle(pts[tri[0]], pts[tri[1]], pts[tri[2]])
            if c and point_in_circumcircle(p, c):
                bad_triangles.append(tri)

        #Trouver la "cavité"
        edges = []
        for tri in bad_triangles:
            for e in [(tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])]:
                if e in edges:
                    edges.remove(e)
                else:
                    edges.append(e)

        # Retirer les triangles "mauvais"
        for tri in bad_triangles:
            triangles.remove(tri)

        # Re-tesseler les nouvelles faces
        for e in edges:
            triangles.append((e[0], e[1], i))

    # Retirer les triangles contenant des sommets du super-triangle
    triangles = [t for t in triangles if all(v >= 3 for v in t)]

    # Nettoyage des indices
    return [(a-3, b-3, c-3) for (a, b, c) in triangles]
