# Analyse préliminaire des erreurs — Baseline HDFS

## Résultats du preview

La baseline TF-IDF + régression logistique atteint une exactitude moyenne de 98,00 % (± 1,00 point) et un F1-score moyen de 97,95 % (± 1,04 point) pour la classe Anomaly sur trois graines (42, 123 et 2026).

Sur 100 sessions par graine, six faux négatifs ont été observés, concernant quatre blocs HDFS distincts.

## Analyse qualitative

- Un bloc de 31 événements contenant deux avertissements est classé comme normal dans les trois graines.
- Deux blocs de 41 événements contiennent chacun un avertissement omis lors de la troncature de leur représentation.
- Un bloc de deux événements ne contient que des messages INFO, malgré son étiquette Anomaly.

Ces observations indiquent des limites potentielles de la représentation textuelle : perte d'information lors de la troncature et difficulté à distinguer les anomalies dont les événements ressemblent à des opérations normales.

Cependant, aucune relation causale entre la troncature et les faux négatifs n'a encore été démontrée.

## Limites

Les résultats proviennent d'un jeu preview équilibré de 100 sessions et ne constituent pas l'évaluation finale. Les catégories d'erreurs restent provisoires. Le protocole principal doit rester inchangé avant le test final.