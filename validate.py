import json
import re
import sys
from pathlib import Path


ARTIFACT_FILES = [
    "chunks.json",
    "retrieval.json",
    "answers.json",
    "eval.json",
    "grounding_check.json",
    "chunking_comparison.json",
]
ANSWER_LABELS = {"grounded_answer", "insufficient_context", "conflicting_context"}
RETRIEVAL_STATUSES = {"hit", "partial_hit", "miss"}
CITATION_CHUNK_PATTERN = re.compile(r"\[.+? §(.+?)\]")


def run_validation() -> bool:
    artifacts_dir = Path("artifacts")
    loaded: dict[str, object] = {}
    passed = 0
    failed = 0

    def record(name: str, condition: bool) -> None:
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"PASS: {name}")
        else:
            failed += 1
            print(f"FAIL: {name}")

    artifact_paths = {name: artifacts_dir / name for name in ARTIFACT_FILES}
    record("ARTIFACTS EXIST", all(path.exists() for path in artifact_paths.values()))

    json_valid = True
    for name, path in artifact_paths.items():
        try:
            loaded[name] = json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            json_valid = False
    record("JSON VALIDITY", json_valid)

    chunks = loaded.get("chunks.json", [])
    retrieval = loaded.get("retrieval.json", [])
    answers = loaded.get("answers.json", [])
    eval_data = loaded.get("eval.json", [])
    eval_records = [
        record_item for record_item in eval_data
        if isinstance(record_item, dict) and "aggregate" not in record_item
    ] if isinstance(eval_data, list) else []

    record(
        "ALL QUERIES PROCESSED",
        isinstance(chunks, list)
        and len(chunks) >= 1
        and isinstance(retrieval, list)
        and len(retrieval) == 5
        and isinstance(answers, list)
        and len(answers) == 5
        and len(eval_records) >= 5,
    )

    retrieval_quality = isinstance(retrieval, list) and all(
        len(result.get("top_k", [])) >= 3
        and all(isinstance(chunk.get("score"), float) for chunk in result.get("top_k", []))
        for result in retrieval
        if isinstance(result, dict)
    )
    record("RETRIEVAL QUALITY", retrieval_quality)

    controlled_answers = isinstance(answers, list) and all(
        answer.get("answer_label") in ANSWER_LABELS
        for answer in answers
        if isinstance(answer, dict)
    )
    controlled_retrieval = all(
        item.get("retrieval_status") in RETRIEVAL_STATUSES for item in eval_records
    )
    record("CONTROLLED VOCABULARY", controlled_answers and controlled_retrieval)

    retrieval_chunk_ids_by_query = {
        result["query_id"]: {
            chunk["chunk_id"] for chunk in result.get("top_k", [])
        }
        for result in retrieval
        if isinstance(result, dict)
    } if isinstance(retrieval, list) else {}
    citation_integrity = True
    if isinstance(answers, list):
        for answer in answers:
            if not isinstance(answer, dict):
                citation_integrity = False
                continue
            citations = answer.get("citations", [])
            if answer.get("answer_label") == "grounded_answer" and not citations:
                citation_integrity = False
            valid_chunk_ids = retrieval_chunk_ids_by_query.get(answer.get("query_id"), set())
            for citation in citations:
                match = CITATION_CHUNK_PATTERN.fullmatch(citation)
                if not match or match.group(1) not in valid_chunk_ids:
                    citation_integrity = False
    else:
        citation_integrity = False
    record("CITATION INTEGRITY", citation_integrity)

    aggregate = None
    if isinstance(eval_data, list):
        for item in eval_data:
            if isinstance(item, dict) and "aggregate" in item:
                aggregate = item["aggregate"]
                break
    aggregate_keys = {"top3_hit_rate", "total_queries", "hits", "partial_hits", "misses"}
    record(
        "AGGREGATE SUMMARY",
        isinstance(aggregate, dict) and aggregate_keys.issubset(aggregate.keys()),
    )

    print(f"PASSED: {passed} checks")
    print(f"FAILED: {failed} checks")
    return failed == 0


def validate_outputs() -> dict:
    success = run_validation()
    return {"success": success}


if __name__ == "__main__":
    sys.exit(0 if run_validation() else 1)
