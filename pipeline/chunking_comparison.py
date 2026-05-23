import json
from pathlib import Path

from pipeline.evaluate import compute_aggregate, evaluate_retrieval
from pipeline.ingest import chunk_documents, load_documents
from pipeline.retrieval import build_index, retrieve


def run_chunking_comparison(kb_dir: str | Path, queries: list[dict]) -> dict:
    strategy_a = _run_strategy(kb_dir, queries, "sentence")
    strategy_b = _run_strategy(kb_dir, queries, "fixed")

    hit_rate_a = strategy_a["aggregate"]["top3_hit_rate"]
    hit_rate_b = strategy_b["aggregate"]["top3_hit_rate"]
    hit_rate_diff = round(abs(hit_rate_a - hit_rate_b), 4)

    if hit_rate_a > hit_rate_b:
        winner = "sentence"
    elif hit_rate_b > hit_rate_a:
        winner = "fixed"
    else:
        winner = "tie"

    explanation = (
        f"Sentence chunking created {strategy_a['chunk_count']} chunks and fixed-size "
        f"chunking created {strategy_b['chunk_count']} chunks. "
        f"The top-3 hit rates were {hit_rate_a} for sentence and {hit_rate_b} for fixed, "
        f"so the comparison result is {winner}."
    )

    comparison = {
        "strategy_a": strategy_a,
        "strategy_b": strategy_b,
        "tradeoff_analysis": {
            "winner": winner,
            "hit_rate_diff": hit_rate_diff,
            "explanation": explanation,
        },
    }

    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    (artifacts_dir / "chunking_comparison.json").write_text(
        json.dumps(comparison, indent=2),
        encoding="utf-8",
    )

    print(f"Chunking comparison winner: {winner}")
    print(f"sentence top3_hit_rate: {hit_rate_a}")
    print(f"fixed top3_hit_rate: {hit_rate_b}")

    return comparison


def _run_strategy(kb_dir: str | Path, queries: list[dict], strategy: str) -> dict:
    documents = load_documents(kb_dir)
    chunks = chunk_documents(documents, strategy=strategy)
    retrieval_results = _retrieve_without_artifact(chunks, queries)
    eval_results = evaluate_retrieval(retrieval_results, queries, save_artifact=False)
    aggregate = compute_aggregate(eval_results, save_artifact=False)

    return {
        "name": strategy,
        "chunk_count": len(chunks),
        "aggregate": aggregate,
    }


def _retrieve_without_artifact(
    chunks: list[dict],
    queries: list[dict],
    top_k: int = 3,
) -> list[dict]:
    index = build_index(chunks)
    retrieval_results: list[dict] = []

    for query in queries:
        retrieval_results.append(
            {
                "query_id": query["query_id"],
                "question": query["question"],
                "top_k": retrieve(query["question"], index, top_k=top_k),
            }
        )

    return retrieval_results
