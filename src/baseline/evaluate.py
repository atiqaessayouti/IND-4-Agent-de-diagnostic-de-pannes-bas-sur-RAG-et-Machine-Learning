
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

if __package__:
    from .train import create_model
else:
    from train import create_model


def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)

    print("=== IND-4 : EVALUATION ML ===")
    print("Accuracy :", accuracy_score(y_test, predictions))
    print("Precision :", precision_score(
        y_test, predictions, pos_label="Anomaly",
        zero_division=0
    ))
    print("Recall :", recall_score(
        y_test, predictions, pos_label="Anomaly",
        zero_division=0
    ))
    print("F1-score :", f1_score(
        y_test, predictions, pos_label="Anomaly",
        zero_division=0
    ))

    print("\nConfusion Matrix:")
    print(confusion_matrix(
        y_test, predictions,
        labels=["Normal", "Anomaly"]
    ))

    print("\nClassification Report:")
    print(classification_report(
        y_test, predictions, zero_division=0
    ))


if __name__ == "__main__":
    # Données synthétiques uniquement pour tester l'évaluation
    X_train = [
        "INFO block received successfully",
        "INFO block stored successfully",
        "INFO block verified successfully",
        "INFO block processed successfully",
        "ERROR block replication failed",
        "ERROR disk failure detected",
        "WARN corrupted data detected",
        "ERROR block recovery failed",
    ]

    y_train = [
        "Normal", "Normal", "Normal", "Normal",
        "Anomaly", "Anomaly", "Anomaly", "Anomaly"
    ]

    X_test = [
        "INFO block stored successfully",
        "ERROR replication failed",
        "INFO block verified",
        "WARN corrupted data",
    ]

    y_test = [
        "Normal", "Anomaly", "Normal", "Anomaly"
    ]

    model = create_model()
    model.fit(X_train, y_train)

    evaluate_model(model, X_test, y_test)
