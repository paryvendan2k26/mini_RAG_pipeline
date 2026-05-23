# Mini-RAG Pipeline

This project is a compact retrieval-augmented generation pipeline for local knowledge-base support answers. It ingests text documents, chunks them, retrieves relevant context with TF-IDF, generates citation-strict answers with Groq, evaluates retrieval quality, checks grounding, compares chunking strategies, and exposes a small FastAPI endpoint.

## Setup

Use Python 3.11+ when possible.

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```bash
GROQ_API_KEY=your_groq_key_here
```

## Run Pipeline

```bash
python3 main.py
```

The pipeline writes outputs to `artifacts/`:

- `chunks.json`
- `retrieval.json`
- `answers.json`
- `eval.json`
- `grounding_check.json`
- `chunking_comparison.json`

LLM call metadata is appended to `llm_calls.jsonl`.

## Validate

```bash
python3 validate.py
```

Validation checks artifact existence, JSON validity, query coverage, retrieval quality, controlled labels, citation integrity, and aggregate metrics.

## API

Start the FastAPI server:

```bash
uvicorn api.app:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Ask a question:

```bash
curl -X POST http://127.0.0.1:8000/answer \
  -H "Content-Type: application/json" \
  -d '{"question": "Can I withdraw profit made on a demo account?"}'
```

## Phase Status

| Phase | Status |
| --- | --- |
| Phase 1: Document ingestion and chunking | Complete |
| Phase 2: TF-IDF retrieval | Complete |
| Phase 3: Citation-strict answer generation | Complete |
| Phase 4: Retrieval evaluation | Complete |
| Phase 5: Grounding check | Complete |
| Phase 6: Chunking comparison | Complete |
| FastAPI endpoint | Complete |
