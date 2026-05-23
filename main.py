import json
from pathlib import Path

from pipeline.ingest import load_documents, run_ingestion
from pipeline.chunking_comparison import run_chunking_comparison
from pipeline.evaluate import run_evaluation
from pipeline.generate import run_generation
from pipeline.grounding import run_grounding_check
from pipeline.retrieval import run_retrieval
from pipeline.state import PipelineState, StateMachine


def main() -> None:
    state_machine = StateMachine()
    print(f"Current state: {state_machine}")

    documents = load_documents("kb")
    state_machine.advance(PipelineState.DOCUMENTS_LOADED)
    print(f"Current state: {state_machine}")
    print(f"Documents loaded: {len(documents)}")

    chunks = run_ingestion("kb", strategy="sentence")
    state_machine.advance(PipelineState.DOCUMENTS_CHUNKED)
    print(f"Current state: {state_machine}")
    print(f"Chunks created: {len(chunks)}")

    queries_path = Path("queries.json")
    queries = json.loads(queries_path.read_text(encoding="utf-8"))
    state_machine.advance(PipelineState.INDEX_BUILT)
    print(f"Current state: {state_machine}")

    retrieval_results = run_retrieval(chunks, queries)
    state_machine.advance(PipelineState.RETRIEVAL_COMPLETE)
    print(f"Current state: {state_machine}")
    print(f"Queries processed: {len(retrieval_results)}")

    retrieval_path = Path("artifacts") / "retrieval.json"
    saved_retrieval_results = json.loads(retrieval_path.read_text(encoding="utf-8"))
    answers = run_generation(saved_retrieval_results)
    state_machine.advance(PipelineState.ANSWERS_GENERATED)
    print(f"Current state: {state_machine}")
    print(f"Answers generated: {len(answers)}")

    retrieval_results = json.loads(retrieval_path.read_text(encoding="utf-8"))
    queries = json.loads(queries_path.read_text(encoding="utf-8"))
    eval_results, aggregate = run_evaluation(retrieval_results, queries)
    state_machine.advance(PipelineState.EVALUATION_COMPLETE)
    print(f"Current state: {state_machine}")
    print(f"Evaluation records: {len(eval_results)}")
    print(f"Top-3 hit rate: {aggregate['top3_hit_rate']}")

    answers_path = Path("artifacts") / "answers.json"
    answers = json.loads(answers_path.read_text(encoding="utf-8"))
    grounding = run_grounding_check(answers, retrieval_results)
    print(f"Grounding checks: {len(grounding)}")

    run_chunking_comparison(kb_dir="kb", queries=queries)

    print("[API] Run 'uvicorn api.app:app --reload' to start the API server")

    state_machine.advance(PipelineState.VALIDATION_COMPLETE)
    print(f"Current state: {state_machine}")
    state_machine.advance(PipelineState.RESULTS_FINALISED)
    print(f"Current state: {state_machine}")
    print("[DONE] Pipeline complete. Run 'python3 validate.py' to validate.")


if __name__ == "__main__":
    main()
