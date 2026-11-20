
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.pipeline import Pipeline


def create_model(strength=1.0, seed=42):
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)),
        ("classifier", LogisticRegression(
            C=strength,
            max_iter=1000,
            class_weight="balanced",
            random_state=seed
        ))
    ])


def fit_baseline(train, validation, seed, grid):
    train_text, train_labels = zip(*train)
    validation_text, validation_labels = zip(*validation)
    best_model, best_score, best_strength = None, -1.0, None
    scores = {}
    for strength in grid:
        model = create_model(strength=strength, seed=seed)
        model.fit(train_text, train_labels)
        score = f1_score(validation_labels, model.predict(validation_text),
                         pos_label="Anomaly", zero_division=0)
        scores[str(strength)] = score
        if score > best_score:
            best_model, best_score, best_strength = model, score, strength
    return best_model, {"selected_C": best_strength, "validation_f1": scores}


if __name__ == "__main__":
    if __package__:
        from ..data.build_dataset import build_labeled_dataset
    else:
        from pathlib import Path
        import sys

        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "data"))
        from build_dataset import build_labeled_dataset

    # Données synthétiques : test technique uniquement
    sample_logs = [
        "INFO Block blk_101 received successfully",
        "INFO Block blk_102 stored successfully",
        "INFO Block blk_103 verified successfully",
        "INFO Block blk_104 processed successfully",
        "ERROR Block blk_201 replication failed",
        "ERROR Block blk_202 disk failure detected",
        "WARN Block blk_203 corrupted data detected",
        "ERROR Block blk_204 recovery failed"
    ]

    sample_labels = {
        "blk_101": "Normal",
        "blk_102": "Normal",
        "blk_103": "Normal",
        "blk_104": "Normal",
        "blk_201": "Anomaly",
        "blk_202": "Anomaly",
        "blk_203": "Anomaly",
        "blk_204": "Anomaly"
    }

    dataset = build_labeled_dataset(
        sample_logs, sample_labels
    )

    X = dataset["log_messages"]
    y = dataset["label"]

    model = create_model()
    model.fit(X, y)

    print("=== IND-4 : BASELINE ML ===")
    print("Nombre de blocs :", len(dataset))
    print("Classes :", list(model.classes_))
    print("Entrainement termine !")

    test_log = [
        "ERROR Block blk_999 replication failed"
    ]

    prediction = model.predict(test_log)
    print("Prediction de test :", prediction[0])
