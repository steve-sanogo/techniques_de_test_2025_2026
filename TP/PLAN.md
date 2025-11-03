# Plan de test
## 1.	Vérification du PointSetID
###Objectif
Vérifier que le PointSetID fourni par le client est valide, existant et conforme au format attendu, afin d’éviter tout échec d’appel au PointSetManager.
### Scénarii de tests : 
-	Envoyer un ID renvoyé précédemment par le PointSetManager lors de l’enregistrement.
-	Envoyer un ID qui n’existe pas dans le PointSetManager
-	Envoyer une chaîne vide ("") comme ID.
-	Envoyer un PointSetID contenant des caractères spéciaux (ex. "!@#$%^&*()").
-	Envoyer un PointSetID de type incorrect (par exemple un nombre entier, ou un décimal au lieu d’une chaîne de caractères)

###2.	Vérifier la structure et les points d’un PointSet
###Objectif
S’assurer que le PointSet récupéré est valide, complet et cohérent avant le calcul de triangulation.
###Scénarii de tests : 
-	Vérifier que le nombre de points indiqué dans les 4 premiers bytes différent de 0.
-	Vérifier que le nombre de points indiqué est supérieur à 3.
-	Vérifier que la taille réelle des données (hors les 4 premiers bytes) correspond bien à nombre_points * 8.
-	Vérifier que les coordonnées X et Y de chaque point ne sont pas vides.
-	Vérifier que le Pointset ne contient pas des points identiques (points en double)

###3.	Vérification de la structure et des points des Triangles
###Objectif
Vérifier que la sortie du Triangulator est correcte, cohérente et conforme à la spécification binaire.
###Scénarii de tests : 
-	Vérifier que le nombre de points = nombre de points du PointSet d’origine
-	Vérifier que le nombre de bytes correct est correct c’est à dire 4 + 8 * nb_points
-	Coordonnées valides (non vides, type correct)
-	Nombre de triangles conforme au calcul attendu
-	Chaque indice ∈ [0, nb_points - 1]
-	Taille totale : 4 + 12 * nb_triangles

### 4.	Vérification du calcul de triangulation
### Objectif
Vérifier que le Triangulator calcule correctement les triangles pour un PointSet donné.

### Scénarii de tests : 
-	Indices corrects, sommets conformes
-	Tous indicent valides et dans la plage des sommets
-	Prévoir le cas où les points entrés ne sont pas une ligne. S’ils ne sont, le gérer et retourner un message d’erreur : « Triangulation impossible » 

### 5.	Cas de tests d’intégration avec PointSetManager
### Objectif : 

S’assurer que le Triangulator interagit correctement avec le PointSetManager, en récupérant les ensembles de points via leur ID et en gérant de manière appropriée les erreurs ou défaillances

### Scénarii de tests : 
-	Vérifier la récupération d’un PointSet via son ID
-	Gestion d’erreurs du PointSetManager (404, 500, timeout)
-	Vérifier que le Triangulator renvoie des erreurs explicites en cas d’échec

###6.	Tests de robustesse et performance
###Objectif
S’assurer de la robustesse, de la stabilité et des performances du Triangulator dans des conditions extrêmes ou anormale.
###Scénarii de tests : 
-	Triangulation d’un grand PointSet (plus de 900 points), afin de vérifier le temps de calcul et de consommation mémoire
-	Gestion de données corrompues ou incomplètes
-	Test de résilience lors de défaillance réseau avec PointSetManager
-	Test de résilience lors de défaillance réseau du PointSetManager avec la Base de données
-	Vérification de la stabilité sur des appels répétés
