import numpy as np

from .data.build_dataset import LABELS


SEEDS = (42, 123, 2026)
SPLIT_SEED = 4604
EVAL_PER_LABEL = 50
TRAIN_COUNTS = {"Normal": 5000, "Anomaly": 1000}
VALIDATION_COUNTS = {"Normal": 1000, "Anomaly": 250}
STRENGTH_GRID = (0.1, 1.0, 10.0)
EVENTS_PER_END = 12
MAX_EVENT_CHARS = 240
TOP_K = 3
NUM_CTX = 8192
NUM_PREDICT = 350
TEMPERATURE = 0.2
BOOTSTRAP_REPS = 5000


def split_incidents(labels):
    fixed_rng = np.random.default_rng(SPLIT_SEED)
    pools, test, preview = {}, [], []
    for label in LABELS:
        ids = sorted(block_id for block_id in labels if labels[block_id] == label)
        required = 2 * EVAL_PER_LABEL + TRAIN_COUNTS[label] + VALIDATION_COUNTS[label]
        if len(ids) < required:
            raise ValueError(f"HDFS needs at least {required} {label} blocks; got {len(ids)}.")
        shuffled = fixed_rng.permutation(ids).tolist()
        test.extend(shuffled[:EVAL_PER_LABEL])
        preview.extend(shuffled[EVAL_PER_LABEL:2 * EVAL_PER_LABEL])
        pools[label] = shuffled[2 * EVAL_PER_LABEL:]
    splits = {}
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        train, validation = [], []
        for label in LABELS:
            perm = rng.permutation(pools[label]).tolist()
            count = TRAIN_COUNTS[label]
            train.extend(perm[:count])
            validation.extend(perm[count:count + VALIDATION_COUNTS[label]])
        splits[seed] = {
            "train": rng.permutation(train).tolist(),
            "validation": rng.permutation(validation).tolist(),
        }
    return fixed_rng.permutation(test).tolist(), fixed_rng.permutation(preview).tolist(), splits


def incident_text(session):
    return "\n".join(session["events"]) or "[no usable events]"
