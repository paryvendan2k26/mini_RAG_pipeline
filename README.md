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


# 🔍 Mini-RAG Pipeline

> A production-style Retrieval-Augmented Generation pipeline that ingests a 
> knowledge base, retrieves relevant context, and generates citation-strict 
> answers — fully local, fully deterministic, fully auditable.

---

## What It Does

This pipeline answers user questions by finding relevant information from a 
knowledge base and generating grounded answers with citations. It never 
fabricates facts — if the context does not support an answer, it says so.

---

## Architecture

Write a clean pipeline flow diagram using markdown like this:

kb/ documents
     ↓
[INGEST] Parse titles, sections, chunk text
     ↓
[INDEX] TF-IDF vectorization
     ↓
[RETRIEVE] Cosine similarity top-3 chunks
     ↓
[GENERATE] LLM answer with citations
     ↓
[EVALUATE] Deterministic retrieval scoring
     ↓
[VALIDATE] Artifact integrity checks
     ↓
artifacts/ + API ready

---

## Pipeline Stages

| Stage | Description |
|---|---|
| INIT | Pipeline starts |
| DOCUMENTS_LOADED | KB files parsed |
| DOCUMENTS_CHUNKED | Text split into chunks |
| INDEX_BUILT | TF-IDF index ready |
| RETRIEVAL_COMPLETE | Top-3 chunks retrieved per query |
| ANSWERS_GENERATED | Grounded answers with citations |
| EVALUATION_COMPLETE | Hit rates computed |
| VALIDATION_COMPLETE | All artifacts verified |
| RESULTS_FINALISED | Pipeline done |

---

## Results

| Metric | Value |
|---|---|
| Documents | 4 |
| Chunks | 19 |
| Queries | 5 |
| Top-3 Hit Rate | 100% |
| Grounded Answers | 5/5 |
| Overall Grounded | 5/5 |
| Validation Checks | 7/7 PASSED |

---

## Quick Start

### 1. Clone and Install

git clone <repo-url>
cd mini-rag-pipeline
pip install -r requirements.txt

### 2. Set API Key

echo "GROQ_API_KEY=your_key_here" > .env

Get a free key at https://console.groq.com

### 3. Run Pipeline

python3 main.py

### 4. Validate

python3 validate.py

### 5. Start API

uvicorn api.app:app --reload

---

## API Usage

### POST /answer

Request:
{
  "question": "How long does a bank withdrawal take?"
}

Response:
{
  "answer_label": "grounded_answer",
  "answer": "Bank withdrawals may take 1 to 3 business days after approval. [Cash withdrawal processing §cash
