import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import fmean

from .metrics import BASELINE
from .protocol import SEEDS


ERROR_CATEGORIES = (
    "routine_event_misread", "anomaly_cue_missed", "missing_or_truncated_evidence",
    "irrelevant_retrieval", "unsupported_root_cause", "invalid_model_output",
    "ambiguous_ground_truth", "other",
)


def build_review(rows, sessions):
    for row in rows:
        if row["seed"] != SEEDS[0]:
            continue
        is_agent = row["method"] != BASELINE
        is_error = row["prediction"] != row["ground_truth"]
        if not is_agent and not is_error:
            continue
        yield {
            **row,
            "events": sessions[row["block_id"]]["events"],
            "review": {"hallucination": None, "source_support": None, "error_category": None, "notes": ""},
        }


def review_summary(rows):
    methods = defaultdict(list)
    for row in rows:
        findings = row["review"]
        agent = row["method"] != BASELINE
        malformed = row["prediction"] == "Invalid"
        has_citations = bool(row.get("citation_ids"))
        wrong = row["prediction"] != row["ground_truth"]
        if agent and not malformed and type(findings["hallucination"]) is not bool:
            raise ValueError(f"Set review.hallucination to true/false for {row['method']} {row['block_id']}.")
        if has_citations and type(findings["source_support"]) is not bool:
            raise ValueError(f"Set review.source_support to true/false for {row['method']} {row['block_id']}.")
        if wrong and findings["error_category"] not in ERROR_CATEGORIES:
            raise ValueError(f"Set a valid error_category for {row['method']} {row['block_id']}.")
        methods[row["method"]].append(row)
    results = {}
    for method, reviews in methods.items():
        valid_agent_reviews = [row for row in reviews if method != BASELINE and row["prediction"] != "Invalid"]
        citations = [row for row in reviews if row.get("citation_ids")]
        results[method] = {
            "n_reviewed": len(reviews),
            "n_valid_agent_outputs_reviewed": len(valid_agent_reviews),
            "n_responses_with_citations_reviewed": len(citations),
            "hallucination_rate_on_valid_responses": fmean(
                row["review"]["hallucination"] for row in valid_agent_reviews) if valid_agent_reviews else None,
            "source_support_rate_on_responses_with_citations": fmean(
                row["review"]["source_support"] for row in citations) if citations else None,
            "error_categories": dict(Counter(row["review"]["error_category"] for row in reviews
                                             if row["prediction"] != row["ground_truth"])),
        }
    return results


def main():
    parser = argparse.ArgumentParser(description="Score human annotations without re-running the test set.")
    parser.add_argument("annotations", type=Path)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    def read_review(path):
        with path.open(encoding="utf-8-sig") as stream:
            return [json.loads(line) for line in stream if line.strip()]

    def original_fields(items):
        return sorted(({key: value for key, value in row.items() if key != "review"} for row in items),
                      key=lambda row: (row["method"], row["block_id"]))

    try:
        rows = read_review(args.annotations)
        if not rows or original_fields(rows) != original_fields(read_review(args.template)):
            raise ValueError("The annotations must match the full original template except for review fields.")
        result = review_summary(rows)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
