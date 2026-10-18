## OpenVisio v27.5 — Cadrage et indicateurs SAN

- Cadrage automatique des groupes de conflits avec zoom borné entre 50 et 150 %.
- Recalcul de la géométrie après changement de zoom avant recentrage.
- Indicateur de conflits Fabric A/B potentiels et actifs par groupe.
- Navigation et aperçu sans mutation du document.
- Windows prioritaire ; captures réelles nouvelles non réalisées.
- Auteur : Abdelhalim Talbi.

## OpenVisio v27.4 — Navigation graphique des groupes de conflits SAN

Navigation précédent/suivant et localisation du groupe dans le canevas par géométrie SVG réelle. Aperçu avant/après non destructif. Auteur : Abdelhalim Talbi.

## OpenVisio v27.3 — Comparaison avant/après des conflits SAN

Aperçu graphique non destructif : routes actuelles en rose, propositions en vert pointillé, gain estimé par groupe sur la sélection courante. Aucune application automatique ; Ctrl+Z reste disponible après validation. Auteur : Abdelhalim Talbi.

## OpenVisio v27.2 — Surlignage et actions de groupe SAN

Dans le diagnostic de câblage SAN, chaque groupe de conflits dispose de trois actions : **Surligner ce groupe** (aperçu rose des tracés existants sans modification), **Sélectionner les liens du groupe**, **Désélectionner ce groupe**. Le statut de conflits actifs est recalculé après chaque action. Les corrections ne sont jamais appliquées sans validation explicite. Auteur : Abdelhalim Talbi.

# OpenVisio v27.0 — Optimisation SAN par composants
Auteur : Abdelhalim Talbi.

- Décomposition du graphe des conflits en composants indépendants.
- Résolution exacte par composant jusqu’à 18 propositions, même pour des lots globaux plus grands.
- Stratégie heuristique déterministe réservée aux composants de plus de 18 propositions.
- Rejet des identifiants dupliqués, des scores non finis et des conflits mal formés.
- Présentation dans l’interface du nombre de groupes exacts et heuristiques.
- Aucun commit automatique : validation humaine et contrôles de topologie existants conservés.
- Les snapshots préexistants sont historiques ; aucune nouvelle capture réelle Windows n’est revendiquée.

## OpenVisio v26.8 — qualification différentielle SAN

240 topologies pseudo-aléatoires reproductibles (graines 1 à 240), parité géométrique stricte avec le moteur de référence v26.5, reproductibilité, absence de mutation, croisements et chevauchements. Les tests Node.js ne remplacent pas la recette Windows. Auteur : Abdelhalim Talbi.

## OpenVisio v26.6 — Optimisation conservatrice du routage SAN

Indexation des obstacles par lignes et colonnes de grille. Conservation de la recherche et de ses résultats, tests de parité avec le moteur v26.5. Auteur : Abdelhalim Talbi.

## V26.5 — topologies SAN multi-obstacles

Fixture déterministe à trois obstacles, tests de protection Fabric A/B, vérification de cohérence avant commit et benchmark Node.js (30 itérations). La recette graphique Windows et les nouvelles captures réelles ne sont pas disponibles dans cet environnement. Auteur : Abdelhalim Talbi.

## OpenVisio v26.3 — Qualification A* sur navigateur réel

Scénario Playwright : contrôle de l’aperçu rouge/vert, application explicite lorsque proposée, vérification du SVG après modification, Ctrl+Z/Ctrl+Y, sauvegarde et rechargement. Si aucun trajet admissible n’existe, la recette le signale sans prétendre avoir testé l’application A*. Les captures ne sont produites que lors d’une exécution graphique réussie. Auteur : Abdelhalim Talbi.

## OpenVisio v26.2 — recette graphique SAN (16 octobre 2026)

Ajout du scénario `tests/browser-san-e2e-v262.py` et de la commande `npm run test:browser-san-e2e` : véritable navigateur Chromium, insertion d'équipements, connecteur, audit de câblage, raccourcis Ctrl+Z/Ctrl+Y, export JSON signé, import et rechargement. Captures uniquement après réussite ; la recette est exécutée sur Linux ici et doit être répétée sur Windows. Cette recette ne prouve pas encore l'application graphique d'une alternative A* ; le scénario dédié reste à développer. Auteur : Abdelhalim Talbi.

## OpenVisio v26.1 — qualification transactionnelle SAN

Validation sur copie : application, vérification géométrique, persistance JSON, annulation et rétablissement. Aucun changement effectif avant succès du précontrôle. Auteur : Abdelhalim Talbi.

Captures : historiques uniquement ; aucune nouvelle capture Windows réelle.

## v26.0 — Vérification géométrique après application

Validation sur copie avant modification de l’état, comparaison des collisions, longueurs et proximité Fabric A/B. Refus de toute régression détectée. Annulation Ctrl+Z conservée. Qualification graphique Windows non réalisée ; captures historiques uniquement.

## OpenVisio v26.0 — Itinéraires alternatifs SAN

Recherche A* bornée de tracés orthogonaux alternatifs, contrôle des obstacles et des proximités Fabric A/B, prévisualisation rouge/vert en lecture seule. Aucune application automatique ; la transformation des résultats en points de passage éditables sera qualifiée ultérieurement. L’analyse est limitée aux 12 premières connexions dans le rapport. Captures historiques uniquement ; qualification graphique Windows non effectuée. Auteur : Abdelhalim Talbi.

## OpenVisio v25.5 — Espacement des Fabrics SAN

Le contrôle groupé impose désormais un espacement géométrique de 8 unités SVG entre les propositions de routage Fabric A/B. La validation reste humaine et transactionnelle. La séparation visuelle ne démontre pas une indépendance physique. Auteur : Abdelhalim Talbi.

# OpenVisio v25.3 — Protection Fabric A/B des corrections groupées

Auteur : Abdelhalim Talbi.

La préparation d'un lot signale désormais explicitement les interférences géométriques entre connexions des Fabrics A et B, et la validation transactionnelle existante interdit l'application simultanée de propositions en conflit. Cette protection concerne le routage graphique, **pas** une validation physique de l'indépendance des fabrics.

## v25.2
Exécuter `npm test` puis la recette graphique Windows. Captures historiques conservées ; aucune nouvelle capture Windows certifiée.

# OpenVisio v25.1 — Validation transactionnelle des corrections SAN

Auteur : Abdelhalim Talbi. La correction d’un décalage de route reste **sur validation humaine** et annulable (Ctrl+Z). Le système refuse désormais un aperçu si les extrémités, un obstacle, les ports, les waypoints ou le décalage de la connexion ont changé depuis sa préparation. En cas d’invalidation, recalculer l’aperçu. Aucune correction automatique globale n’est activée.

La recette graphique Windows et les captures réelles de cette version ne sont pas réalisées dans cet environnement ; les snapshots présents sont historiques.

## OpenVisio v24.9 — Audit géométrique SAN

Ajout du module `src/san-geometry-audit.js` : contrôle déterministe des points d’ancrage, orthogonalité et collisions avec équipements tiers. Les erreurs sont rapportées sans modification des diagrammes. Tests dédiés dans `tests/v249.test.mjs`. Ce module est une API de contrôle et n’est pas encore raccordé à une commande de l’interface graphique. Auteur : Abdelhalim Talbi.

# OpenVisio v24.7 — recette sur éditeur natif

- Recette Playwright de l'éditeur réel : insertion serveur/stockage, glisser-déposer du SVG, création d'une connexion via l'outil Connecteur, contrôle de la géométrie des tracés.
- Le scénario de surface de test indépendante reste conservé pour diagnostic, mais est désormais complété par un test du véritable éditeur.
- La recette Chromium sous Windows doit être exécutée sur une machine Windows équipée de Playwright. Aucune nouvelle capture Windows n'a été produite ici.
- Auteur : Abdelhalim Talbi.

## OpenVisio v24.6 — gestes Playwright et comparaison SAN

Le banc `tests/browser-san-performance.py` ajoute des événements réels `pointerdown/pointermove/pointerup`, roulette et touche Échap sur une surface de qualification indépendante. La capture est créée uniquement après succès. Correction de la comparaison de référence : champs `samples` au lieu de `results`. **Limite :** ces gestes valident le moteur d’automatisation navigateur, pas encore les outils natifs de l’éditeur. Recette Windows non exécutée ici. Auteur : Abdelhalim Talbi.


## OpenVisio v24.5 — qualification interactive SAN
Banc Chromium : zoom (0,5x à 2x), sélection, déplacement simultané de quatre équipements, validation des chemins SVG (absence de NaN/Infinity). Rapport JSON et capture réelle seulement si Chromium réussit. Les scénarios testent le rendu programmatique, pas les gestes souris natifs. Exécuter `windows/Run-Graphic-Qualification.ps1` sous Windows. Auteur : Abdelhalim Talbi.
# OpenVisio v24.4 — Recette Windows automatisée

Exécuter sous Windows : `powershell -ExecutionPolicy Bypass -File windows/Run-Graphic-Qualification.ps1`. Pré-requis : Python, `pip install playwright`, `python -m playwright install chromium`. Résultats : `qualification-windows/browser-report.json`, `comparison.json`, capture réelle `openvisio-ui-real.png` seulement en cas de réussite. Option `-Baseline ancien-rapport.json` pour comparer. Auteur : Abdelhalim Talbi.

## OpenVisio v24.3 — recette graphique SAN

Banc Chromium headless : `npm run benchmark:browser-san`. Scénarios de rendu initial, réutilisation et déplacement de nœud sur 16, 64 et 160 connexions. Résultats JSON et captures réelles uniquement si le navigateur démarre. Ne constitue pas une qualification Windows. Auteur : Abdelhalim Talbi.

## OpenVisio v24.2 — Diagnostic de rendu SAN

Le panneau Diagnostic rendu affiche désormais le taux de mutation DOM, le mode de routage et le temps moyen des rendus complets. Le bouton « Exporter JSON » télécharge localement les métriques sans transmettre les diagrammes. Les temps mesurent le JavaScript, pas le temps de peinture ni les FPS. Les captures incluses restent historiques, aucune capture native Windows nouvelle n’a été réalisée. Auteur : Abdelhalim Talbi.

## OpenVisio v24.1 — instrumentation DOM

Le rendu expose désormais `domMutations` dans les statistiques : éléments créés/remplacés, supprimés, réutilisés, et ratio de mutation. Ce ratio ne mesure ni le FPS ni le temps de peinture du navigateur. Les captures existantes sont historiques ; aucune nouvelle capture native Windows n’a été réalisée. Auteur : Abdelhalim Talbi.


## v23.8 — Contrôle différentiel SAN
- Comparateur de géométrie entre tracés locaux et globaux (tolérance 0,001).
- Vérification d'un recalcul local sur 16 : si divergence, utilisation du tracé global de référence.
- En dehors de l'échantillonnage, le garde de qualification v23.7 reste appliqué.
- Le contrôle périodique ne constitue pas une preuve d'équivalence sur chaque image ; prudence sur les topologies complexes.


## v23.5 — Qualification conservative du routage local SAN
- Nouvelle API `qualifyLocalRouteUpdate` pour détecter les situations où le recalcul local ne peut pas être garanti.
- Repli explicite vers recalcul global en cas de topologie modifiée, routes manquantes, changements simultanés ou dépendances de faisceau non qualifiées.
- Aucun routage local risqué n'est activé automatiquement dans l'interface.
- Auteur : Abdelhalim Talbi.


## v23.0 — Mesures de rendu par phase

- Le diagnostic interactif distingue le coût de génération du SVG et celui des surcouches du canevas (guides, sélection).
- Les mesures utilisent des fenêtres bornées, restent locales et sont réinitialisables ensemble.
- Le temps de peinture/composition du navigateur, les FPS et le rendu Windows natif ne sont pas mesurés.
- Aucun changement de géométrie ni de comportement de routage ; priorité à la qualification reproductible.
- Auteur : Abdelhalim Talbi. Les captures existantes sont historiques.


## v22.8 — Qualification topologies SAN denses

- Nouveau moteur de diagnostic par balayage spatial `analyzeDenseRouteBundles` avec limites explicites de segments, paires et résultats.
- Benchmark reproductible `npm run benchmark:dense` sur 100, 300 et 600 connexions (cas espacés, parallèles et denses).
- Aucun changement automatique de tracé ; les résultats incomplets sont signalés (`complete: false`).
- Les captures du dossier snapshots sont historiques, pas des captures Windows v22.8.

## v22.5 — Aperçu de correction SAN

Dans le panneau Câblage SAN, cliquer sur « Aperçu correction » pour une anomalie géométrique. Le calcul compare chevauchements, croisements et collisions ; aucun changement n’est appliqué avant confirmation. « Appliquer (annulable) » crée un point d’annulation Ctrl+Z. Les routes manuelles et les modes non orthogonaux sont protégés. Les captures précédentes sont historiques ; la recette native Windows reste à effectuer. Auteur : Abdelhalim Talbi.

## OpenVisio v22.4 — Localisation des anomalies géométriques

Liste des croisements, superpositions et tracés invalides avec bouton « Localiser » dans le panneau SAN. Diagnostic borné et non destructif. Auteur : Abdelhalim Talbi.


## v22.0 — Faisceaux SAN et voies parallèles
- Attribution déterministe des voies des connexions parallèles (tri par identifiant).
- API `planParallelLanes` pour les futurs routages multi-faisceaux ; déduplication et limitation configurables.
- Répartition des segments partagés indépendante de l’ordre des arêtes.
- Six tests de régression supplémentaires.
- Les captures existantes sont historiques ; aucune nouvelle capture réelle Windows revendiquée.

## OpenVisio v21.9 — Routage et superpositions

Le moteur de routage mesure désormais la longueur de segments orthogonaux partagés entre connexions et pénalise ces superpositions dans le choix des décalages et dans l’optimisation globale des petits diagrammes. Les chemins manuels restent prioritaires et inchangés. Les grands diagrammes conservent la stratégie rapide existante. Auteur : Abdelhalim Talbi.

## OpenVisio v21.8 — Espacement intelligent (Abdelhalim Talbi)

Nouvelles commandes **Auto ↔** et **Auto ↕** dans « Aligner et répartir » : distribution des formes sélectionnées sans chevauchement, avec un espacement minimal de 24 unités et prise en compte de la grille. Les formes verrouillées sont exclues des modifications par le contrôleur. Les positions peuvent dépasser l’emprise initiale pour préserver la lisibilité.

## OpenVisio v21.7 — Inspecteur multi-sélection

L’inspecteur affiche les types, l’emprise du groupe, le nombre de formes modifiables et distingue les valeurs différentes. Les opérations de masse ne touchent plus les formes verrouillées. Les calques mixtes sont signalés explicitement. Auteur : Abdelhalim Talbi.

## OpenVisio v21.5 — Ergonomie de l’atelier vectoriel

- Bouton « ⛶ Canevas seul » : masque ou restaure bibliothèque et inspecteur sans modifier le diagramme.
- Raccourci `Ctrl+Maj+F` pour basculer l’affichage.
- Le canevas récupère réellement la largeur des panneaux masqués, y compris lorsque seul l’un des deux est fermé.
- État ARIA synchronisé pour les contrôles de panneaux ; ruban et actions rapides défilants sur écrans étroits.
- La compatibilité du format vectoriel et les fonctions SAN existantes sont conservées.
- Auteur : Abdelhalim Talbi.


## v21.4 — Recette navigateur renforcée (Abdelhalim Talbi)
- Serveur de recette démarré avec le Python courant (`sys.executable`) : compatible Windows et environnements virtuels.
- Vérification du format de sauvegarde SHA-256 v2 et de son empreinte hexadécimale.
- Test d'import d'un fichier altéré : aucune modification du diagramme.
- Vérification de l'ouverture du diagnostic de sauvegarde avant et après récupération.
- Erreur `ERR_BLOCKED_BY_ADMINISTRATOR` distinguée d'un défaut applicatif (`ENVIRONMENT_BLOCKED`).
- Recette Chromium non validée ici : blocage administrateur sur l'URL localhost ; aucune nouvelle capture réelle.

## v21.2 — Recette navigateur reproductible

Ajout de `tests/browser-recovery.py` : scénario Chromium réel d’ajout de forme, export SHA-256, import confirmé, rechargement, corruption simulée et restauration depuis la copie de secours. Exécution : `pip install playwright` puis `python tests/browser-recovery.py --chromium /chemin/vers/chromium --screenshot snapshots/recette-v211-reelle.png`. Les tests navigateur sont distincts des tests Node. Une capture ne doit être étiquetée réelle qu’après exécution réussie.

# OpenVisio v21.0 — reprise des écritures interrompues

Correction de la gestion des sauvegardes en cas d’échec de remplacement du document principal. Le secours précédent est restauré si le document principal n’a pas changé ; si le principal a été écrit avant l’erreur, la nouvelle copie de secours est conservée. 893 tests Node réussis. Recette Windows graphique et nouvelles captures non réalisées. Auteur : Abdelhalim Talbi.


## OpenVisio v20.8
Tester l’export et la restauration JSON depuis le navigateur Windows. La qualification graphique reste à effectuer.

## OpenVisio v20.6 — Persistance unifiée

Le diagramme, le zoning et le dernier import SAN sont désormais sauvegardés dans une unique entrée localStorage (`openvisio-document-v206`), avec validation avant restauration. Les anciennes clés restent lisibles pour migration ; la conservation d’une sauvegarde JSON exportée est recommandée. Le stockage local navigateur n’est pas un système de sauvegarde durable.

## OpenVisio v20.5 — transactions zoning et imports SAN

Validation du zoning avant écriture et historique, absence de point de restauration pour une valeur identique ; import SAN enregistré dans l’historique avant remplacement. Auteur : Abdelhalim Talbi.

## Version 19.9 — renommage contrôlé des ports SAN

Dans l’inspecteur d’un équipement, sélectionner « Renommer un port et réaffecter ses connexions… ». Saisir le nom existant puis le nouveau nom. La prévisualisation indique les connexions impactées ; confirmer pour appliquer en une seule action Annuler/Rétablir. Le nom ne peut pas entrer en collision avec un port existant. Les champs SAN et les points de passage sont préservés. Aucune connexion n’est supprimée.

## Version 19.8 — Protection des ports SAN

Lorsqu’un port utilisé est retiré du catalogue d’un équipement, la modification est refusée et les connexions concernées sont présentées. Réaffecter les ports des câbles avant de supprimer le port. La suppression des ports libres reste autorisée. La validation intervient avant la création d’une entrée d’historique. Aucune connexion n’est supprimée automatiquement.

## OpenVisio v19.6 — déplacements multiples cohérents

Le déplacement groupé conserve les écarts entre formes, y compris près des limites x=0 et y=0. L’alignement sur grille applique un delta commun. Auteur : Abdelhalim Talbi.

## Nouveautés v19.4 — Historique bidirectionnel

Annuler (Ctrl+Z) et Rétablir (Ctrl+Y ou Ctrl+Maj+Z) les opérations d’édition. Une nouvelle modification après annulation efface la branche de rétablissement. Historique limité à 60 états dans chaque direction. Les actions de navigation et de zoom ne sont pas historisées.

## v19.3 — Performance grands diagrammes

Optimisation du diagnostic des croisements par balayage spatial horizontal, avec filtrage vertical et ordre de résultats stable. Le contrôle ne modifie jamais les connexions. Les points de passage restent conservés. Auteur : Abdelhalim Talbi.

## OpenVisio v19.0 — Analyse des segments de connexion

Le diagnostic de croisements compare désormais les segments des routes orthogonales et des trajets à points de passage, et non les droites entre centres. Les extrémités partagées sont ignorées. Le calcul reste non destructif. Limite : les optimisations finales du moteur SVG (fan-out et décalages de parallèles) ne sont pas réinjectées dans ce diagnostic ; le résultat est une approximation du rendu final.

Auteur : Abdelhalim Talbi.

## Vérification v18.7 sous Windows
Créer deux équipements et une connexion présentant une anomalie ; ouvrir le diagnostic et activer « Voir la connexion ». Vérifier la fermeture du panneau, la sélection du lien, son contour rouge et le focus clavier. Capturer une image réelle uniquement après vérification.

## v18.6 — Vérification Windows
Ouvrir le panneau de câblage, tester chaque filtre, vérifier la lecture des messages et l’absence de modification du graphe.

## OpenVisio v18.4 — navigation clavier des menus

Les menus d’outils acceptent les flèches Haut/Bas (navigation cyclique), Début/Fin, Échap (fermeture et retour au déclencheur). Une commande activée referme le menu et rend le focus au résumé. Cette livraison ne constitue pas une qualification interactive Windows. Auteur : Abdelhalim Talbi.

## v18.3 — Menus accessibles et fermeture contrôlée

- Un seul menu du ruban peut rester ouvert.
- Fermeture par clic extérieur, touche Échap et activation d'une commande.
- Retour du focus au résumé du menu lors de la fermeture clavier.
- Correction CSS : le panneau fermé reste masqué ; menu Superposition accessible sur écrans étroits.
- Six tests nouveaux ; aucun retrait de commande.
- Auteur : Abdelhalim Talbi.

## OpenVisio v18.2 — Ruban progressif

Les commandes du canevas sont regroupées dans quatre menus : Aligner et répartir, Transformer, Repères et grille, Superposition. Ouvrir un menu avec un clic ou le clavier (Entrée/Espace) ; les commandes historiques et leurs identifiants sont conservés. Les menus sont des éléments HTML natifs `details/summary`. Les captures anciennes restent historiques et ne constituent pas une capture réelle v18.2. Auteur : Abdelhalim Talbi.

## v18.1 — Lancement Windows
Double-cliquer OpenVisio-Windows.cmd. Le lanceur PowerShell utilise uniquement 127.0.0.1, ouvre le navigateur par défaut et ne nécessite pas Python. Build-Windows-EXE.cmd requiert le SDK .NET 8 ; l’EXE n’est pas fourni précompilé.

## v17.8 — Mesures des interactions et correction du rafraîchissement

- Correction d'une boucle de programmation des frames : la callback v17.7 replanifiait une frame sans dessiner.
- Déplacement des formes désormais planifié via requestAnimationFrame, plutôt qu'un rendu synchrone à chaque événement pointermove.
- Ajout d'un collecteur de métriques glissantes (moyenne, p50, p95, dépassements 16,67 ms), sans export ni stockage.
- Les mesures sont internes : aucun panneau de performance ni qualification navigateur Windows n'est encore disponible.
- Auteur : Abdelhalim Talbi.

## v17.7 — Rafraîchissement interactif par frame

Pendant le déplacement, le redimensionnement et l’édition de points de passage, les rafraîchissements sont regroupés via requestAnimationFrame. Le relâchement du pointeur déclenche un rendu final complet. Cela réduit les rendus redondants mais ne garantit pas un gain de latence mesuré en navigateur.

## v17.6 — Index spatial des routes
Index en grille des enveloppes de routes, recherche de candidats locale, invalidation conservative des routes inconnues. L’index est réutilisé pour une même Map de routes ; si celle-ci est mutée en place, créer une nouvelle Map pour reconstruire l’index. Auteur : Abdelhalim Talbi.

## OpenVisio v17.2 — analyse spatiale des connexions

Nouveau module `src/spatial-routing.js` : identification conservative des liaisons affectées par le déplacement de formes et par les obstacles traversant les anciens chemins. L’analyse ne remplace pas encore le pipeline de recalcul global du rendu SVG ; l’intégration et la validation graphique sont prévues pour la prochaine itération.

## v16.4
Les connexions orthogonales sont réorganisées au rendu. Aucune installation supplémentaire requise.

## OpenVisio v16.2 — Faisceaux multisegments

Séparation automatique des chemins orthogonaux identiques comportant plusieurs segments. Conservation des extrémités, respect des points de passage manuels, refus des décalages traversant des obstacles. Les formes ne sont pas déplacées. Limite : les faisceaux partiellement communs ne sont pas encore fusionnés.

Auteur : Abdelhalim Talbi.

## OpenVisio v15.7 — Repères personnalisables

Repères verticaux et horizontaux ajoutables depuis la barre du diagramme ; déplacement à la souris, suppression globale et accrochage des bords/centres des formes (tolérance 7 unités). Les repères sont des aides de travail temporaires non enregistrées dans le document. Auteur : Abdelhalim Talbi.

## v15.5 — Guides visibles et dimensionnement uniforme

Guides magnétiques SVG temporaires lors du déplacement d’une forme, affichés en pointillés roses. Commandes Même largeur, Même hauteur, Même taille pour plusieurs formes, référence = sélection principale. Calques verrouillés exclus. Annulation via historique. La validation graphique réelle sur Windows reste à effectuer. Auteur : Abdelhalim Talbi.

# OpenVisio v15.1 — Dessin vectoriel et diagrammes généralistes

OpenVisio reste avant tout un éditeur de dessin vectoriel SVG, de diagrammes fonctionnels, de schémas et d’organigrammes. Les audits SAN sont des fonctions complémentaires et facultatives.

Cette version ajoute 16 types de formes éditables et 3 modèles : diagramme de flux, organigramme, cartographie applicative. Les formes utilisent le moteur SVG existant (sélection, déplacement, connexion, export SVG, sauvegarde JSON).

Windows est prioritaire. Les aperçus historiques du dossier snapshots ne sont pas des captures réelles de v15.1.

Auteur : Abdelhalim Talbi.

## v14.8 — Scénarios de pannes SAN multiples

Sélection multiple (Ctrl+clic) des switches, liens ou Fabrics dans Comparer topologies, puis « Simuler toutes les sélections ». Comparaison non destructive des chemins survivants, applications impactées et export CSV/HTML. L’analyse reste documentaire ; pas de découverte réelle. Auteur : Abdelhalim Talbi.

# OpenVisio v14.7 — Simulation de panne SAN

Sélectionner **Comparer topologies**, charger le diagramme cible, choisir une Fabric, un équipement ou une connexion, puis **Simuler la panne**. Exporter le résultat en CSV ou HTML. Simulation non destructive et documentaire, sans lecture ni action sur les équipements.

Auteur : Abdelhalim Talbi.

## OpenVisio v14.6 — Validation SAN de bout en bout

La fenêtre « Comparer topologies » propose une validation consolidée du diagramme cible : zoning, masking, WWPN, LUN, chemins et redondance Fabric A/B. Export CSV et rapport HTML. Contrôles documentaires seulement ; aucune interrogation matérielle. Auteur : Abdelhalim Talbi.

## v14.5
L’enveloppe Windows n’a pas changé. L’éditeur du masking est accessible dans le panneau des propriétés du stockage. Compilation EXE Windows non qualifiée dans cet environnement.

# OpenVisio v14.3 — Corrélation zoning / connexions

Corrélation des zones importées avec les WWPN et connexions du diagramme cible, dans « Comparer topologies ». Détection des membres absents, zones inconnues, zones hors zoneset et absence d’activation déclarée. Exports CSV/HTML. Le fichier cible peut contenir `sanImport` ; sinon l’import SAN courant est utilisé. Aucune interrogation du switch réel.

Auteur : Abdelhalim Talbi.

## v14.2
Les nouvelles fonctions sont accessibles dans le même lanceur Windows. Aucune nouvelle dépendance Windows. Compilation EXE et recette Windows non exécutées dans cet environnement.

## v14.1 — Édition graphique des propriétés SAN

Sélectionner un serveur pour renseigner les HBA, les WWPN initiateurs (format hexadécimal à huit octets) et le multipathing dans le panneau de propriétés. Sélectionner un équipement de stockage pour renseigner les LUN. Les listes sont séparées par point-virgule, validées et enregistrées dans le diagramme JSON. Ces valeurs sont déclaratives, sans découverte automatique. Auteur : Abdelhalim Talbi.

# OpenVisio v13.9 — Matrice d’impact SAN

Comparaison de deux diagrammes JSON depuis **Comparer topologies**. La matrice relie les serveurs, Fabrics A/B, stockages et applications explicitement associées. Exports CSV et HTML. Les chemins sont déduits des liens dessinés : aucune vérification des HBA, MPIO, zoning actif ou disponibilité réelle.

Windows reste prioritaire, enveloppe inchangée. Les images dans snapshots/ sont des aperçus historiques, **pas des captures réelles de v13.9**. Auteur : Abdelhalim Talbi.

# OpenVisio v13.7 — Impact SAN

Auteur : Abdelhalim Talbi.

Comparaison des chemins SAN entre deux diagrammes : dans « Comparer topologies », charger les deux JSON, puis consulter « Impact des chemins SAN ». Le bouton « Exporter rapport impact SAN HTML » produit un rapport autonome. Les résultats sont déclaratifs, sans vérification sur switches. L’enveloppe Windows reste inchangée ; priorité aux fonctionnalités.

# OpenVisio v13.6 — Superposition des topologies

Auteur : Abdelhalim Talbi.

La boîte **Comparer topologies** affiche une superposition SVG non destructive des deux fichiers JSON. Les éléments ajoutés, supprimés, modifiés et inchangés sont colorés. Les objets de la version initiale sont en pointillés, ceux de la cible en traits pleins. Filtrer par statut, cliquer sur une ligne de différence pour cibler un identifiant, ou saisir manuellement cet identifiant. Le ciblage ne modifie pas le diagramme actif.

**Limites :** comparaison par ID stable, positions issues des fichiers, aucune vérification réseau live. Les trois images historiques du dossier snapshots ne sont pas des captures réelles de v13.6. Windows EXE non compilé dans cet environnement.

---

# Guide Windows — OpenVisio v11.0
Auteur : Abdelhalim Talbi

## Exécution immédiate
Extraire intégralement le ZIP. Double-cliquer sur `OpenVisio-Windows.cmd`. Le lanceur PowerShell héberge les ressources localement, sans Python. Ne pas exposer ce serveur sur Internet.

## Construire OpenVisio.exe
1. Installer le SDK officiel .NET 8 sur Windows 10/11 x64.
2. Ouvrir le dossier extrait et lancer `Build-Windows-EXE.cmd`.
3. Le script exécute `dotnet publish` pour `win-x64` en mode `--self-contained true`.
4. Le script vérifie `dist\windows-x64\OpenVisio.exe` et `wwwroot\index.html`.
5. La recette PowerShell démarre l’EXE avec `--no-browser`, attend l’URL loopback, vérifie `/`, `/src/main.js`, `/styles/app.css`, puis arrête le processus.
6. Si le test réussit, distribuer **tout le dossier** `dist\windows-x64`, pas uniquement le fichier EXE.

## En cas d’échec
Consulter la sortie de `Build-Windows-EXE.cmd` ; vérifier le SDK .NET 8, les permissions Windows et la disponibilité des ports locaux. Aucun résultat de compilation Windows n’est revendiqué par la présente livraison.


## v11.1 — Vérification renforcée de l'EXE
Lancer `Build-Windows-EXE.cmd` depuis un poste Windows avec SDK .NET 8. Le script appelle automatiquement `windows/Validate-OpenVisio-Windows.ps1` après compilation. Il contrôle l'accueil, les ressources JS/CSS, HEAD, le refus POST (405), une ressource absente (404) et les en-têtes de sécurité. Le succès des tests Node.js sur Linux ne remplace pas cette recette Windows.

## v11.7
Les diagnostics de câblage s'exécutent localement dans l'interface. Qualification native Windows à effectuer sur une machine Windows avec .NET 8 SDK.

## v11.8
Windows demeure prioritaire. Le lanceur `OpenVisio-Windows.cmd` ne nécessite pas Python. L'exécutable natif doit être compilé avec le SDK .NET sur un poste Windows. Aucun EXE précompilé n'est fourni.


## v11.9
Le panneau de câblage est intégré à l’inspecteur. La recette Windows native et la compilation EXE restent à réaliser sur un poste Windows avec SDK .NET 8.


## v12.0
Lancer `OpenVisio-Windows.cmd` depuis l'archive extraite. Le nouveau bouton **Câblage SAN / CSV** exporte des fichiers CSV lisibles dans Excel Windows. L'EXE autonome nécessite une compilation sur Windows avec .NET 8 ; aucun EXE précompilé n'est fourni.

## v12.1
Windows prioritaire : `OpenVisio-Windows.cmd` sans Python ; `Build-Windows-EXE.cmd` nécessite .NET SDK. EXE non compilé dans cet environnement. Pour exporter l’audit, ouvrez **Câblage SAN / CSV** puis **Exporter chemins SAN CSV**.

## v12.3
L’éditeur de zoning fonctionne en navigateur local. Les zones ne sont pas persistées dans le document. La compilation de l’EXE Windows reste à qualifier sur Windows.

## v12.4
Le zoning est enregistré dans les fichiers JSON du diagramme. La compilation native Windows et les captures réelles restent non qualifiées dans cet environnement.


### v12.5
Import local de fichiers `.txt`, `.cfg`, `.conf`, `.log` sans connexion au réseau SAN. Construction de l'EXE non vérifiée sous Windows.

## v12.6
Démarrage : `OpenVisio-Windows.cmd`. Compilation EXE facultative : `Build-Windows-EXE.cmd` avec SDK .NET 8. Qualification native Windows non réalisée dans cet environnement.


## v12.7 — Zonesets et VSAN
Importer un export texte Brocade ou Cisco MDS depuis le panneau SAN. L'interface indique le nombre de zonesets et d'activations déclarées. Le moteur identifie les commandes de définition et d'activation et les numéros VSAN Cisco, mais **ne confirme pas l'état effectif du switch**. La classification initiateur/cible reste manuelle. Les snapshots inclus sont historiques et statiques.


## v12.8 — Zonesets / VSAN
Importer une configuration SAN depuis **Câblage SAN / CSV** ; les zonesets importés enrichissent le rapport HTML avec leur VSAN, les zones référencées, et les écarts avec le diagramme. Les données de l’import ne sont pas persistées entre sessions. La commande d’activation n’atteste pas l’état réel du switch. Windows reste prioritaire ; compilation EXE non qualifiée dans cet environnement.

## v12.9
Les zonesets et VSAN sont inclus dans les fichiers JSON de diagramme. Le kit ne contient pas d’EXE précompilé ; les tests Windows natifs restent à réaliser. Les aperçus UI sont statiques historiques.


## OpenVisio v13.0 — Cockpit SAN
Après import de fichiers SAN, cliquez sur **Cockpit SAN** dans la barre supérieure. Consultez l’historique (30 imports maximum), les compteurs Fabric A/B et les anomalies de zonesets. Utilisez **Exporter les écarts CSV** pour récupérer un fichier ouvrable dans Excel. Les données restent dans le navigateur local ; elles ne reflètent pas nécessairement la configuration active des switches. Les aperçus PNG sont historiques, pas des captures de cette version.

## v13.1
Le cockpit SAN est accessible via le navigateur lancé par `OpenVisio-Windows.cmd`. L’EXE nécessite une compilation sur Windows avec .NET 8. Aucune validation Windows native n’a été réalisée dans cet environnement.


## v13.2
Le rapport HTML SAN est exporté localement et s’ouvre dans Edge ou Chrome sans serveur externe. La compilation de l’EXE Windows n’a pas été effectuée dans cet environnement.


## v13.3 — Cockpit SAN
Ouvrir Cockpit SAN. Utiliser les filtres Fabric et Criticité, choisir les versions 1 et 2, puis consulter les écarts et la courbe des scores. Les résultats sont indicatifs, calculés sur les imports locaux.


## OpenVisio v13.4
Dans Cockpit SAN, choisir Fabric, criticité et les deux versions puis cliquer **Exporter comparaison HTML**. Les lignes d’écarts sont colorées par criticité. Les comparaisons sont déclaratives.
Les snapshots du ZIP sont des aperçus statiques historiques, pas des captures de v13.4.


## v13.5 — Différences de topologie
La comparaison de topologies s’utilise dans le navigateur Windows via le bouton « Comparer topologies ». Le rapport HTML est autonome.

## v13.8
L’enveloppe Windows reste inchangée. Ouvrir **Comparer topologies** pour accéder aux nouveaux contrôles FC et applicatifs.

## v14.0
Fonctions de chaînes SAN disponibles dans l’interface existante, sans modification du lanceur Windows.

## v14.4
Aucun changement de l’enveloppe Windows. Utiliser Comparer topologies pour l’audit des accès SAN. L’exécutable natif n’a pas été compilé ni testé sur Windows dans cet environnement.


## v14.9 — Campagnes de résilience SAN
Dans **Comparer topologies**, chargez un diagramme cible, sélectionnez plusieurs équipements/liens/Fabrics (Ctrl+clic), puis cliquez **Lancer la campagne**. Chaque panne isolée et leur combinaison sont comparées dans un tableau classé par pertes, dégradations et applications affectées. Export CSV/HTML disponible. Simulation documentaire, non destructive. Les cumuls par équipement ne prouvent pas une causalité isolée.


## v15.0 — SPOF SAN
v15.0 : analyse SPOF dans la même interface Windows ; compilation EXE non qualifiée dans cet environnement.


## v15.2
La gestion de superposition est disponible dans l’éditeur graphique existant. Aucune compilation native Windows n’a été effectuée dans cet environnement.


## v15.3 — Connecteurs intelligents
Les nouvelles connexions sont créées en mode **smart** : choix automatique des côtés d'accrochage, recherche de trajets orthogonaux évitant les formes intermédiaires et pénalisation des croisements. Les connexions suivent les déplacements des formes lors du rendu. Dans les propriétés d'une connexion, le mode « Trajet » permet de choisir `smart`, `avoid`, `orthogonal` ou `straight`. Les points de passage manuels conservent la priorité. Cette évolution reste généraliste : organigrammes, processus, infrastructure, cloud et SAN. Auteur : Abdelhalim Talbi.

## v15.4
Les commandes d’alignement sont disponibles dans la barre du diagramme sous Windows.


## OpenVisio v15.6 — Règles et redimensionnement
- Graduations SVG horizontales et verticales activables dans le ruban « Règles ».
- Poignée de redimensionnement en bas à droite de la forme sélectionnée ; Maj conserve les proportions.
- Grille respectée si activée, dimensions minimales, annulation via Ctrl+Z.
- Fonctionnalités d’édition vectorielle généralistes ; auteur Abdelhalim Talbi.


## OpenVisio v15.8 — Repères persistants et verrouillables
Les repères horizontaux/verticaux sont sauvegardés dans le JSON du document et dans la sauvegarde locale. La liste déroulante permet de choisir un repère et de verrouiller/déverrouiller son déplacement. Les modifications sont intégrées à l'historique d'annulation. Un repère verrouillé reste utilisable pour l'accrochage. Les captures historiques ne constituent pas des captures réelles de la v15.8. Auteur : Abdelhalim Talbi.

## v15.9
Commandes de rotation et de symétrie accessibles dans la barre du diagramme. L’application reste livrée sous forme de sources et de lanceur Windows : aucun EXE Windows n’a été compilé ni testé dans cet environnement Linux.

## v16.0 — Connexions lisibles et rotations
- Les ports géométriques suivent la rotation et les symétries des formes.
- Réorganisation automatique des chemins : deux ordres de routage évalués, minimisation pondérée des croisements, longueurs et coudes.
- Les points de passage manuels restent prioritaires ; aucune forme n’est déplacée automatiquement.
- Routage recalculé après déplacement/rotation ; calcul limité à deux passes pour contenir la charge.
- Limites : routage orthogonal approximatif, pas de garantie d'absence de croisement ; ports physiques nommés et tracés peuvent encore demander des ajustements.

## v16.1
La séparation des liens parallèles fonctionne dans l’éditeur sous Windows sans option supplémentaire. L’exécutable Windows n’a pas été compilé dans cet environnement.

## v16.3
Les faisceaux de connexions sont traités directement dans le rendu SVG ; aucune installation supplémentaire n’est nécessaire.


## OpenVisio v16.5 — Répartition des ancrages
Les connexions automatiques qui partagent le même côté d'une forme sont réparties selon la position de leurs destinations, avec marge et espacement minimal. Les points manuels, interfaces physiques et ports explicites restent inchangés. Les formes tournées ne sont pas traitées par ce mécanisme. Les liens droits peuvent devenir obliques et l'optimisation n'est pas une garantie globale d'absence de collision. Auteur : Abdelhalim Talbi.


## OpenVisio v16.6 — sorties orthogonales en éventail
Les connexions à ancrage automatique réparti peuvent recevoir un court départ orthogonal. Le traitement préserve les ports explicites, interfaces physiques et tracés manuels ; il rejette les candidats non orthogonaux ou traversant un autre équipement. Une sortie est conservée sans modification si les contraintes ne permettent pas un résultat sûr. Auteur : Abdelhalim Talbi.

## v16.7 — Évitement local des croisements et budget de calcul
Les sorties orthogonales en éventail peuvent être ajustées localement pour réduire les croisements. Les points de connexion, chemins manuels et interfaces physiques restent inchangés. L’optimisation est désactivée au-delà de 160 liens pour maîtriser le coût de calcul. Cette étape n’est pas un routage global optimal.


## v16.8 — Performance du routage
Le calcul global des itinéraires est mémorisé par canevas et par signature géométrique complète (nœuds et connexions). Les sélections et autres rafraîchissements sans changement de géométrie réutilisent les chemins calculés. Toute modification de forme, de lien, de port ou de point de passage invalide le cache. Les éléments SVG restent synchronisés par signature individuelle. La mémoire conserve au plus un résultat de routage global par canevas.

## v16.9 — Mesures
Sous Node.js, exécuter `npm run benchmark:large` pour produire BENCHMARK-V16.9.json. Ces mesures ne remplacent pas une qualification graphique Windows.


## v17.0 — Routage adaptatif des grands diagrammes
Pour plus de 160 liens, le routage intelligent examine au maximum cinq couples de ports au lieu de seize, tout en conservant la recherche d’évitement d’obstacles. Les diagrammes plus petits conservent le routage complet. Le cache inclut le mode de calcul. Auteur : Abdelhalim Talbi.

## v17.1 — Invalidation géométrique sélective
Les changements de couleur, de libellé et de présentation n'entraînent plus le recalcul global du routage. Les changements de position, de taille, de ports, de rotation ou de points de passage continuent à invalider le cache. Un diagnostic pur `affectedGraphElements` identifie les formes et liens concernés. Le rendu SVG réutilise les groupes inchangés déjà existants. Il ne s'agit pas encore d'un recalcul local complet des chemins après déplacement d'une forme.


## v17.3 — Routage incrémental prudent
Le moteur réutilise les chemins inchangés pour les grands diagrammes (>160 liens) orthogonaux simples lorsque 12 liens au maximum (et 4 % du total) sont affectés. Les autres cas repassent au calcul global. Les captures historiques ne constituent pas des captures réelles v17.3. Auteur : Abdelhalim Talbi.


## v17.4
Le moteur de routage spatial est inclus dans la version web. Aucun exécutable Windows natif n’a été compilé dans cet environnement.


## OpenVisio v17.5 — Analyse spatiale précise
Les segments des connexions sont testés contre les zones modifiées, au lieu de se limiter à leur rectangle englobant. Benchmarks Node.js : BENCHMARK-V17.5.json. Les captures historiques ne constituent pas des captures réelles de la v17.5. Auteur : Abdelhalim Talbi.

## Diagnostic Windows v17.9
Ouvrez l’application, cliquez sur « Diagnostic rendu », déplacez plusieurs formes, puis notez P95 et les dépassements de 16,67 ms. Aucun exécutable Windows n’est inclus.

## Version 18.0 — Vérification Windows
Vérifiez que le titre et l'en-tête indiquent `v18.0`. Pour qualifier les interactions et produire des captures réelles, suivre `QUALIFICATION-V18.0.md`. Le script `Build-Windows-EXE.cmd` nécessite le SDK .NET 8 sur une machine Windows ; aucun exécutable Windows n'est fourni comme étant validé dans cette archive.


## Contrôle v18.5
Lancer `npm test` puis vérifier dans l’interface les ports déclarés, les câbles, les conflits et les Fabric A/B. Les tests automatiques ne remplacent pas la recette graphique Windows.

## v18.8 — Vérification manuelle Windows
Ouvrir un schéma avec plusieurs anomalies, vérifier le filtrage, les boutons précédent/suivant, le centrage et le focus sur le canevas. Capturer les écrans réels depuis Windows ; cette compilation n’a pas été effectuée ici.


## v18.9
v18.9 : diagnostic de croisements indicatif disponible dans le rapport de câblage. Tests automatisés sous Linux ; validation Windows interactive encore nécessaire.


## v19.1 — Diagnostic des chemins SVG affichés
Le rapport de câblage récupère les polylignes M/L du SVG réellement affiché et les utilise pour détecter les croisements. Si un chemin est absent ou utilise une commande non prise en charge, le diagnostic se replie sur le routage calculé. Aucune modification automatique des liens.

## v19.2 — Audit de robustesse des diagnostics SVG
- Analyse stricte des commandes SVG M/L : les caractères inconnus, les nombres mal formés et les commandes relatives sont rejetés sans interprétation partielle.
- Limites de taille pour protéger l'interface contre des tracés importés anormalement volumineux.
- Élimination rapide des paires de chemins dont les rectangles englobants ne se recoupent pas, avant comparaison des segments.
- Conservation du repli sur le routage du modèle si un tracé SVG ne peut pas être lu.
- Aucun changement des équipements ou connexions. Auteur : Abdelhalim Talbi.


## Version 19.7 — Inventaire des ports SAN
L’inventaire indexe les câbles par équipement et port pour accélérer les grands schémas. Les conflits de réutilisation de port sont conservés et les boucles sur un même port ne sont plus comptées deux fois.

### v20.0 — Recette recommandée
Après lancement de l'application, vérifier la modification des propriétés SAN, la saisie invalide, le maintien des câbles sur ports protégés et les raccourcis Annuler/Rétablir. Cette recette interactive Windows n'a pas été exécutée dans l'environnement de construction.


## OpenVisio v20.1
Validation transactionnelle des propriétés de connexion : décalages non numériques refusés, interfaces vérifiées, aucune mutation ni entrée d’historique pour les valeurs inchangées. Inspecteur multi-sélection : suppression des opérations identiques inutiles. Auteur : Abdelhalim Talbi.


## OpenVisio v20.2 — Historique intégré
Le moteur Annuler/Rétablir utilise désormais un module transactionnel réutilisable. Les tests d’intégration couvrent une modification de connexion, l’annulation, le rétablissement, l’invalidation de la pile redo, la limite de capacité et la restauration des ports. Auteur : Abdelhalim Talbi.

## v20.4 — Recette reproductible
Depuis PowerShell : `powershell -ExecutionPolicy Bypass -File .\QUALIFIER-WINDOWS.ps1`. Le script exécute les tests Node et crée `qualification-windows-v20.4.log`. L’interface graphique doit ensuite être contrôlée manuellement ; ne pas confondre cette procédure avec une recette réalisée.


## v20.4 — Historique SAN unifié
- Les checkpoints contiennent désormais les zones déclarées et le dernier import SAN.
- Annuler/Rétablir restaure les données SAN et le diagramme ; les instantanés anciens restent lisibles.
- Les données SAN sont validées avant toute restauration.
- Tests automatisés : 858/858 PASS.
- La recette interactive Windows et les nouvelles captures réelles ne sont pas disponibles dans cet environnement.


## v20.7 — Sauvegarde et récupération
Avant chaque remplacement du document unifié, OpenVisio vérifie le document précédent et l’enregistre en copie de secours avec empreinte de contrôle. En cas de document principal illisible, la restauration depuis une sauvegarde valide demande confirmation. Une sauvegarde corrompue n’est jamais restaurée automatiquement. La copie ne remplace pas une sauvegarde externe.


## OpenVisio v20.9 — SHA-256
Les sauvegardes portables v2 utilisent SHA-256 via Web Crypto (HTTPS ou localhost requis). Les sauvegardes v1 FNV-1a restent importables pour compatibilité, sans garantie cryptographique. Une restauration valide le document avant écriture. La qualification Windows graphique et EXE reste à réaliser. Auteur : Abdelhalim Talbi.

## Recette Windows v21.2
Installer `py -3 -m pip install playwright`, puis `py -3 -m playwright install chromium`. Double-cliquer sur `Recette-Windows.cmd`. Consulter `recette/rapport.json` ; la capture `recette/capture.png` n’est créée que si le scénario atteint la fin.


## OpenVisio v21.4 — diagnostic intégré

Le bouton « État sauvegardes » ouvre un panneau en lecture seule indiquant si le document principal et la copie de secours sont valides, absents ou corrompus. « Actualiser » relance le contrôle sans modifier les données. Pour une sauvegarde indépendante du navigateur, utilisez « Sauvegarde JSON ». Auteur : Abdelhalim Talbi.


### OpenVisio v21.6 — Productivité
Palette « Commandes » (Ctrl+Maj+P) : recherche des outils et actions de l'atelier, Entrée pour lancer le premier résultat. « Propriétés » (Ctrl+I) ouvre l'inspecteur et lui donne le focus. Les commandes désactivées ne sont pas exécutées. Auteur : Abdelhalim Talbi.


## v22.2 — Intégration des voies SAN
Le moteur `separateParallelRoutes` utilise désormais le planificateur déterministe `planParallelLanes` pour attribuer les voies indépendamment de l’ordre des connexions. Les chemins manuels et les obstacles sont conservés. Auteur : Abdelhalim Talbi.


## v22.3 — Panneau de qualité des tracés SAN
Le dialogue « Inventaire de câblage et matrice SAN A/B » affiche désormais les statistiques des tracés SVG : nombre de segments, trajets invalides, croisements et chevauchements. Les comparaisons coûteuses sont désactivées pour les très grands diagrammes. Diagnostic indicatif en lecture seule, sans correction automatique.

## OpenVisio v22.6 — Superposition avant/après SAN
Aperçu temporaire directement sur le canevas SVG : tracé existant rouge pointillé, proposition verte continue. Fermeture du panneau ou annulation supprime la superposition ; application explicite conservant Ctrl+Z. Aucun test graphique Windows natif réalisé pour cette version. Auteur : Abdelhalim Talbi.

## v22.7 — Optimisation du diagnostic SAN
Le calcul d'aperçu élimine les comparaisons entre chemins dont les boîtes englobantes sont disjointes, sans changer la politique de validation manuelle. Les connexions à points de passage restent protégées. Auteur : Abdelhalim Talbi.


## v22.9 — Diagnostic spatial intégré
Le panneau SAN utilise le diagnostic spatial pour les grands diagrammes (> 1500 segments). Les comptages de ces diagrammes indiquent les anomalies distinctes affichées et ne sont pas des totaux exhaustifs. Les limites de calcul sont signalées ; aucune modification automatique. Auteur : Abdelhalim Talbi.


## v23.1 — Cache de topologie pendant les gestes
Pendant un déplacement ou redimensionnement, les références des objets visibles sont conservées entre les frames. Les positions restent lues en direct. Le rendu complet invalide le cache, puis actualise les propriétés et la sauvegarde. Les captures du ZIP sont historiques et non des captures de cette version. Auteur : Abdelhalim Talbi.


## OpenVisio v23.2 — Réutilisation du DOM SVG
Le panneau « Diagnostic rendu » présente les nombres de nœuds et de connexions SVG conservés ou reconstruits pendant le dernier rendu. Les éléments inchangés sont préservés ; les modifications de géométrie, sélection ou apparence provoquent leur reconstruction. Ces compteurs permettent de distinguer le coût de calcul du coût des mutations DOM. Les captures présentes dans le ZIP sont historiques, pas une recette native Windows v23.2.


## V23.3 — Signatures SVG ciblées

- Les signatures de réutilisation des connexions sont désormais calculées à partir de la liaison, du tracé SVG effectif, de la sélection et des alertes ; elles ne sérialisent plus les objets CMDB complets des deux extrémités à chaque frame.
- Les signatures des équipements restent complètes pour garantir la mise à jour de leurs attributs et ports.
- Les modifications des chemins, des labels, des alertes et de la sélection continuent à invalider les éléments SVG concernés.
- Aucun gain de performance Windows n'est revendiqué sans recette graphique native.


## OpenVisio v23.5 — Cache de diagnostic SAN
Le moteur conserve les résultats de diagnostic des câbles par canevas lorsque les données de topologie n'ont pas changé. Les sélections et rafraîchissements visuels ne relancent pas le diagnostic. Toute mutation des nœuds, interfaces ou liaisons invalide automatiquement ce cache. L'optimisation est conservatrice : elle ne modifie ni le routage ni les commandes d'annulation.


## Version 23.6 — garde de routage local
La qualification des dépendances SAN est maintenant appelée par le pipeline de routage. En cas de doute (faisceaux partagés, itinéraire manquant, interfaces épinglées), le calcul global est conservé. Aucun gain de vitesse n’est revendiqué pour les scénarios refusés. Les captures de `snapshots/` sont historiques, pas des captures Windows v23.6.


### v23.7 — Dépendances locales SAN
Une connexion orthogonale isolée peut être recalculée localement si aucun autre câble ne partage ses extrémités et si aucun itinéraire tiers ne traverse les zones d'impact. Dans tous les autres cas, recalcul global conservateur. Les captures incluses sont historiques, non réalisées sur Windows pour cette version.

## Vérification des performances v24.0
Installer Node.js puis exécuter `npm test` et `npm run benchmark:differential` dans le dossier extrait. Comparer les résultats sur la même machine, à charge équivalente. Les snapshots fournis restent historiques.

### Recette graphique v24.0
Ouvrir un diagramme SAN dense, déplacer un équipement, vérifier les chemins, les alertes de câblage et la sélection. Comparer le temps de rendu dans les outils de développement du navigateur. Aucune capture Windows v24.0 n’a été produite dans cet environnement Linux.


## v24.8 — Recette native et régression visuelle
Le banc Playwright vérifie désormais la sélection native et le cycle Annuler/Rétablir après création d’une connexion SAN. Option `--visual-baseline` : comparaison pixel à pixel des captures Chromium réellement réalisées, avec `--visual-threshold` (ratio moyen normalisé, valeur par défaut 0,02). Dépendance optionnelle `Pillow` (`py -m pip install pillow`). Aucune capture n’est synthétisée. Le test Windows reste à exécuter sur un poste Windows. Auteur : Abdelhalim Talbi.


## Version 25.0 — Audit géométrique intégré
Le panneau **Inventaire de câblage** présente désormais l’audit des chemins SVG réellement affichés : ancrages, orthogonalité et collisions avec des équipements tiers. Chaque anomalie propose **Localiser**. Le contrôle est non destructif ; les corrections restent soumises à l’aperçu existant. Pour éviter les blocages, l’audit détaillé est limité à 250 liens et 500 équipements. Les captures historiques ne constituent pas une qualification Windows v25.0. Auteur : Abdelhalim Talbi.


### OpenVisio v25.4
La qualification graphique Windows du nouveau sélecteur reste à effectuer.


## OpenVisio v25.6 — Audit des Fabrics existantes
Audit en lecture seule des distances entre routes A/B effectivement affichées ; seuil 8 unités SVG, limites 250 liens et 30 anomalies affichées. Les routes absentes et les audits tronqués sont signalés. Aucune correction automatique. Auteur : Abdelhalim Talbi.


## v25.7 — Protection des routes SAN existantes
Les corrections groupées sont désormais filtrées contre **toutes les routes existantes de Fabric opposée** dans le périmètre analysé : une proposition créant une proximité sous 8 unités SVG, ou aggravant une proximité existante, est écartée avant prévisualisation. Les routes manquantes empêchent l'approbation automatique pour les Fabrics identifiées. Le moteur reste un optimiseur de décalage orthogonal, pas encore un calculateur général de chemins autour des obstacles. Qualification graphique Windows non effectuée ; snapshots historiques uniquement. Auteur : Abdelhalim Talbi.


Version 25.9 : validation explicite des itinéraires alternatifs, contrôle des ancres et de la topologie, application avec historique Ctrl+Z. Qualification graphique Windows non effectuée.


## v26.4 — scénario A* déterministe
- Fixture `fixtures/san-astar-wall-v264.json` : deux équipements, un obstacle, ports SAN explicites.
- Tests de proposition A* positive, absence de collision, préparation, commit, sérialisation/undo/redo et rejet d'une topologie périmée.
- La recette graphique Windows n'est pas déclarée réussie : les captures présentes sont historiques.
- Auteur : Abdelhalim Talbi.

## Qualification v26.7 sous Windows
Dans PowerShell : `npm test`, puis `npm run benchmark:routing-comparison`. Les mesures Node.js ne remplacent pas la recette graphique Playwright.

## Qualification v26.9
Depuis PowerShell : `npm test`. Les tests graphiques Windows restent à exécuter sur une machine équipée de Chromium/Playwright.


## OpenVisio v27.1 — Visualisation des conflits SAN
La fenêtre de diagnostic affiche les groupes de conflits, les paires de liens incompatibles et l'état de la sélection en temps réel. Les conflits actifs sont signalés avant validation. Les corrections restent soumises à validation humaine et peuvent être annulées via Ctrl+Z. Auteur : Abdelhalim Talbi.


## OpenVisio v27.6 — Indicateurs de conflits Fabric A/B
Calcul centralisé des gains de routage sur la sélection courante, comptage exact des conflits internes au groupe, distinction des conflits Fabric A/B et blocage visuel des sélections incompatibles. Aucun changement automatique des routes. Auteur : Abdelhalim Talbi.
