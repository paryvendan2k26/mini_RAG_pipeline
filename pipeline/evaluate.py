import json
from pathlib import Path


def evaluate_retrieval(
    retrieval_results: list[dict],
    queries: list[dict],
    save_artifact: bool = True,
) -> list[dict]:
    queries_by_id = {query["query_id"]: query for query in queries}
    eval_results: list[dict] = []

    for retrieval_result in retrieval_results:
        query_id = retrieval_result["query_id"]
        query = queries_by_id[query_id]
        expected_titles = query["expected_doc_titles"]
        retrieved_titles = [
            chunk["doc_title"] for chunk in retrieval_result.get("top_k", [])[:3]
        ]

        matched_titles = [
            title for title in expected_titles if title in retrieved_titles
        ]
        matched_expected_title = bool(matched_titles)

        if len(matched_titles) == len(expected_titles):
            retrieval_status = "hit"
            first_rank = retrieved_titles.index(matched_titles[0]) + 1
            explanation = f"Expected title found at rank {first_rank}"
        elif matched_titles:
            retrieval_status = "partial_hit"
            explanation = "Some expected titles found in top 3"
        else:
            retrieval_status = "miss"
            explanation = "Expected title not found in top 3"

        eval_results.append(
            {
                "query_id": query_id,
                "expected_doc_titles": expected_titles,
                "retrieved_doc_titles_top3": retrieved_titles,
                "retrieval_status": retrieval_status,
                "matched_expected_title": matched_expected_title,
                "explanation": explanation,
            }
        )

    if save_artifact:
        artifacts_dir = Path("artifacts")
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        (artifacts_dir / "eval.json").write_text(
            json.dumps(eval_results, indent=2),
            encoding="utf-8",
        )

    return eval_results


def compute_aggregate(eval_results: list[dict], save_artifact: bool = True) -> dict:
    total_queries = len(eval_results)
    hits = sum(1 for result in eval_results if result["retrieval_status"] == "hit")
    partial_hits = sum(
        1 for result in eval_results if result["retrieval_status"] == "partial_hit"
    )
    misses = sum(1 for result in eval_results if result["retrieval_status"] == "miss")
    top3_hit_rate = round(hits / total_queries, 4) if total_queries else 0.0

    aggregate = {
        "top3_hit_rate": top3_hit_rate,
        "total_queries": total_queries,
        "hits": hits,
        "partial_hits": partial_hits,
        "misses": misses,
    }

    if save_artifact:
        artifacts_dir = Path("artifacts")
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        eval_path = artifacts_dir / "eval.json"
        eval_path.write_text(
            json.dumps([*eval_results, {"aggregate": aggregate}], indent=2),
            encoding="utf-8",
        )

    print("Retrieval Evaluation Summary")
    print(f"total_queries: {total_queries}")
    print(f"hits: {hits}")
    print(f"partial_hits: {partial_hits}")
    print(f"misses: {misses}")
    print(f"top3_hit_rate: {top3_hit_rate}")

    return aggregate


def run_evaluation(retrieval_results: list[dict], queries: list[dict]) -> tuple[list[dict], dict]:
    eval_results = evaluate_retrieval(retrieval_results, queries)
    aggregate = compute_aggregate(eval_results)
    return eval_results, aggregate
