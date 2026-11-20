
import csv
import hashlib
import io
import zipfile
from contextlib import contextmanager
from pathlib import PurePosixPath
from urllib.request import urlopen

import pandas as pd

if __package__:
    from .preprocess import BLOCK_PATTERN, preprocess_hdfs
else:
    from preprocess import BLOCK_PATTERN, preprocess_hdfs


HDFS_URL = "https://zenodo.org/records/8196385/files/HDFS_v1.zip?download=1"
HDFS_MD5 = "76a24b4d9a6164d543fb275f89773260"
LABELS = ("Normal", "Anomaly")


def download_hdfs(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".part")
    digest = hashlib.md5(usedforsecurity=False)
    with partial.open("xb") as target:
        try:
            with urlopen(HDFS_URL, timeout=60) as source:
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    digest.update(chunk)
                    target.write(chunk)
        except BaseException:
            target.close()
            partial.unlink()
            raise
    if digest.hexdigest() != HDFS_MD5:
        partial.unlink()
        raise ValueError("Loghub archive does not match Zenodo's published checksum.")
    partial.replace(path)


@contextmanager
def open_hdfs(archive=None, logs=None, labels=None):
    if archive is None:
        with logs.open(encoding="utf-8", errors="replace") as log_file:
            with labels.open(encoding="utf-8-sig", newline="") as label_file:
                yield log_file, label_file
        return
    with zipfile.ZipFile(archive) as bundle:
        def member(filename):
            matches = [name for name in bundle.namelist() if (
                PurePosixPath(name).name == filename
                and "__MACOSX" not in PurePosixPath(name).parts
            )]
            if len(matches) != 1:
                raise ValueError(f"Expected one {filename} in {archive}; found {matches}.")
            return bundle.open(matches[0])

        with io.TextIOWrapper(member("HDFS.log"), encoding="utf-8", errors="replace") as log_file:
            with io.TextIOWrapper(member("anomaly_label.csv"), encoding="utf-8-sig", newline="") as label_file:
                yield log_file, label_file


def read_labels(source):
    reader = csv.DictReader(source)
    if not reader.fieldnames or not {"BlockId", "Label"}.issubset(reader.fieldnames):
        raise ValueError("Expected BlockId,Label columns in the HDFS label CSV.")
    labels = {}
    for row in reader:
        block_id = (row["BlockId"] or "").strip()
        label = (row["Label"] or "").strip()
        if not BLOCK_PATTERN.fullmatch(block_id) or label not in LABELS:
            raise ValueError(f"Invalid HDFS label row at line {reader.line_num}.")
        if block_id in labels:
            raise ValueError(f"Duplicate ground-truth label for {block_id}.")
        labels[block_id] = label
    return labels


def build_labeled_dataset(log_lines, labels):
    """Associer chaque bloc HDFS à son label."""
    df = preprocess_hdfs(log_lines)

    labels_df = pd.DataFrame(
        list(labels.items()),
        columns=["block_id", "label"]
    )

    dataset = df.merge(
        labels_df,
        on="block_id",
        how="left",
        validate="one_to_one"
    )

    if dataset["label"].isna().any():
        missing = dataset.loc[
            dataset["label"].isna(), "block_id"
        ].tolist()
        raise ValueError(f"Labels manquants: {missing}")

    return dataset


if __name__ == "__main__":
    # Données fictives pour tester notre pipeline
    sample_logs = [
        "INFO Receiving block blk_123 from node1",
        "INFO Writing block blk_123 to disk",
        "WARN Failed to replicate blk_456",
        "INFO Block blk_456 recovery started"
    ]

    sample_labels = {
        "blk_123": "Normal",
        "blk_456": "Anomaly"
    }

    dataset = build_labeled_dataset(
        sample_logs,
        sample_labels
    )

    print("=== HDFS LABELED DATASET ===")
    print(
        dataset[
            ["block_id", "num_events", "label"]
        ].to_string(index=False)
    )
