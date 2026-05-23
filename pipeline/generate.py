import hashlib
import datetime
import json
import logging
import os
import re
from pathlib import Path

import jsonlines
from dotenv import load_dotenv
from groq import Groq


MODEL_NAME = "llama-3.1-8b-instant"
CITATION_PATTERN = re.compile(r"\[.+? §.+?\]")


def build_context_block(top_k_chunks: list[dict]) -> str:
    lines = []
    for i, chunk in enumerate(top_k_chunks, 1):
        doc_title = chunk["doc_title"]
        chunk_id = chunk["chunk_id"]
        text = chunk["chunk_text"]
        lines.append(f"[{i}] doc_title: {doc_title} | chunk_id: {chunk_id}")
        lines.append(f"    {text}")
        lines.append("")
    return "\n".join(lines)


def build_prompt(question: str, context_block: str) -> dict[str, str]:
    system_prompt = """You are a support assistant. Answer ONLY using the numbered context chunks provided below.

CITATION RULES - follow exactly:
- Every factual claim MUST include a citation
- Citation format MUST be: [doc_title §chunk_id]
- Use the exact doc_title and chunk_id shown in the context header, not the number
- Example: [Password reset and account recovery §password-reset-and-account-recovery_s1]
- Never use just a number like [1] as a citation
- Never invent facts outside the context

ANSWER RULES:
- If the context contains relevant information, use it and cite it
- Even partial answers must be given if context is relevant
- Only respond with INSUFFICIENT_CONTEXT: <reason> if the context has absolutely no relevant information
- Never say information is unavailable if it appears in the context chunks

ANSWER FORMAT:
Your answer sentence. [doc_title §chunk_id]"""
    user_prompt = f"Context:\n{context_block}\n\nQuestion:\n{question}"
    return {"system": system_prompt, "user": user_prompt}


def parse_answer(raw_text: str, top_k_chunks: list[dict]) -> dict:
    answer = raw_text.strip()
    answer_label = (
        "insufficient_context"
        if answer.startswith("INSUFFICIENT_CONTEXT:")
        else "grounded_answer"
    )
    citations = CITATION_PATTERN.findall(answer)

    retrieved_by_chunk_id = {chunk["chunk_id"]: chunk for chunk in top_k_chunks}
    valid_citations = {
        f"[{chunk['doc_title']} §{chunk['chunk_id']}]": chunk["chunk_id"]
        for chunk in top_k_chunks
    }

    used_chunk_ids: list[str] = []
    for citation in citations:
        chunk_id = valid_citations.get(citation)
        if chunk_id is None:
            chunk_id = _extract_chunk_id_from_citation(citation)
            if chunk_id not in retrieved_by_chunk_id:
                logging.warning("Invalid citation not found in retrieved chunks: %s", citation)
                continue
            logging.warning("Citation doc title mismatch or formatting mismatch: %s", citation)

        if chunk_id not in used_chunk_ids:
            used_chunk_ids.append(chunk_id)

    return {
        "answer_label": answer_label,
        "answer": answer,
        "citations": citations,
        "used_chunk_ids": used_chunk_ids,
    }


def _extract_chunk_id_from_citation(citation: str) -> str:
    citation_body = citation.strip()[1:-1]
    if " §" not in citation_body:
        return ""
    return citation_body.rsplit(" §", maxsplit=1)[1].strip()


def call_llm(prompt_dict, query_id):
    load_dotenv()
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": prompt_dict["system"]},
            {"role": "user", "content": prompt_dict["user"]},
        ],
        max_tokens=1000,
    )
    raw_text = response.choices[0].message.content

    prompt_hash = hashlib.md5(prompt_dict["user"].encode()).hexdigest()
    log_record = {
        "stage": "answer_generation",
        "query_id": query_id,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "provider": "groq",
        "model": "llama-3.1-8b-instant",
        "prompt_hash": prompt_hash,
        "input_artifacts": ["artifacts/retrieval.json"],
        "output_artifact": "artifacts/answers.json"
    }
    log_path = Path("llm_calls.jsonl")

    with jsonlines.open(log_path, mode="a") as writer:
        writer.write(log_record)

    return raw_text


def run_generation(retrieval_results: list[dict]) -> list[dict]:
    answer_results: list[dict] = []

    for retrieval_result in retrieval_results:
        query_id = retrieval_result["query_id"]
        context_block = build_context_block(retrieval_result["top_k"])
        prompt_dict = build_prompt(retrieval_result["question"], context_block)
        raw_answer = call_llm(prompt_dict, query_id)
        parsed_answer = parse_answer(raw_answer, retrieval_result["top_k"])
        answer_result = {"query_id": query_id, **parsed_answer}
        answer_results.append(answer_result)

        print(f"{query_id}: {answer_result['answer_label']} - {answer_result['answer'][:80]}")

    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    answers_path = artifacts_dir / "answers.json"
    answers_path.write_text(json.dumps(answer_results, indent=2), encoding="utf-8")

    return answer_results
