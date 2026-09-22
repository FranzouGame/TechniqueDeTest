# TODO

## Tests unitaires
### Test de la fonction conversion des données binaires:

| Cas | Entrée | Attendu | Pourquoi |
|-----|--------|---------|----------|
| Ensemble valide | header = 1, point (1.0, 2.0) en binaire | `[(1.0, 2.0)]` | Cas nominal : vérifie l'ordre X puis Y |
| Ensemble vide | header = 0 | `[]` | Vérifie que la fonction gère correctement un ensemble vide |
| Ensemble avec plusieurs points | header = 3, points (1.0, 2.0), (3.0, 4.0), (5.0, 6.0) en binaires | `[(1.0, 2.0), (3.0, 4.0), (5.0, 6.0)]` | Vérifie que la fonction gère correctement un ensemble avec plusieurs points |
| Ensemble avec des coordonnées négatives | header = 2, points (-1.0, -2.0), (-3.0, -4.0) en binaires | `[(-1.0, -2.0), (-3.0, -4.0)]` | Vérifie que la fonction gère correctement les coordonnées négatives |
| Ensemble avec des coordonnées à virgule flottante | header = 2, points (1.5, 2.5), (3.5, 4.5) en binaires | `[(1.5, 2.5), (3.5, 4.5)]` | Vérifie que la fonction gère correctement les coordonnées à virgule flottante |
| Le header annonce 5 point mais seulement 3 sont présents | header = 5, points (1.0, 2.0), (3.0, 4.0), (5.0, 6.0) en binaires | `ValueError` | Vérifie que la fonction gère correctement les incohérences entre le header et le nombre de points présents |
| Le binaire fait moins de 4 bytes | binaire de 3 bytes | `ValueError` | Vérifie que la fonction gère correctement les entrées binaires trop courtes |
| Il y a trop de bytes par rapport au header | header = 1, binaire de 20 bytes | `ValueError` | Vérifie que la fonction gère correctement les entrées binaires trop longues |

### Test de la fonction de triangulation:

| Cas | Entrée | Attendu | Pourquoi |
|-----|--------|---------|----------|
| Cas nominal | points (0.0, 0.0), (4.0, 0.0), (0.0, 3.0) | Un triangle en sortie (succès) | Vérifie que la fonction de triangulation fonctionne correctement avec un ensemble de points valides |
| Ensemble vide | () | `ValueError` | Vérifie que la fonction de triangulation gère correctement un ensemble vide |
| Ensemble avec un seul point | points (1.0, 2.0) | `ValueError` | Vérifie que la fonction de triangulation gère correctement un ensemble avec un seul point |
| Ensemble avec deux points | points (1.0, 2.0), (3.0, 4.0) | `ValueError` | Vérifie que la fonction de triangulation gère correctement un ensemble avec deux points |
| Ensemble avec des points colinéaires | points (1.0, 2.0), (2.0, 4.0), (3.0, 6.0) -> (Bx - Ax) * (Cy - Ay) - (By - Ay) * (Cx - Ax) = 0 | `ValueError` | Vérifie que la fonction de triangulation gère correctement un ensemble de points colinéaires |
| Ensemble avec des coordonnées négatives | points (-1.0, -1.0), (-4.0, -1.0), (-1.0, -5.0) | Un triangle en sortie (succès) | Vérifie que la fonction de triangulation gère correctement un ensemble avec des coordonnées négatives |
| Ensemble avec des coordonnées à virgule flottante | points (0.5, 0.5), (2.5, 0.5), (1.5, 2.5) | Un triangle en sortie (succès) | Vérifie que la fonction de triangulation gère correctement un ensemble avec des coordonnées à virgule flottante |
| Ensemble de points qui forme un carré | points (0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0) | Deux triangles en sortie (succès) | Vérifie que la fonction de triangulation gère correctement un ensemble de points formant un carré |
| Ensemble de points qui forme un triangle avec un points intérieur | points (0.0, 0.0), (4.0, 0.0), (0.0, 4.0), (1.0, 1.0) | Trois triangles en sortie (succès) | Vérifie que la fonction de triangulation gère correctement un ensemble de points formant un triangle avec un point intérieur |
| Ensemble de points aléatoires | 100 points générés aléatoirement, coordonnées dans [-1000, 1000] | Chaque point apparaît dans au moins un triangle, tous les triangles ont une aire différente de 0, tous les indices sont compris entre 0 et N-1 | Vérifie des propriétés toujours vraies sur un cas dont on ne peut pas prédire le résultat exact à la main |
| Ensemble avec des points dupliqués | points (1.0, 2.0), (1.0, 2.0), (3.0, 4.0), (0.0, 3.0) | `ValueError` | Un point en double produirait un triangle d'aire nulle : on préfère refuser l'ensemble plutôt que renvoyer une triangulation invalide |

### Test de la fonction de conversion des triangles en données binaires:

Le binaire produit est composé de deux parties :
- Partie sommets (format PointSet) : 4 bytes pour N, puis 8 bytes par point (X puis Y en `float`)
- Partie triangles : 4 bytes pour T, puis 12 bytes par triangle (3 indices en `unsigned long`)

Taille attendue : 8 + 8N + 12T bytes.

Pour vérifier le contenu, on redécode la partie sommets avec la fonction de conversion binaire → points
(test aller-retour), puis on relit les indices de la partie triangles.

| Cas | Entrée | Attendu | Pourquoi |
|-----|--------|---------|----------|
| Cas nominal | points [(0.0, 0.0), (4.0, 0.0), (0.0, 3.0)], triangles [(0, 1, 2)] | 44 bytes, sommets redécodés = points d'entrée, triangle lu = (0, 1, 2) | Cas nominal : vérifie la structure en deux parties et l'ordre des données |
| Ensemble vide | points [], triangles [] | 8 bytes, tous à 0 (N = 0 et T = 0) | Les deux compteurs doivent être présents même sans données |
| Ensemble avec un seul triangle | points [(1.0, 2.0), (3.0, 4.0), (5.0, 6.0)], triangles [(0, 1, 2)] | 44 bytes, sommets redécodés = points d'entrée, triangle lu = (0, 1, 2) | L'encodeur ne fait pas de géométrie : il encode même des points alignés |
| Ensemble avec plusieurs triangles | points [(0.0, 0.0), (4.0, 0.0), (0.0, 3.0), (1.0, 2.0), (3.0, 4.0), (5.0, 6.0)], triangles [(0, 1, 2), (3, 4, 5)] | 80 bytes, sommets redécodés = points d'entrée, triangles lus = (0, 1, 2), (3, 4, 5) dans cet ordre | Vérifie que plusieurs triangles sont écrits à la suite, sans décalage |
| Ensemble avec des coordonnées négatives | points [(-1.0, -1.0), (-4.0, -1.0), (-1.0, -5.0)], triangles [(0, 1, 2)] | 44 bytes, sommets redécodés = points d'entrée | Vérifie que le signe des `float` est conservé à l'encodage |
| Ensemble avec des coordonnées à virgule flottante | points [(0.5, 0.5), (2.5, 0.5), (1.5, 2.5)], triangles [(0, 1, 2)] | 44 bytes, sommets redécodés = points d'entrée | Vérifie que la partie décimale est conservée à l'encodage |
| Un triangle avec l'indice 5 alors qu'il n'y a que 3 points | Points [(0.0, 0.0), (4.0, 0.0), (0.0, 3.0)] triangle [(0, 1, 5)] | `ValueError` | Vérifie que la fonction de conversion gère correctement un triangle avec un indice invalide |

## Tests d'api
  Pour tout les tests d'api, on va donc crée un mock de l'api PointSetManager, qui va renvoyer les coordonnées des points, 
  pour pouvoir tester l'api sans avoir besoin d'un serveur réel.
  
    GET /triangulation/{Id valide} alors que le pointSetId est valide, renvoie un code 200 et les données triangulés
      Entrée : 
        -Id valide
      Attendu :
        -Code 200
        -Données triangulés
      Pourquoi : 
        -Vérifier que l'api renvoie bien les données triangulés pour un pointSetId valide
    
    Get /triangulation/{Id valide} alors que le pointSetId n'existe pas, renvoie un code 404 et un message d'erreur
      Entrée : 
        -Id valide mais inexistant
      Attendu :
        -Code 404
        -Message d'erreur
      Pourquoi : 
        -Vérifier que l'api renvoie bien un message d'erreur pour un pointSetId invalide

    Get /triangulation/{Id invalide} renvoie un code 400 et un message d'erreur
      Entrée : 
        -Id invalide
      Attendu :
        -Code 400
        -Message d'erreur
      Pourquoi : 
        -Vérifier que l'api renvoie bien un message d'erreur pour un pointSetId invalide

    Get /triangulation/{Id valide ou Invalide} alors que le serveur est indisponible, renvoie un code 500 et un message d'erreur
      Entrée : 
        -Id valide ou invalide
      Attendu :
        -Code 500
        -Message d'erreur
      Pourquoi : 
        -Vérifier que l'api renvoie bien un message d'erreur pour un pointSetId valide ou invalide lorsque le serveur est indisponible

    Get /triangulation/{Id valide ou Invalide} alors que le service est indisponible, renvoie un code 503 et un message d'erreur
      Entrée : 
        -Id valide ou invalide
      Attendu :
        -Code 503
        -Message d'erreur
      Pourquoi : 
        -Vérifier que l'api renvoie bien un message d'erreur pour un pointSetId valide ou invalide lorsque le service est indisponible


## Tests de performance

## Qualité