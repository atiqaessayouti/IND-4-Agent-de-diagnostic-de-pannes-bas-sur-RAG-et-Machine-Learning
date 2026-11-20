# Partie 1 — Dataset HDFS, prétraitement et baseline supervisée

## 1. Description du jeu de données

Notre étude repose sur le jeu de données public HDFS v1 du corpus Loghub, disponible sur Zenodo (enregistrement 8196385).

Ce jeu contient des journaux d'exécution du système Hadoop Distributed File System (HDFS), accompagnés d'étiquettes de référence permettant de distinguer deux classes : **Normal** et **Anomaly**.

Les fichiers principaux sont :

- `HDFS.log` : journal brut contenant les événements système.
- `anomaly_label.csv` : étiquettes des sessions identifiées par leur Block ID.

L'unité d'analyse retenue est la session associée à un identifiant de bloc HDFS.

## 2. Prétraitement des journaux

Un pipeline de prétraitement a été développé afin de transformer les journaux bruts en sessions exploitables par un modèle de classification.

Les opérations sont les suivantes :

1. Extraction des identifiants de blocs (`Block ID`) à partir des messages.
2. Regroupement des événements appartenant à une même session, en conservant leur ordre.
3. Exclusion des lignes mentionnant plusieurs blocs distincts dans le protocole expérimental.
4. Normalisation des messages par suppression des préfixes temporels et masquage des identifiants de blocs, adresses IP et valeurs numériques.
5. Conservation des 12 premiers et 12 derniers événements au maximum, avec limitation à 240 caractères par événement.
6. Association de chaque session à son étiquette de référence.

Cette représentation vise à réduire la variabilité textuelle et la taille des entrées. Elle peut néanmoins provoquer une perte d'informations pertinentes lorsque les sessions sont longues.

## 3. Protocole expérimental

Les expériences utilisent trois graines aléatoires : **42, 123 et 2026**.

Pour chaque graine, les données d'apprentissage comprennent 5 000 sessions normales et 1 000 sessions anormales. L'ensemble de validation comprend 1 000 sessions normales et 250 anomalies.

Un ensemble preview indépendant, composé de 50 sessions normales et 50 anomalies, sert aux vérifications préliminaires. Le test final contient 100 autres sessions réservées et ne doit pas être exploité pour ajuster les modèles.

## 4. Baseline : TF-IDF et régression logistique

Une méthode supervisée classique a été retenue comme baseline scientifique.

La représentation textuelle repose sur **TF-IDF**, avec des unigrammes, des bigrammes et une pondération sous-linéaire des fréquences.

Un classifieur Logistic Regression utilise ensuite ces caractéristiques pour prédire les classes Normal et Anomaly.

Le modèle emploie une pondération équilibrée des classes et un maximum de 1 000 itérations.

Le paramètre de régularisation C est choisi parmi {0,1 ; 1 ; 10} selon le F1-score de la classe Anomaly sur l'ensemble de validation.

## 5. Résultats préliminaires

| Métrique | Moyenne ± écart-type |
|---|---|
| Accuracy | 98,00 % ± 1,00 point |
| Precision Anomaly | 100,00 % ± 0,00 point |
| Recall Anomaly | 96,00 % ± 2,00 points |
| F1-score Anomaly | 97,95 % ± 1,04 point |

Le paramètre C=10 a été sélectionné dans les trois expériences.

Au total, six faux négatifs ont été observés parmi les 300 prédictions du preview, correspondant à quatre blocs HDFS distincts.

L'analyse qualitative révèle trois difficultés potentielles : des avertissements non reconnus par le classifieur, la disparition de certains événements à cause de la troncature et des sessions anormales très courtes dépourvues de messages WARN ou ERROR.

Ces observations restent exploratoires. Une ablation sera nécessaire pour évaluer l'influence réelle de la troncature.

## 6. Limites

Ces performances correspondent uniquement à une évaluation préliminaire équilibrée. Elles ne constituent pas les résultats finaux de l'étude et ne permettent pas d'estimer directement la performance en exploitation sur une distribution naturelle déséquilibrée.

Les résultats définitifs seront établis après comparaison du classifieur avec les deux variantes du modèle de langage, avec et sans recherche documentaire.