# IND-4 — Protocole expérimental

## Question et décision

Sur le même ensemble équilibré de sessions HDFS, ajouter au LLM des passages de documentation HDFS améliore-t-il l'exactitude par rapport (1) au classifieur supervisé et (2) au même LLM sans documentation ? Dans quels cas les diagnostics et leurs justifications échouent-ils ?

L'exactitude est la métrique principale. Rapporter d'abord le delta **RAG − classifieur** ; un intervalle apparié entièrement au-dessus de zéro soutient une amélioration, entièrement au-dessous soutient une dégradation, et un intervalle recouvrant zéro rend le résultat non concluant. Le delta **RAG − LLM sans recherche** mesure l'ablation de la recherche ; c'est une comparaison secondaire. Une meilleure traçabilité sans gain d'exactitude est un constat distinct, pas une victoire sur le classifieur.

## Données et découpage

- Source : Loghub HDFS_v1, dépôt Zenodo 8196385 (voir les références [1] et [2]). Un incident est une session associée à un `BlockId`, y compris les témoins normaux. Les labels natifs `Normal` et `Anomaly` sont la vérité terrain. Les données ne comprennent ni capteurs ni catégories de causes validées ; l'étude répond à la variante « diagnostic binaire à partir des journaux ».
- Avec la graine 4604, tirer par classe 50 blocs pour le test final et 50 autres pour l'aperçu (100 blocs uniques par lot). À partir des blocs restants, pour chaque graine 42, 123 et 2026, tirer 5 000 normaux et 1 000 anomalies pour l'entraînement, puis 1 000 normaux et 250 anomalies pour la validation. Les partitions d'évaluation restent identiques entre graines et entre méthodes ; les jeux de développement peuvent se chevaucher d'une graine à l'autre, jamais avec les deux lots réservés.
- Conserver l'ordre des lignes, exclure les lignes qui mentionnent plusieurs blocs distincts pour éviter de partager un même événement entre partitions, retirer le préfixe temporel et masquer identifiants de blocs, IPv4/ports et nombres. Garder les 12 premières et 12 dernières lignes au plus (240 caractères par ligne), avec indication explicite de troncature des sessions longues. Conserver et compter les sessions sans événement exploitable plutôt que de remplacer des cas après observation.
- Exécuter le test une fois avec la configuration figée ; les trois graines font partie de cette exécution. Aucun exemple d'évaluation ni label associé n'est envoyé au LLM. L'aperçu indépendant est réservé aux vérifications techniques et ne constitue pas un résultat principal.

## Méthodes et réglages

| Méthode | Réglages figés |
|---|---|
| Classifieur supervisé | TF-IDF sous-linéaire, unigrammes et bigrammes, vocabulaire ajusté sur entraînement seulement ; régression logistique à pondération équilibrée ; maximum 1 000 itérations. Choix de C parmi 0,1 / 1 / 10 selon le F1 Anomaly de validation, départage par le plus petit C. |
| LLM sans recherche | Qwen2.5 3B Instruct dans Ollama local ; température 0,2 ; contexte maximum 8 192, sortie maximum 350 jetons ; une génération par graine et par cas, sans réessai de réponse invalide. |
| LLM avec RAG | Même modèle, manifeste, réglages, messages, format de sortie et graines ; seule différence : jusqu'à trois notices techniques, classement TF-IDF par similarité cosinus positive. L'index est ajusté sur les notices Apache, sans incident ni étiquette. Les notices sont des reformulations sourcées, pas un index des cas. |

Le système produit un label, une justification, les identifiants des événements utilisés et ceux des notices citées. Il ne déclenche aucune action. Les journaux sont présentés comme des données, jamais comme des consignes ; le projet ne conclut pas à la résistance aux entrées malveillantes, qui n'est pas mesurée ici.

## Mesures automatiques

- Exactitude, rappel Normal, précision/rappel/F1 Anomaly, matrice de confusion et taux de réponses invalides. Une réponse invalide est incorrecte en exactitude et compte comme non-détection pour un cas Anomaly. Les effectifs normal/anormal sont publiés ; précision et F1 ne se transposent pas directement à la prévalence réelle.
- Moyenne et écart-type échantillonnal sur les trois graines. Pour chaque delta d'exactitude, moyenner les différences de justesse par incident à travers les graines puis rééchantillonner les incidents appariés 5 000 fois, avec stratification selon le label ; rapporter l'intervalle percentile à 95 %, conditionnel à ce jeu et ces graines. Les 300 prédictions d'une méthode ne sont pas 300 incidents indépendants.
- Latence murale de prédiction (p50/p95 par graine). Chauffer le LLM avant la mesure, alterner l'ordre des bras selon la position du cas, mesurer la recherche dans le bras RAG. Exclure entraînement, lecture, construction d'index et chargement initial. Déclarer le matériel réellement utilisé, le recours éventuel au GPU et les interruptions. Comptabiliser les jetons et le coût direct d'API (0 USD en local, hors matériel, temps et électricité).
- Traçabilité automatique : proportion de sorties avec au moins une citation et sans identifiant hors contexte ; proportion de sorties comportant une citation hors contexte ; proportion de sorties comportant une référence de log absente. Une citation valide sur la forme ne prouve pas qu'elle soutient l'explication.

## Revue manuelle

Annoter les deux agents pour **tous** les cas de la graine 42, y compris les cas correctement classés, et les erreurs du classifieur. Faire d'abord une lecture des éléments de preuve, avant de juger la prédiction à partir du label. Si possible, faire annoter indépendamment une partie commune par deux personnes, rapporter leur accord brut et résoudre les désaccords. Le formulaire n'est pas aveugle au bras ; mentionner cette limite.

- `hallucination` : `true` si la réponse bien formée contient au moins une affirmation factuelle contradictoire ou non étayée (ex. cause précise présentée comme confirmée sans preuve), sinon `false`. Une hypothèse explicitement présentée comme telle n'est pas une hallucination en soi. Laisser `null` pour le classifieur et les réponses invalides ; ces dernières ont leur propre taux.
- `source_support` : pour les réponses qui citent, `true` si toutes les citations existent dans le contexte et soutiennent les affirmations auxquelles elles sont associées, `false` sinon. Laisser `null` en l'absence de citation. Rapporter le dénominateur de chaque taux.
- `error_category` pour les classifications incorrectes : `routine_event_misread` (événement normal mal interprété), `anomaly_cue_missed`, `missing_or_truncated_evidence`, `irrelevant_retrieval`, `unsupported_root_cause`, `invalid_model_output`, `ambiguous_ground_truth`, `other`. Choisir la catégorie principale ; expliquer l'observation et les preuves dans `notes`. Le label public est conservé même si le cas paraît ambigu.

## Limites à discuter

Un cluster historique et un modèle local léger limitent la généralisation. Le découpage est disjoint par bloc, pas chronologique ni disjoint par cluster ou motif ; il réduit la contamination directe mais des motifs peuvent se répéter entre partitions. Des signaux utiles peuvent être masqués ou tronqués. L'échantillonnage équilibré sert à obtenir des erreurs interprétables, non à reproduire la fréquence des anomalies d'exploitation. Une contamination du préentraînement du LLM par des exemples publics est possible et non vérifiée. La documentation explique le fonctionnement d'HDFS mais ne contient pas la cause certaine d'un incident.
