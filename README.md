# Techniques de test 2025/2026

Forkez le repository pour pouvoir en faire votre version avec votre travail.  
Le sujet du TP se trouve [ici](./TP/SUJET.md)

## Étudiant

Vous devez compléter cette partie pour qu'on puisse vous identifier.  

Nom : SANOGO  
Prénom : M Steve Belvin  
Groupe de TP : M1 AI

## Remarques particulières

Commandes batch : chemin --> techniques_de_test_2025_2026/

* test.bat : lance tous les tests (basé sur pytest).

* unit_test.bat : lance tous les tests sauf les tests de performance (basé sur pytest).

* perf_test.bat : lance uniquement les tests de performance (basé sur pytest).

* coverage.bat : génère un rapport de couverture de code (basé sur coverage).

* lint.bat : valide la qualité de code (basé sur ruff check).

* doc.bat : génère la documentation en HTML (basé sur pdoc3).


Chemin : techniques_de_test_2025_2026/triangulator

* delaunay.py : implémentation de l’algorithme de Bowyer-Watson pour la triangulation de Delaunay.

* geometry.py : fonctions géométriques utilitaires (cercle circonscrit, alignement de points, etc.).

* PLAN -FINAL.md : notre nouveau plan de test 

* triangulator.py : classe principale Triangulator pour gérer les PointSets et la triangulation.

* test_triangulator.py : tests unitaires et tests de performance pour la classe Triangulator.

* triangulator.html : documentation HTML générée pour la classe Triangulator.

* test_triangulator.html : documentation HTML des tests du Triangulator.

* coverage_triangulator.jpg : résultat des tests de performance et couverture de code pour la classe Triangulator.
