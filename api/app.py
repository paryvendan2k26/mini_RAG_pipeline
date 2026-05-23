import json
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from pipeline.generate import build_context_block, build_prompt, call_llm, parse_answer
from pipeline.retrieval import build_index, retrieve


app = FastAPI(title="Mini-RAG Pipeline")


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer_label: str
    answer: str
    citations: list[str]


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "pipeline": "mini-rag"}


@app.post("/answer", response_model=AnswerResponse)
async def answer_question(request: QuestionRequest) -> AnswerResponse:
    chunks_path = Path("artifacts") / "chunks.json"
    chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
    index = build_index(chunks)
    top_k_chunks = retrieve(request.question, index, top_k=3)
    context_block = build_context_block(top_k_chunks)
    prompt = build_prompt(request.question, context_block)
    raw_answer = call_llm(prompt, query_id="api_request")
    parsed_answer = parse_answer(raw_answer, top_k_chunks)

    return AnswerResponse(
        answer_label=parsed_answer["answer_label"],
        answer=parsed_answer["answer"],
        citations=parsed_answer["citations"],
    )
