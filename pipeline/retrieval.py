import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def build_index(chunks: list[dict]) -> dict:
    texts = [chunk["text"] for chunk in chunks]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(texts)

    return {
        "vectorizer": vectorizer,
        "tfidf_matrix": tfidf_matrix,
        "chunks": chunks,
    }


def retrieve(query: str, index: dict, top_k: int = 3) -> list[dict]:
    vectorizer = index["vectorizer"]
    tfidf_matrix = index["tfidf_matrix"]
    chunks = index["chunks"]

    query_vector = vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    ranked_indices = similarities.argsort()[::-1][:top_k]

    results: list[dict] = []
    for rank, chunk_index in enumerate(ranked_indices, start=1):
        chunk = chunks[int(chunk_index)]
        score = float(similarities[chunk_index])
        results.append(
            {
                "rank": rank,
                "chunk_id": chunk["chunk_id"],
                "doc_title": chunk["doc_title"],
                "score": round(score, 4),
                "chunk_text": chunk["text"],
            }
        )

    return results


def run_retrieval(chunks: list[dict], queries: list[dict], top_k: int = 3) -> list[dict]:
    index = build_index(chunks)
    retrieval_results: list[dict] = []

    for query in queries:
        top_results = retrieve(query["question"], index, top_k=top_k)
        result = {
            "query_id": query["query_id"],
            "question": query["question"],
            "top_k": top_results,
        }
        retrieval_results.append(result)

        top_result = top_results[0] if top_results else None
        if top_result is None:
            print(f"{query['query_id']}: no results")
        else:
            print(
                f"{query['query_id']}: {top_result['doc_title']} "
                f"(score={top_result['score']})"
            )

    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    retrieval_path = artifacts_dir / "retrieval.json"
    retrieval_path.write_text(json.dumps(retrieval_results, indent=2), encoding="utf-8")

    return retrieval_results
