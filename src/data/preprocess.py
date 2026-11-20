
import re
from collections import deque
import pandas as pd

BLOCK_PATTERN = re.compile(r"blk_-?\d+")
LOG_PREFIX = re.compile(r"^\d{6}\s+\d{6}\s+\d+\s+")
IP_ADDRESS = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?\b")
NUMBER = re.compile(r"\b\d+\b")


def extract_block_ids(log_line):
    """Extraire les identifiants des blocs HDFS."""
    return list(dict.fromkeys(BLOCK_PATTERN.findall(log_line)))


def normalize_event(log_line):
    text = LOG_PREFIX.sub("", log_line.strip())
    text = BLOCK_PATTERN.sub("<BLOCK>", text)
    text = IP_ADDRESS.sub("<IP>", text)
    return NUMBER.sub("<NUM>", text)


def selected_sessions(log_lines, block_ids, events_per_end=12, max_chars=240):
    heads = {block_id: [] for block_id in block_ids}
    tails = {}
    counts = dict.fromkeys(heads, 0)
    for line in log_lines:
        blocks = extract_block_ids(line)
        if len(blocks) != 1 or blocks[0] not in heads:
            continue
        block_id = blocks[0]
        counts[block_id] += 1
        event = normalize_event(line)[:max_chars]
        if len(heads[block_id]) < events_per_end:
            heads[block_id].append(event)
        else:
            if block_id not in tails:
                tails[block_id] = deque(maxlen=events_per_end)
            tails[block_id].append(event)
    for block_id, head in heads.items():
        tail = list(tails.get(block_id, ()))
        omitted = counts[block_id] - len(head) - len(tail)
        yield block_id, {
            "events": head + (["[events omitted]"] if omitted else []) + tail,
            "event_count": counts[block_id],
        }


def preprocess_hdfs(log_lines):
    """Regrouper les logs par Block ID."""
    records = []

    for line in log_lines:
        block_ids = extract_block_ids(line)

        for block_id in block_ids:
            records.append({
                "block_id": block_id,
                "log_message": line.strip()
            })

    df = pd.DataFrame(records)

    if df.empty:
        return pd.DataFrame(
            columns=["block_id", "log_messages", "num_events"]
        )

    result = (
        df.groupby("block_id", sort=True)
        .agg(
            log_messages=("log_message", lambda x: " ".join(x)),
            num_events=("log_message", "count")
        )
        .reset_index()
    )

    return result


if __name__ == "__main__":
    sample_logs = [
        "INFO Receiving block blk_123 from node1",
        "INFO Writing block blk_123 to disk",
        "WARN Failed to replicate blk_456",
        "INFO Block blk_456 recovery started"
    ]

    result = preprocess_hdfs(sample_logs)

    print("=== HDFS PREPROCESSING ===")
    print(result[["block_id", "num_events"]].to_string(index=False))
