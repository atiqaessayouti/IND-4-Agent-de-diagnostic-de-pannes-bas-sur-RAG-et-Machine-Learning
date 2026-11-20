from collections import Counter, defaultdict
from statistics import fmean, stdev

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support

from .data.build_dataset import LABELS
from .protocol import BOOTSTRAP_REPS, SEEDS, SPLIT_SEED


BASELINE = "tfidf_logistic"
NO_RETRIEVAL = "llm_no_retrieval"
RAG = "llm_rag"


def percentile(values, quantile):
    return float(np.percentile(values, quantile))


def measure(rows):
    truth = [row["ground_truth"] for row in rows]
    predictions = [row["prediction"] for row in rows]
    precision, recall, f1, _ = precision_recall_fscore_support(
        [label == "Anomaly" for label in truth], [label == "Anomaly" for label in predictions],
        average="binary", zero_division=0,
    )
    label_order = [*LABELS, "Invalid"]
    matrix = confusion_matrix(truth, predictions, labels=label_order).tolist()
    scores = {
        "accuracy": float(accuracy_score(truth, predictions)),
        "anomaly_precision": float(precision),
        "anomaly_recall": float(recall),
        "anomaly_f1": float(f1),
        "normal_recall": matrix[0][0] / sum(matrix[0]),
        "invalid_output_rate": predictions.count("Invalid") / len(rows),
        "latency_ms_p50": percentile([row["latency_ms"] for row in rows], 50),
        "latency_ms_p95": percentile([row["latency_ms"] for row in rows], 95),
    }
    if rows[0]["method"] != BASELINE:
        scores["invalid_citation_response_rate"] = fmean(bool(row["invalid_citation_ids"]) for row in rows)
        scores["invalid_log_reference_rate"] = fmean(bool(row["invalid_log_event_ids"]) for row in rows)
        scores["valid_citation_coverage"] = fmean(
            bool(row["citation_ids"]) and not row["invalid_citation_ids"] for row in rows
        )
        scores["direct_api_cost_usd_per_incident"] = fmean(row["direct_api_cost_usd"] for row in rows)
        for token_key in ("prompt_tokens", "output_tokens"):
            counts = [row[token_key] for row in rows]
            scores[f"mean_{token_key}"] = fmean(counts) if None not in counts else None
            scores[f"n_{token_key}_observed"] = sum(count is not None for count in counts)
    return scores, {"row_labels_true": list(LABELS), "column_labels_predicted": label_order, "counts": matrix[:2]}


def paired_delta(rows, left, right):
    indexed = {(row["method"], row["seed"], row["block_id"]): row for row in rows}
    first_seed = [row for row in rows if row["method"] == left and row["seed"] == SEEDS[0]]
    samples = defaultdict(list)
    for row in first_seed:
        label, block_id = row["ground_truth"], row["block_id"]
        deltas = [int(indexed[left, seed, block_id]["prediction"] == label)
                  - int(indexed[right, seed, block_id]["prediction"] == label) for seed in SEEDS]
        samples[label].append(fmean(deltas))
    rng = np.random.default_rng(SPLIT_SEED)
    resampled = np.zeros(BOOTSTRAP_REPS)
    for label in LABELS:
        data = np.array(samples[label])
        indices = rng.integers(0, len(data), size=(BOOTSTRAP_REPS, len(data)))
        resampled += data[indices].sum(axis=1) / len(first_seed)
    return {
        "left": left, "right": right,
        "accuracy_delta": fmean(delta for values in samples.values() for delta in values),
        "incident_bootstrap_95_ci": [percentile(resampled, 2.5), percentile(resampled, 97.5)],
    }


def summarize(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row["method"], row["seed"]].append(row)
    summary = {"methods": {}, "paired_accuracy_deltas": []}
    for (method, seed), items in groups.items():
        scores, matrix = measure(items)
        summary["methods"].setdefault(method, {"per_seed": {}})["per_seed"][str(seed)] = {
            **scores, "confusion_matrix": matrix,
        }
    for result in summary["methods"].values():
        seed_scores = list(result["per_seed"].values())
        result["across_seeds"] = {}
        for metric in seed_scores[0]:
            values = [score[metric] for score in seed_scores]
            if all(isinstance(value, (float, int)) for value in values):
                result["across_seeds"][metric] = {"mean": fmean(values), "sample_sd": stdev(values)}
    if RAG in summary["methods"]:
        summary["paired_accuracy_deltas"] = [
            paired_delta(rows, RAG, BASELINE), paired_delta(rows, RAG, NO_RETRIEVAL),
        ]
    unique = {row["block_id"]: row for row in rows}.values()
    summary["incident_counts"] = dict(Counter(row["ground_truth"] for row in unique))
    summary["empty_sessions"] = sum(row["event_count"] == 0 for row in unique)
    return summary
