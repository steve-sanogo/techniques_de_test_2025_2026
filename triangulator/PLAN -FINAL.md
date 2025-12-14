# Plan de Test – Triangulator

## 1. Vérification du PointSetID

**Objectif** :
Vérifier que le PointSetID fourni par le client est valide, existant et conforme au format attendu pour éviter tout échec d’appel au PointSetManager.

**Scénarios de tests :**

* Envoyer un ID valide enregistré dans le PointSetManager.
* Envoyer un ID inexistant → vérifier retour 404.
* Envoyer un ID invalide (chaîne vide, caractères spéciaux, type incorrect) → retour 400 avec message explicite.

---

## 2. Vérification de la structure et des points d’un PointSet

**Objectif** :
S’assurer que le PointSet récupéré est valide, complet et cohérent avant triangulation.

**Scénarios de tests :**

* Vérifier que `N` (nombre de points) dans les 4 premiers bytes ≥ 3.
* Vérifier que la taille réelle des données correspond à `4 + 8 * N` bytes.
* Vérifier que chaque point possède des coordonnées X et Y valides (non nulles).
* Tester comportement en cas de PointSet corrompu ou incomplet (données tronquées ou incohérentes) → retour 400.
* Vérifier que le PointSet contient au moins 3 points et ne se réduit pas à une ligne → sinon retour erreur segment.

---

## 3. Vérification des Triangles

**Objectif** :
S’assurer que la sortie du Triangulator est correcte, cohérente et conforme à la spécification binaire.

**Scénarios de tests :**

* Vérifier que le nombre de points retournés correspond au PointSet original.
* Vérifier que la taille totale des triangles = `4 + 12 * nb_triangles`.
* Vérifier que chaque indice de triangle ∈ [0, nb_points - 1].
* Vérifier que chaque triangle forme effectivement un triangle géométrique non dégénéré.

---

## 4. Vérification du calcul de triangulation

**Objectif** :
S’assurer que le Triangulator calcule correctement les triangles pour un PointSet donné.

**Scénarios de tests :**

* Vérifier que les indices des triangles sont corrects et conformes aux points.
* Vérifier que tous les indices sont dans la plage valide.
* Tester le cas où les points forment une ligne → Triangulation impossible → retour 400.
* Tester des configurations simples et complexes (ex. pentagone, hexagone).

---

## 5. Vérification de la sérialisation et désérialisation

**Objectif** :
S’assurer que le Triangulator peut correctement convertir les PointSets et Triangles entre formats interne et binaire.

**Scénarios de tests :**

* Vérifier la conversion binaire → PointSet → binaire → PointSet identique.
* Vérifier la conversion binaire des triangles et correspondance avec les points.
* Vérifier le comportement en cas de données corrompues (ex. point tronqué) → lever exception `InvalidPointSetBinary` et retour 400.

---

## 6. Cas de tests d’intégration avec PointSetManager

**Objectif** :
Vérifier que le Triangulator interagit correctement avec le PointSetManager et gère les erreurs.

**Scénarios de tests :**

* Récupération d’un PointSet via son ID → succès.
* Gestion d’erreurs du PointSetManager :

  * 404 PointSet non trouvé
  * 400 ID invalide
  * 503 Service indisponible / erreur réseau
* Vérifier que le Triangulator renvoie des messages d’erreur explicites en cas d’échec de récupération.

---

## 7. Gestion des exceptions internes

**Objectif** :
Assurer que le Triangulator gère proprement les erreurs internes ou exceptions levées par l’algorithme de triangulation.

**Scénarios de tests :**

* Lever une exception dans l’algorithme Bowyer-Watson → retour 500 avec message `Internal triangulation failure`.
* Tester comportement en cas de PointSetManager indisponible → retour 503 avec message de communication.

---

## 8. Tests de robustesse et performance

**Objectif** :
Assurer la robustesse, la stabilité et les performances du Triangulator sur des cas extrêmes ou répétitifs.

**Scénarios de tests :**

* Triangulation de grands PointSets (ex. 10000 points) → mesurer temps et mémoire.
* Tests répétés sur plusieurs PointSets → vérifier stabilité et cohérence des résultats.
* Vérifier tolérance à la corruption ou à l’incomplétude des données.
* Vérifier résilience en cas de défaillance réseau ou Base de données du PointSetManager.

---

### 9. Tests segmentés (spécifiques)

**Objectif** :
S’assurer que le Triangulator détecte correctement les configurations géométriques invalides.

**Scénarios de tests :**

* Tester PointSets formant uniquement un segment → retour 400 avec message “segment”.
* Vérifier que la triangulation ne produit pas de triangles sur des points colinéaires.
