# TODO

## Hypothèse sur le format binaire

La spécification dit combien de bytes fait chaque donnée, mais pas dans quel ordre ces bytes sont
écrits. Il y a deux ordres possibles, et un nombre écrit dans un ordre et relu dans l'autre ne donne
pas la même valeur. Comme le problème ne change pas la taille des données, il serait difficile à
repérer.

J'ai donc choisi le petit-boutiste (little-endian) pour tous mes tests, c'est à dire l'option par
défaut sur la plupart des machines. Si le vrai PointSetManager utilise l'autre ordre, il faudra le
changer, mais au moins le choix est écrit quelque part.

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

Ces tests appellent l'API du Triangulator avec le client de test de Flask, sans lancer de vrai serveur.
Le PointSetManager n'est pas lancé non plus, il est remplacé par un mock, qui joue le rôle du vrai
service et renvoie ce que celui-ci renverrait, c'est à dire un code HTTP et, en cas de succès, un
PointSet au format binaire. Le mock permet aussi de simuler une panne réseau (aucune réponse).

Dans tous les cas d'erreur, on vérifie le code HTTP, mais aussi que le corps de la réponse est un JSON
contenant les champs `code` et `message`, comme décrit dans le schéma Error de la spécification.

| Cas | Entrée (requête et réponse du mock) | Attendu | Pourquoi |
|-----|--------|---------|----------|
| Cas nominal | GET /triangulation/{UUID valide}, le mock répond 200 avec le PointSet du carré (4 points) | Code 200, en-tête `Content-Type: application/octet-stream`, corps de 64 bytes décodable en 4 sommets et 2 triangles | Vérifie le comportement bout en bout : appel au PointSetManager, décodage, triangulation, encodage |
| Identifiant mal formé | GET /triangulation/pas-un-uuid | Code 400, JSON d'erreur, et le mock du PointSetManager n'est jamais appelé | L'identifiant doit être validé avant tout appel réseau, pour ne pas charger inutilement le PointSetManager |
| PointSet inexistant | UUID valide, le mock répond 404 | Code 404, JSON d'erreur | Le Triangulator doit propager le 404 du PointSetManager et ne pas le transformer en 500 |
| PointSetManager indisponible | UUID valide, le mock répond 503 | Code 503, JSON d'erreur | La panne vient d'une dépendance, pas du Triangulator : le client doit savoir qu'il peut réessayer plus tard |
| PointSetManager injoignable | UUID valide, le mock lève une erreur de connexion (ou ne répond pas dans le délai imparti) | Code 503, JSON d'erreur, pas de trace d'exception renvoyée au client | Une coupure réseau ne doit pas faire planter le service ni exposer une erreur interne |
| Réponse du PointSetManager corrompue | UUID valide, le mock répond 200 avec un binaire incohérent (header annonçant 5 points pour 3 points présents) | Code 500, JSON d'erreur | La `ValueError` du décodage doit être attrapée et traduite en réponse HTTP propre |
| PointSet non triangulable | UUID valide, le mock répond 200 avec un PointSet de 2 points | Code 500, JSON d'erreur | La spécification prévoit le 500 quand la triangulation échoue, et la `ValueError` ne doit pas remonter telle quelle |
| PointSet vide | UUID valide, le mock répond 200 avec un PointSet de 0 point | Code 500, JSON d'erreur | Même raison, et cohérent avec le choix fait dans les tests unitaires de triangulation |
| Méthode non autorisée | POST /triangulation/{UUID valide} | Code 405 | Seul le GET est décrit dans la spécification |

Cas ajoutés : réponse 500 du PointSetManager, identifiant vide dans l'URL et route inconnue.

## Tests de performance

La triangulation et les conversions binaires sont les opérations les plus coûteuses du service, et leur
coût dépend directement du nombre de points. Ces tests servent donc à deux choses : vérifier que les
temps restent acceptables sur des volumes réalistes, et observer comment ils évoluent quand le volume
augmente.

Ils sont marqués avec `@pytest.mark.perf` et déclarés dans la configuration de pytest. On peut donc les
exclure du reste des tests avec `pytest -m "not perf"` (cible `make unit_test`) ou les lancer seuls avec
`pytest -m perf` (cible `make perf_test`).

Les mesures sont faites avec `time.perf_counter`. Chaque mesure est répétée plusieurs fois et on retient
la médiane, pour limiter l'effet des variations de la machine. Les seuils sont volontairement larges,
car un test de performance qui échoue au hasard finit par être ignoré.

| Cas | Entrée | Attendu | Pourquoi |
|-----|--------|---------|----------|
| Décodage binaire | PointSets de 1 000, 10 000 et 100 000 points | Temps mesuré pour chaque taille, moins d'une seconde pour 100 000 points | Le décodage est fait à chaque requête, il ne doit pas devenir le goulot d'étranglement |
| Encodage des triangles | Triangulations de 1 000, 10 000 et 100 000 points | Temps mesuré pour chaque taille, moins d'une seconde pour 100 000 points | Même raison que le décodage, dans l'autre sens |
| Aller-retour des conversions | PointSet de 10 000 points encodé puis décodé | Temps mesuré, et les points obtenus sont identiques aux points de départ | Vérifie que l'optimisation éventuelle des conversions ne casse pas leur justesse |
| Triangulation | 100, 1 000 et 10 000 points aléatoires | Temps mesuré pour chaque taille, moins de dix secondes pour 10 000 points | C'est l'opération la plus coûteuse, et celle dont le coût risque le plus d'exploser |
| Évolution du temps de triangulation | Points aléatoires, en doublant le nombre de points à chaque étape | Le temps ne doit pas être multiplié par plus de quatre quand le nombre de points double | Détecte un algorithme dont le coût augmente trop vite, ce qu'un seul seuil fixe ne verrait pas |
| Requête complète | GET /triangulation avec un mock renvoyant 10 000 points | Temps de réponse mesuré, moins de dix secondes | Mesure ce que vit réellement le client, conversions et triangulation comprises |

Cas ajoutés : consommation mémoire sur un gros PointSet et comparaison des points très regroupés
avec des points bien répartis.

## Qualité

### Couverture

La couverture est mesurée avec `coverage`, configuré dans `pyproject.toml` pour ne regarder que le
package `triangulator` et pour afficher les lignes non couvertes. L'objectif est que tout le code du
composant soit couvert, et surtout qu'une ligne non couverte soit une question à se poser : soit il
manque un test, soit le code ne sert à rien.

La couverture seule ne suffit pas à prouver que les tests sont bons. Au moment du rendu intermédiaire,
elle est déjà à 100 % alors qu'aucune fonction n'est implémentée : les fonctions lèvent
`NotImplementedError`, cette ligne est exécutée, donc elle est comptée comme couverte. Cela montre bien
qu'un chiffre élevé ne dit rien de la pertinence des tests.

Pour éviter de me rassurer à tort, les tests vérifient des valeurs précises plutôt que l'absence
d'erreur, et le fichier `conftest.py` relit le binaire avec son propre code plutôt qu'avec les
fonctions testées. Sans cela, une même erreur à l'encodage et au décodage s'annulerait et le test
passerait quand même.

### Qualité du code

`ruff check` doit passer sans aucune remarque, avec les règles fournies dans `pyproject.toml`. Aucune
règle n'a été retirée. La règle `D` impose d'écrire une docstring pour chaque module, classe et
fonction, y compris dans les tests.

### Documentation

La documentation HTML est générée avec `pdoc3` à partir des docstrings, dans le dossier `docs/`. Lint
et documentation sont donc liés : si `ruff` ne signale rien, c'est que tout est documenté et que la
documentation générée est complète. Le dossier `docs/` est ignoré par git, car il est régénérable et
n'a pas à être versionné.

### Commandes

| Cible | Ce qu'elle lance |
|-------|------------------|
| `make test` | tous les tests, performance comprise |
| `make unit_test` | tous les tests sauf la performance (`-m "not perf"`) |
| `make perf_test` | uniquement les tests de performance (`-m perf`) |
| `make coverage` | les tests hors performance, puis le rapport de couverture |
| `make lint` | `ruff check` sur tout le projet |
| `make doc` | la documentation HTML dans `docs/` |

Le marqueur `perf` est déclaré dans `pyproject.toml`, ce qui permet de séparer les tests de
performance du reste sans avoir à les ranger dans un dossier à part.
