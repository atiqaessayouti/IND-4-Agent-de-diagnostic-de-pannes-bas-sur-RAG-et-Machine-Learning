import argparse
import hashlib
import json
import platform
import sys
from importlib.metadata import version
from pathlib import Path
from time import perf_counter

import numpy as np

from . import protocol
from .agent import CORPUS, DEFAULT_MODEL, Ollama, Retriever, diagnose
from .baseline.train import fit_baseline
from .data.build_dataset import download_hdfs, open_hdfs, read_labels
from .data.preprocess import selected_sessions
from .metrics import BASELINE, NO_RETRIEVAL, RAG, summarize
from .review import build_review


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARCHIVE = ROOT / "data" / "raw" / "HDFS_v1.zip"


def fingerprint(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, data):
    staged = path.with_suffix(path.suffix + ".tmp")
    with staged.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    staged.replace(path)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def prediction_key(row):
    return row["method"], row["seed"], row["block_id"]


def run_manifest(args, model_metadata):
    if args.logs is not None:
        datasets = {"logs": fingerprint(args.logs), "labels": fingerprint(args.labels)}
    else:
        datasets = {"archive": fingerprint(args.archive)}
    return {
        "mode": "preview" if args.preview else "final_test",
        "methods": [BASELINE] if args.baseline_only else [BASELINE, RAG, NO_RETRIEVAL],
        "data_sha256": datasets,
        "source_sha256": {source.relative_to(ROOT).as_posix(): fingerprint(source)
                          for source in sorted([*(ROOT / "src").rglob("*.py"), CORPUS])},
        "python": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "dependency_versions": {name: version(name) for name in (
            "numpy", "pandas", "scikit-learn", "scipy", "threadpoolctl", "joblib",
        )},
        "ollama": model_metadata,
        "settings": {name.lower(): value for name, value in vars(protocol).items()
                     if name.isupper() and name != "LABELS"},
    }


def inputs(args):
    if args.logs is None:
        args.archive = args.archive or DEFAULT_ARCHIVE
        if not args.archive.exists():
            if not args.download:
                raise ValueError(f"Missing {args.archive}. Pass --download or point to a local archive.")
            print("Downloading Loghub HDFS_v1 from Zenodo...", flush=True)
            download_hdfs(args.archive)


def run(args):
    output = args.output
    manifest_path = output / "run.json"
    summary_path = output / "summary.json"
    predictions_path = output / "predictions.jsonl"
    if args.resume and (not manifest_path.is_file() or summary_path.exists()):
        raise ValueError("Can resume only an interrupted run with run.json and no summary.json.")
    if not args.resume and output.exists():
        raise ValueError(f"Output already exists: {output}. Use a new directory or --resume.")
    engine = None if args.baseline_only else Ollama(args.model)
    model_metadata = engine.metadata() if engine is not None else None
    inputs(args)
    manifest = run_manifest(args, model_metadata)
    manifest = json.loads(json.dumps(manifest))
    if args.resume and read_json(manifest_path) != manifest:
        raise ValueError("Run settings, model, code, environment or data changed. Cannot resume.")

    print("Reading labels and streaming the selected HDFS sessions...", flush=True)
    with open_hdfs(args.archive, args.logs, args.labels) as (logs, label_file):
        labels = read_labels(label_file)
        test, preview, splits = protocol.split_incidents(labels)
        evaluation = preview if args.preview else test
        targets = set(evaluation)
        for split in splits.values():
            targets.update(split["train"])
            targets.update(split["validation"])
        sessions = dict(selected_sessions(logs, targets, protocol.EVENTS_PER_END, protocol.MAX_EVENT_CHARS))

    if not args.resume:
        output.mkdir(parents=True, exist_ok=False)
        write_json(manifest_path, manifest)
    write_json(output / "splits.json", {"evaluation": evaluation, "runs": splits})
    existing = {}
    if predictions_path.is_file():
        with predictions_path.open(encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                key = prediction_key(row)
                if (key in existing or row["method"] not in manifest["methods"]
                        or row["seed"] not in splits or row["block_id"] not in evaluation
                        or row["ground_truth"] != labels[row["block_id"]]):
                    raise ValueError(f"Unexpected or duplicate prediction in {predictions_path}: {key}.")
                existing[key] = row

    def examples(ids):
        return [(protocol.incident_text(sessions[block_id]), labels[block_id]) for block_id in ids]

    retriever = None if engine is None else Retriever()
    tuning = {}
    with predictions_path.open("a", encoding="utf-8", newline="\n") as stream:
        for seed, split in splits.items():
            model, tuning[seed] = fit_baseline(examples(split["train"]), examples(split["validation"]),
                                              seed, protocol.STRENGTH_GRID)
            print(f"Seed {seed}: baseline trained (C={tuning[seed]['selected_C']}).", flush=True)
            if engine is not None:
                engine.warm()
            order = np.random.default_rng(seed).permutation(evaluation).tolist()
            for index, block_id in enumerate(order, 1):
                agent_order = (RAG, NO_RETRIEVAL) if index % 2 else (NO_RETRIEVAL, RAG)
                methods = (BASELINE,) if engine is None else (BASELINE, *agent_order)
                for method in methods:
                    key = method, seed, block_id
                    if key in existing:
                        continue
                    session = sessions[block_id]
                    if method == BASELINE:
                        start = perf_counter()
                        prediction = str(model.predict([protocol.incident_text(session)])[0])
                        details = {"prediction": prediction, "latency_ms": (perf_counter() - start) * 1000}
                    else:
                        details = diagnose(engine, session, seed, retriever if method == RAG else None)
                    row = {"method": method, "seed": seed, "block_id": block_id,
                           "ground_truth": labels[block_id], "event_count": session["event_count"], **details}
                    stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
                    stream.flush()
                    existing[key] = row
                if index % 10 == 0 or index == len(order):
                    print(f"Seed {seed}: {index}/{len(order)} incidents complete.", flush=True)

    rows = list(existing.values())
    with (output / "review_template.jsonl").open("w", encoding="utf-8", newline="\n") as stream:
        for row in build_review(rows, sessions):
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    summary = {"mode": manifest["mode"], "tuning": tuning, **summarize(rows)}
    write_json(summary_path, summary)
    for method, metrics in summary["methods"].items():
        accuracy = metrics["across_seeds"]["accuracy"]
        print(f"{method}: accuracy {accuracy['mean']:.3f} (SD {accuracy['sample_sd']:.3f})")
    print(f"Results: {summary_path}")


def main():
    parser = argparse.ArgumentParser(description="Run the preregistered IND-4 HDFS comparison.")
    parser.add_argument("--archive", type=Path, help="Local Loghub HDFS_v1.zip (default: data/raw/HDFS_v1.zip).")
    parser.add_argument("--download", action="store_true", help="Download the official archive if missing.")
    parser.add_argument("--logs", type=Path, help="Use an extracted HDFS.log instead of the ZIP.")
    parser.add_argument("--labels", type=Path, help="Use the matching extracted anomaly_label.csv with --logs.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Locally installed Ollama model tag.")
    parser.add_argument("--preview", action="store_true", help="Use the independent preview set, not final test.")
    parser.add_argument("--baseline-only", action="store_true", help="Skip Ollama on the preview set only.")
    parser.add_argument("--output", type=Path, help="New results directory (default: results/final or results/preview).")
    parser.add_argument("--resume", action="store_true", help="Continue an interrupted run with identical settings.")
    args = parser.parse_args()
    if bool(args.logs) != bool(args.labels) or (args.logs is not None and (args.archive or args.download)):
        parser.error("Use --logs and --labels together, or use an archive with optional --download.")
    if args.baseline_only and not args.preview:
        parser.error("--baseline-only requires --preview so the final test stays untouched.")
    if args.output is None:
        args.output = ROOT / "results" / ("preview" if args.preview else "final")
    try:
        run(args)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"IND-4: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
