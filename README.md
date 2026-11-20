# IND-4 — Détection d'anomalies HDFS avec documentation technique

Ce projet compare trois méthodes sur les mêmes blocs HDFS v1 : TF-IDF + régression logistique, LLM local avec recherche documentaire (RAG), et même LLM sans recherche. L'archive publique donne une vérité terrain **Normal / Anomaly au niveau du bloc** : elle permet de comparer la détection et d'auditer les explications, pas de mesurer l'identification de causes racines ni l'apport de capteurs.

## Démarrage sous Windows

Depuis la racine du projet, avec Python 3.11 (vérifier avec `python --version`) :

```powershell
python -m pip install -r requirements.txt
```

Si le `.venv` actuel est rattaché à une installation Python inaccessible, créer un autre environnement sans écraser l'ancien : `py -3.11 -m venv .venv-ind4`, puis remplacer `python` dans les commandes par `..venv-ind4Scriptspython.exe`.

Installer et démarrer [Ollama](https://ollama.com/download/windows), puis télécharger le modèle local (environ 1,9 Go) :

```powershell
ollama pull qwen2.5:3b-instruct
```

## Commande unique : expérience principale

```powershell
python -m src.experiment --download
```

La commande télécharge au besoin [HDFS_v1.zip sur Zenodo](https://zenodo.org/records/8196385), vérifie le MD5 publié, lit les fichiers dans l'archive sans les extraire, puis lance les trois méthodes. L'archive fait environ 187 Mo. On peut aussi utiliser `--archive cheminHDFS_v1.zip` ou `--logs cheminHDFS.log --labels cheminanomaly_label.csv`. Le fichier `HDFS_2k.log` est un extrait de démonstration, pas un substitut à l'archive et aux labels de blocs. Les données brutes et sorties locales sont exclues du dépôt.

Pour vérifier la chaîne avec le classifieur seul, **sans ouvrir le test final** et sans Ollama :

```powershell
python -m src.experiment --download --preview --baseline-only
```

Pour vérifier les deux agents, utiliser `--preview` sans `--baseline-only`, dans un autre répertoire via `--output results/preview_agents`. Le test final est réservé à la configuration figée ; il exécute 600 générations locales et 300 prédictions du classifieur. Si une exécution est interrompue, relancer la même commande avec `--resume` : les lignes déjà écrites ne sont pas recalculées. Ne pas relancer un test terminé pour essayer un autre modèle ou un autre prompt.

## Exploitation des résultats

- `run.json` : versions, matériel déclaré, paramètres, empreintes des fichiers et du modèle. `splits.json` : identifiants évalués, d'entraînement et de validation.
- `summary.json` : métriques par graine, moyennes et écarts-types, matrices de confusion et écarts d'exactitude appariés avec intervalles bootstrap.
- `predictions.jsonl` : diagnostics, latence, jetons, passages retrouvés et références hors contexte, incident par incident.
- `review_template.jsonl` : à copier sous `review_annotations.jsonl` et à annoter selon la grille du [protocole](docs/protocole.md#revue-manuelle). Les champs hors de `review` doivent rester inchangés.

```powershell
python -m src.review results/final/review_annotations.jsonl --template results/final/review_template.jsonl --output results/final/review_summary.json
```

Le [protocole expérimental](docs/protocole.md), la [bibliographie de travail](docs/etat_de_l_art.md) et le [plan de remise](docs/remise.md) décrivent les décisions et les livrables restants. Les démonstrations initiales (`python -m src.baseline.train` et `python -m src.baseline.evaluate`) sont des essais synthétiques, pas des résultats scientifiques.
