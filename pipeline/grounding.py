import json
import re
from pathlib import Path


CITATION_CHUNK_PATTERN = re.compile(r"\[.+? §(.+?)\]")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "for",
    "from",
    "if",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "with",
    "your",
}


def check_grounding(answers: list[dict], retrieval_results: list[dict]) -> list[dict]:
    retrieval_by_query = {
        result["query_id"]: {
            chunk["chunk_id"]: chunk for chunk in result.get("top_k", [])
        }
        for result in retrieval_results
    }
    grounding_results: list[dict] = []

    for answer in answers:
        query_id = answer["query_id"]
        retrieved_chunks = retrieval_by_query.get(query_id, {})
        answer_keywords = _keywords(answer.get("answer", ""))
        citation_checks: list[dict] = []

        for citation in answer.get("citations", []):
            match = CITATION_CHUNK_PATTERN.fullmatch(citation)
            chunk_id = match.group(1) if match else ""
            chunk = retrieved_chunks.get(chunk_id)
            citation_valid = chunk is not None
            overlap_count = 0

            if citation_valid:
                chunk_keywords = _keywords(chunk.get("chunk_text", ""))
                overlap_count = len(answer_keywords & chunk_keywords)

            citation_checks.append(
                {
                    "citation": citation,
                    "chunk_id": chunk_id,
                    "citation_valid": citation_valid,
                    "chunk_found_in_retrieval": chunk is not None,
                    "keyword_overlap_count": overlap_count,
                    "supported": citation_valid and overlap_count >= 1,
                }
            )

        if citation_checks:
            overall_grounded = all(check["supported"] for check in citation_checks)
        else:
            overall_grounded = answer.get("answer_label") != "grounded_answer"

        grounding_results.append(
            {
                "query_id": query_id,
                "answer_label": answer["answer_label"],
                "overall_grounded": overall_grounded,
                "citation_checks": citation_checks,
            }
        )
        print(f"{query_id}: overall_grounded {overall_grounded}")

    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    (artifacts_dir / "grounding_check.json").write_text(
        json.dumps(grounding_results, indent=2),
        encoding="utf-8",
    )

    return grounding_results


def run_grounding_check(answers: list[dict], retrieval_results: list[dict]) -> list[dict]:
    return check_grounding(answers, retrieval_results)


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return {word for word in words if len(word) > 2 and word not in STOPWORDS}
