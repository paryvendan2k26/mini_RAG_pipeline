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


## What This Is

A machine that reads, retrieves, and answers -- but only from what
it actually knows. No guessing. No hallucination. No fabrication.

You give it a knowledge base. It indexes every sentence. When a
question arrives, it finds the three most relevant chunks, hands
them to a language model, and says: answer only from these. Cite
every fact. If the context does not support the answer, say so.

That is the whole contract.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


## The Journey of a Question

A question walks in through the door.
It does not know what it will find.

  USER QUESTION
      "How long does a bank withdrawal take?"
           |
           v
  TF-IDF INDEX  <---  19 text chunks from 4 articles
           |
           |   cosine similarity across all chunks
           |   top 3 rise to the surface
           |
           v
  RETRIEVED CHUNKS
      rank 1: 0.5108   "Bank withdrawals may take 1 to 3 business days."
      rank 2: 0.3201
      rank 3: 0.2847
           |
           |   handed to the language model with strict instructions
           |
           v
  LANGUAGE MODEL
      "Answer only from the context above.
       Cite every fact. Format: [title §chunk_id]
       If unsure, say insufficient_context."
           |
           v
  GROUNDED ANSWER
      "Bank withdrawals may take 1 to 3 business days after approval.
       [Cash withdrawal processing §cash-withdrawal-processing_s1]"
           |
           v
  EVALUATOR  --  was the right document retrieved?
  GROUNDING  --  is the citation real?
  VALIDATOR  --  did all 7 checks pass?

The question got its answer.
It knew exactly where it came from.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


## The Nine States

  Every run of this pipeline passes through nine gates.
  No gate may be skipped. No gate may be visited twice.
  Attempt to jump ahead and the machine will refuse you.

       o
       |
       |   INIT
       |   the machine wakes
       v
    DOCUMENTS_LOADED
       |   four articles read from disk
       |   titles and sections parsed
       v
    DOCUMENTS_CHUNKED
       |   nineteen sentences extracted
       |   each one a retrievable unit
       v
    INDEX_BUILT
       |   TF-IDF vectors computed
       |   the index is ready
       v
    RETRIEVAL_COMPLETE
       |   top three chunks found per query
       |   scores assigned, ranked, saved
       v
    ANSWERS_GENERATED
       |   language model called once per query
       |   citations enforced, labels controlled
       v
    EVALUATION_COMPLETE
       |   hit rates computed deterministically
       |   no LLM involved in scoring
       v
    VALIDATION_COMPLETE
       |   seven integrity checks run
       |   artifacts verified, vocabulary checked
       v
    RESULTS_FINALISED
       |
       o   done.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


## Results

  Documents loaded          4          pass
  Chunks created            19         pass
  Queries answered          5 of 5     pass
  Top-3 retrieval hit rate  100%       pass
  Grounded answers          5 of 5     pass
  Citation integrity        5 of 5     pass
  Validation checks passed  7 of 7     pass

  All five queries retrieved the correct document at rank one.
  All five answers cited real chunks from the retrieved context.
  Zero hallucinations. Zero fabrications. Zero missed citations.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


## Project Map

  mini-rag-pipeline/
  |
  |-- kb/                         the knowledge base lives here
  |   |-- article_01.txt          password reset and account recovery
  |   |-- article_02.txt          cash withdrawal processing
  |   |-- article_03.txt          document verification requirements
  |   `-- article_04.txt          demo account behaviour
  |
  |-- pipeline/                   the engine room
  |   |-- state.py                nine stages, strict ordering
  |   |-- ingest.py               parse, chunk, save
  |   |-- retrieval.py            tfidf index, cosine similarity
  |   |-- generate.py             llm calls, citation parsing
  |   |-- evaluate.py             deterministic scoring
  |   |-- grounding.py            citation validity checks
  |   `-- chunking_comparison.py  sentence vs fixed strategy
  |
  |-- api/
  |   `-- app.py                  POST /answer   GET /health
  |
  |-- artifacts/                  everything the pipeline writes
  |   |-- chunks.json
  |   |-- retrieval.json
  |   |-- answers.json
  |   |-- eval.json
  |   |-- grounding_check.json
  |   `-- chunking_comparison.json
  |
  |-- main.py                     runs the whole pipeline top to bottom
  |-- validate.py                 seven checks, exits 0 or 1
  |-- queries.json                five test questions with ground truth
  |-- llm_calls.jsonl             one audit record per llm call
  |-- requirements.txt
  |-- .env                        api keys  --  never commit this
  `-- README.md


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


## Quick Start

  // step one -- get the code

  git clone <repo-url>
  cd mini-rag-pipeline
  pip install -r requirements.txt


  // step two -- add your key
  //             free tier at console.groq.com

  echo "GROQ_API_KEY=your_key_here" > .env


  // step three -- run everything

  python3 main.py


  // step four -- verify everything

  python3 validate.py

  > PASS: ARTIFACTS EXIST
  > PASS: JSON VALIDITY
  > PASS: ALL QUERIES PROCESSED
  > PASS: RETRIEVAL QUALITY
  > PASS: CONTROLLED VOCABULARY
  > PASS: CITATION INTEGRITY
  > PASS: AGGREGATE SUMMARY
  > PASSED: 7 checks
  > FAILED: 0 checks


  // step five -- start the api

  uvicorn api.app:app --reload


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


## API

  /*
   *  POST /answer
   *
   *  send a question.
   *  get a grounded answer back.
   *  with citations.
   *  always with citations.
   */

  curl -X POST http://localhost:8000/answer \
    -H "Content-Type: application/json" \
    -d '{"question": "How long does a bank withdrawal take?"}'

  {
    "answer_label": "grounded_answer",
    "answer": "Bank withdrawals may take 1 to 3 business days after approval.
               [Cash withdrawal processing §cash-withdrawal_s1]",
    "citations": ["[Cash withdrawal processing §cash-withdrawal_s1]"]
  }


  /*
   *  GET /health
   */

  curl http://localhost:8000/health

  { "status": "ok", "pipeline": "mini-rag" }


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


## The Three Laws of This Pipeline

  I.    An answer may not cite a chunk that was not retrieved.

  II.   An answer must cite at least one chunk or declare itself
        insufficient_context.

  III.  The evaluation must be deterministic code.
        The LLM may not score itself.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


## Controlled Vocabularies

  answer labels          retrieval statuses
  ─────────────          ──────────────────
  grounded_answer        hit
  insufficient_context   partial_hit
  conflicting_context    miss

  citation format
  ───────────────
  [doc_title §chunk_id]

  example:
  [Cash withdrawal processing §cash-withdrawal-processing_s1]


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


## Chunking Strategies Compared

  sentence-based                    fixed-size
  ──────────────                    ──────────
  one chunk per sentence            200 characters per chunk
  natural language boundaries       20 character overlap
  19 chunks                         varies by document
  hit rate: 100%                    hit rate: 100%

  verdict: tie on this knowledge base.
           sentence chunking preferred for citation clarity.
           fixed-size preferred when documents have no punctuation.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


## Requirements

  scikit-learn    >=1.4.0     tfidf and cosine similarity
  groq            >=0.9.0     llm inference, free tier
  fastapi         >=0.111.0   api server
  uvicorn         >=0.29.0    asgi runner
  jsonlines       >=4.0.0     llm call audit log
  python-dotenv   >=1.0.0     api key loading


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


  built to be replaced.
  the kb/ folder can be swapped.
  the queries.json can be swapped.
  the llm can be swapped.

  the pipeline stays the same.
  the citations stay enforced.
  the validation stays green.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                              MIT License

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
