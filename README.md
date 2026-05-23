# Mini-RAG Pipeline


    ███╗   ███╗██╗███╗   ██╗██╗    ██████╗  █████╗  ██████╗
    ████╗ ████║██║████╗  ██║██║    ██╔══██╗██╔══██╗██╔════╝
    ██╔████╔██║██║██╔██╗ ██║██║    ██████╔╝███████║██║  ███╗
    ██║╚██╔╝██║██║██║╚██╗██║██║    ██╔══██╗██╔══██║██║   ██║
    ██║ ╚═╝ ██║██║██║ ╚████║██║    ██║  ██║██║  ██║╚██████╔╝
    ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝

          P  I  P  E  L  I  N  E


                 [ find it. cite it. never fake it. ]


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


  "The retrieval shall speak first.
   The answer shall not come before the evidence.
   And the evidence shall cite its origin
   or it shall not be spoken at all."

                                        -- The Pipeline Constitution


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


# Mini-RAG Pipeline

> A compact, end-to-end Retrieval-Augmented Generation pipeline for support-style knowledge base answers, built in Python with TF-IDF retrieval, citation-strict LLM generation, grounding checks, evaluation, chunking comparison, and a FastAPI serving layer.

---

## Table Of Contents

- [Overview](#overview)
- [What This Project Does](#what-this-project-does)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Run The Pipeline](#run-the-pipeline)
- [Artifacts](#artifacts)
- [Validation](#validation)
- [API](#api)
- [Phase Status](#phase-status)
- [Implementation Notes](#implementation-notes)
- [Troubleshooting](#troubleshooting)

---

## Overview

Mini-RAG Pipeline is a small but complete RAG system designed around a local support knowledge base. It demonstrates the full lifecycle of a RAG workflow: document ingestion, chunking, retrieval, answer generation, evaluation, grounding validation, chunking strategy comparison, and API serving.

The project is intentionally lightweight. Retrieval uses `scikit-learn` TF-IDF vectors instead of an external vector database, and generated answers are forced to cite retrieved chunks using strict citation formatting.

---

## What This Project Does

| Capability | Description |
| --- | --- |
| Document ingestion | Loads `.txt` knowledge base articles from `kb/` using `pathlib.Path`. |
| Chunking | Supports sentence chunks and fixed-size overlapping chunks. |
| Retrieval | Builds a TF-IDF index and retrieves top-k chunks by cosine similarity. |
| Answer generation | Uses Groq chat completions to generate citation-strict answers. |
| Citation parsing | Extracts citations in `[doc_title §chunk_id]` format. |
| Evaluation | Measures whether expected document titles appear in the top 3 retrieved chunks. |
| Grounding check | Verifies citations point to retrieved chunks and have keyword overlap. |
| Chunking comparison | Compares sentence chunking against fixed-size chunking. |
| Validation | Checks artifacts, JSON validity, query coverage, labels, citations, and aggregate metrics. |
| API | Provides `/health` and `/answer` endpoints with FastAPI. |

---

## Architecture

```text
kb/*.txt
   |
   v
Document ingestion
   |
   v
Chunking
   |
   v
artifacts/chunks.json
   |
   v
TF-IDF retrieval
   |
   v
artifacts/retrieval.json
   |
   v
Groq answer generation
   |
   v
artifacts/answers.json
   |
   +--------------------+
   |                    |
   v                    v
Evaluation          Grounding check
   |                    |
   v                    v
artifacts/eval.json artifacts/grounding_check.json
   |
   v
Chunking comparison
   |
   v
artifacts/chunking_comparison.json
```

The main script orchestrates the full pipeline through explicit state transitions:

```text
INIT
DOCUMENTS_LOADED
DOCUMENTS_CHUNKED
INDEX_BUILT
RETRIEVAL_COMPLETE
ANSWERS_GENERATED
EVALUATION_COMPLETE
VALIDATION_COMPLETE
RESULTS_FINALISED
```

---

## Project Structure

```text
mini-rag-pipeline/
├── api/
│   ├── __init__.py
│   └── app.py
├── artifacts/
│   └── .gitkeep
├── kb/
│   ├── article_01.txt
│   ├── article_02.txt
│   ├── article_03.txt
│   └── article_04.txt
├── pipeline/
│   ├── __init__.py
│   ├── chunking_comparison.py
│   ├── evaluate.py
│   ├── generate.py
│   ├── grounding.py
│   ├── ingest.py
│   ├── retrieval.py
│   └── state.py
├── .env
├── .gitignore
├── main.py
├── queries.json
├── README.md
├── requirements.txt
└── validate.py
```

---

## Setup

### 1. Install dependencies

Python 3.11+ is recommended.

```bash
pip install -r requirements.txt
```

### 2. Configure your API key

Create or update `.env` in the project root:

```bash
GROQ_API_KEY=your_groq_key_here
```

The key is loaded with `python-dotenv` and is never hardcoded in source code.

---

## Run The Pipeline

Run the complete pipeline:

```bash
python3 main.py
```

This performs:

1. Document loading
2. Sentence chunking
3. TF-IDF retrieval
4. Groq answer generation
5. Retrieval evaluation
6. Grounding checks
7. Chunking comparison
8. Final pipeline state completion

Expected final message:

```text
[DONE] Pipeline complete. Run 'python3 validate.py' to validate.
```

---

## Artifacts

The pipeline writes structured JSON outputs into `artifacts/`.

| Artifact | Purpose |
| --- | --- |
| `artifacts/chunks.json` | All generated chunks from the knowledge base. |
| `artifacts/retrieval.json` | Top-k retrieved chunks for each query. |
| `artifacts/answers.json` | Generated answers, labels, citations, and used chunk IDs. |
| `artifacts/eval.json` | Per-query retrieval evaluation plus aggregate metrics. |
| `artifacts/grounding_check.json` | Citation validity and grounding checks. |
| `artifacts/chunking_comparison.json` | Sentence vs fixed chunking comparison. |
| `llm_calls.jsonl` | Append-only metadata log for LLM calls. |

Example answer record:

```json
{
  "query_id": "Q1",
  "answer_label": "grounded_answer",
  "answer": "Bank withdrawals may take 1 to 3 business days after approval. [Cash withdrawal processing §cash-withdrawal-processing_s1]",
  "citations": ["[Cash withdrawal processing §cash-withdrawal-processing_s1]"],
  "used_chunk_ids": ["cash-withdrawal-processing_s1"]
}
```

---

## Validation

Run:

```bash
python3 validate.py
```

Validation checks:

| Check | What It Verifies |
| --- | --- |
| Artifacts exist | Required output files are present. |
| JSON validity | Artifact files parse as valid JSON. |
| Query coverage | All 5 queries were processed. |
| Retrieval quality | Each query has at least 3 retrieved chunks with numeric scores. |
| Controlled vocabulary | Labels and retrieval statuses use approved values. |
| Citation integrity | Grounded answers cite chunks from retrieved context. |
| Aggregate summary | Evaluation metrics are present. |

Successful output:

```text
PASS: ARTIFACTS EXIST
PASS: JSON VALIDITY
PASS: ALL QUERIES PROCESSED
PASS: RETRIEVAL QUALITY
PASS: CONTROLLED VOCABULARY
PASS: CITATION INTEGRITY
PASS: AGGREGATE SUMMARY
PASSED: 7 checks
FAILED: 0 checks
```

---

## API

Start the server:

```bash
uvicorn api.app:app --reload
```

### Health Check

```bash
curl http://127.0.0.1:8000/health
```

Response:

```json
{
  "status": "ok",
  "pipeline": "mini-rag"
}
```

### Ask A Question

```bash
curl -X POST http://127.0.0.1:8000/answer \
  -H "Content-Type: application/json" \
  -d '{"question": "Can I withdraw profit made on a demo account?"}'
```

Response shape:

```json
{
  "answer_label": "grounded_answer",
  "answer": "Demo profit cannot be withdrawn. [Demo account behaviour §demo-account-behaviour_s2]",
  "citations": ["[Demo account behaviour §demo-account-behaviour_s2]"]
}
```

---

## Phase Status

| Phase | Status | Output |
| --- | --- | --- |
| Phase 1: Document ingestion and chunking | Complete | `artifacts/chunks.json` |
| Phase 2: TF-IDF retrieval | Complete | `artifacts/retrieval.json` |
| Phase 3: Citation-strict answer generation | Complete | `artifacts/answers.json` |
| Phase 4: Retrieval evaluation | Complete | `artifacts/eval.json` |
| Phase 5: Grounding check | Complete | `artifacts/grounding_check.json` |
| Phase 6: Chunking comparison | Complete | `artifacts/chunking_comparison.json` |
| FastAPI endpoint | Complete | `/health`, `/answer` |

---

## Implementation Notes

### Chunking

The project supports two chunking strategies:

| Strategy | Behavior |
| --- | --- |
| `sentence` | Splits each document body into sentence-level chunks. |
| `fixed` | Splits body text into 200-character chunks with 20-character overlap. |

The main pipeline uses sentence chunking by default. Chunking comparison evaluates both strategies without overwriting the main `chunks.json` or `retrieval.json` artifacts.

### Retrieval

Retrieval is implemented with:

- `TfidfVectorizer(stop_words="english")`
- `cosine_similarity`
- Top-k ranking by descending similarity score

Each retrieved item includes:

```json
{
  "rank": 1,
  "chunk_id": "demo-account-behaviour_s2",
  "doc_title": "Demo account behaviour",
  "score": 0.6673,
  "chunk_text": "Demo profit cannot be withdrawn"
}
```

### Answer Labels

Generated answers use a controlled vocabulary:

| Label | Meaning |
| --- | --- |
| `grounded_answer` | The answer uses retrieved context and citations. |
| `insufficient_context` | The context does not contain enough relevant information. |
| `conflicting_context` | Reserved for future conflict detection. |

### Citation Format

Every factual claim should use this citation format:

```text
[doc_title §chunk_id]
```

Example:

```text
[Password reset and account recovery §password-reset-and-account-recovery_s1]
```

---

## Troubleshooting

### `GROQ_API_KEY` error

Make sure `.env` exists and contains:

```bash
GROQ_API_KEY=your_real_key_here
```

### Missing artifacts

Run the full pipeline first:

```bash
python3 main.py
```

Then validate:

```bash
python3 validate.py
```

### API cannot answer

The API expects `artifacts/chunks.json` to exist. Run the pipeline or at least the ingestion phase before starting the server.

### Validation fails citation integrity

Regenerate answers with a valid LLM key. The validator expects every `grounded_answer` to cite retrieved chunks using the exact `[doc_title §chunk_id]` format.

---

## License

This project is intended as an educational mini-RAG pipeline scaffold.
