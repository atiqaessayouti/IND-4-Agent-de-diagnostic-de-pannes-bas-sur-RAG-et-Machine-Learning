# IND-4 — Plan de remise

Le catalogue décrit IND-4 et les directives fixent les jalons et livrables. Les notes ci-dessous traduisent ces exigences en tâches de projet, sans tenir lieu de résultat ni de remise. Aucun chiffre d'exactitude, d'hallucination ou de latence n'est disponible tant que l'exécution et la revue ne sont pas terminées.

## J5 — 24 novembre 2026 : résultats, ablation et erreurs

1. Récupérer HDFS_v1 et vérifier le démarrage du modèle local. Lancer l'aperçu pour vérifier les dépendances, l'archive, le format des sorties et la latence indicative.
2. Versionner le code et consigner le matériel, le modèle et le protocole ; lancer une seule fois l'expérience finale sans ajuster la configuration en fonction du test.
3. Reporter les valeurs de `summary.json` : tableau des trois méthodes (exactitude et F1 ± écart-type, rappel par classe, sorties invalides, latence, jetons) et figure des deux écarts d'exactitude avec intervalles.
4. Compléter la revue manuelle et calculer `review_summary.json` : fréquences par type d'erreur, taux d'hallucination, soutien des citations et dénominateurs. Choisir des cas contrastés, dont un échec, en indiquant leur critère de sélection.

## J6 — 8 décembre 2026 : article, code et soutenance

Le [brouillon de l’article](article_ind4.md) contient le résumé provisoire, l’introduction, les travaux connexes et la méthode. Les mesures et la conclusion restent explicitement à compléter avant export Word et PDF.

**Article Word et PDF** : 8 à 12 pages hors références, deux colonnes. Titre proposé : *La documentation technique améliore-t-elle la détection d'anomalies HDFS par un LLM local ?* Le résumé (150 à 250 mots) annonce la question, les méthodes, les résultats principaux mesurés et leur portée. L'introduction présente les contributions ; les travaux connexes positionnent l'ablation ; la méthode décrit données, partage des cas, reproductibilité et métriques ; les résultats présentent les tableaux, l'ablation et les cas annotés ; la discussion borne la généralisation ; la conclusion répond à la question sans extrapoler aux capteurs ni aux causes racines. Importer les références dans Zotero, Mendeley ou BibTeX pour uniformiser la bibliographie.

**PowerPoint modifiable, 13 diapositives** : (1) titre et équipe ; (2) problème opérationnel ; (3) question et hypothèses ; (4) données et définition d'un incident ; (5) partitions, graines et garde-fous ; (6) baseline ; (7) agent RAG ; (8) contrôle sans recherche ; (9) métriques ; (10) résultats et incertitude ; (11) cas d'erreur et citations ; (12) limites ; (13) conclusion, références clés et commande de reproduction.

**Code** : inclure `README.md`, `requirements.txt`, les paramètres et le code source. Ne pas inclure l'archive de données ni le modèle. Utiliser `SDIA2026_IND-4_<NomDuGroupe>_article.docx`, `SDIA2026_IND-4_<NomDuGroupe>_article.pdf`, `SDIA2026_IND-4_<NomDuGroupe>_presentation.pptx` et `SDIA2026_IND-4_<NomDuGroupe>_code.zip` ou un lien de dépôt. La remise est prévue avant le début de la séance.
