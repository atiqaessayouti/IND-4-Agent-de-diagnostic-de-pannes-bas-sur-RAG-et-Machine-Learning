# Soutenance IND-4 — Partie 1

## 1. Présentation du dataset HDFS

Dans notre projet, nous avons utilisé le dataset public HDFS v1 issu du corpus Loghub.

Ce dataset contient des journaux d'événements du système Hadoop Distributed File System. Chaque session est identifiée par un Block ID et associée à une étiquette Normal ou Anomaly.

Notre objectif est de préparer ces données afin de permettre une comparaison rigoureuse entre une méthode classique de machine learning et des agents basés sur les modèles de langage.

## 2. Prétraitement des données

Nous avons d'abord extrait les identifiants de blocs et regroupé les événements appartenant à la même session.

Ensuite, nous avons normalisé les messages en masquant certaines informations variables, notamment les adresses IP, les identifiants et les valeurs numériques.

Pour limiter la longueur des entrées, nous avons conservé les 12 premiers et les 12 derniers événements des longues sessions.

## 3. Baseline Machine Learning

Comme méthode de référence, nous avons utilisé TF-IDF combiné avec une régression logistique.

TF-IDF transforme les messages textuels en caractéristiques numériques, tandis que la régression logistique prédit si une session est normale ou anormale.

Nous avons répété les expériences avec trois graines aléatoires afin d'évaluer la variabilité des performances.

## 4. Résultats préliminaires

Sur notre ensemble preview de 100 sessions équilibrées, nous avons obtenu :

- Accuracy moyenne : 98 %.
- Précision pour les anomalies : 100 %.
- Rappel pour les anomalies : 96 %.
- F1-score pour les anomalies : 97,95 %.

Nous avons également observé six faux négatifs sur les trois exécutions, correspondant à quatre blocs distincts.

L'analyse a montré notamment que certains avertissements sont omis lors de la troncature des longues sessions. Cependant, une expérience complémentaire serait nécessaire pour démontrer l'effet de cette troncature sur les performances.

Ces résultats constituent une évaluation préliminaire et non les résultats finaux de la comparaison des trois méthodes.s