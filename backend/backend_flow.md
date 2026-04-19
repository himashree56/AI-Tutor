# AI Tutor — System Flow Diagrams

Detailed flow diagrams for every major operation in the AI Tutor platform. Each diagram traces the exact path data takes through the system — from raw user input to a grounded, AI-generated response.

---

## 📥 Flow 1: Document Ingestion (PDF → Pinecone)

Describes how an uploaded PDF is transformed into searchable vector embeddings.

```mermaid
flowchart TD
    A([🖥️ Streamlit Frontend]) -->|POST /ingest/upload\nmultipart/form-data| B[FastAPI Ingest Route]
    B --> C{Valid PDF?\n≤ 50 MB?}
    C -->|No| ERR1([❌ HTTP 400 Bad Request])
    C -->|Yes| D[IngestionService]

    D --> E[PDF Processor\nPyPDF2]
    E -->|Extracted raw text| F[Text Chunker\nRecursiveCharacterTextSplitter\nchunk_size=1000, overlap=200]
    F -->|List of chunk dicts\nid · text · metadata| G{Chunks\nExtracted?}
    G -->|None| ERR2([❌ No text extracted])
    G -->|Yes| H[EmbeddingsService\nembed_texts]

    H -->|OpenRouter API\nopenai/text-embedding-3-small| I[1536-dim Float Vectors]
    I --> J[Delete stale Pinecone vectors\nfilter by source name]
    J --> K[Pinecone Upsert\nbatch_size=100\nid · values · metadata]
    K --> L([✅ chunks_added: N\nsource: filename])

    style A fill:#4f46e5,color:#fff
    style L fill:#16a34a,color:#fff
    style ERR1 fill:#dc2626,color:#fff
    style ERR2 fill:#dc2626,color:#fff
```

**Key steps:**
1. File validation (PDF only, ≤ 50 MB)
2. Text extraction per page with page-number metadata attached
3. Recursive character splitting with 200-char overlap for context continuity
4. Cloud embedding via OpenRouter (or local via Sentence-Transformers)
5. Atomic upsert — old chunks for the same source are deleted first

---

## 💬 Flow 2: Grounded RAG Chat (Query → Streamed Answer)

Describes the two-stage retrieval and generation pipeline for user questions.

```mermaid
flowchart TD
    A([🖥️ User Question]) -->|POST /chat\nor GET /chat/stream| B[FastAPI Chat Route]
    B --> C[ChatService]
    C --> D[RAG Pipeline]

    D --> D1[Load Session Memory\nConversationBuffer]
    D --> E[EmbeddingsService\nembed_query]
    E -->|1536-dim query vector| F[Pinecone Query\ntop_k = 20 candidates]

    F -->|Raw matches\n+ cosine scores| G{Results\nFound?}
    G -->|None| EMPTY([⚠️ No context —\nRefusal response])
    G -->|Yes| H[RerankerService\ncross-encoder/ms-marco-MiniLM-L-6-v2]

    H -->|Logit scores per pair\nquery × each chunk| I[Sort by score\nKeep top-K ≥ -5.0]
    I --> J[Prompt Builder\nStrict grounding template]
    D1 -->|Prior turns| J

    J -->|System prompt:\n'Use only provided context'| K[LLM — OpenRouter\ngoogle/gemma-2-9b-it:free]
    K -->|Streaming tokens\nvia SSE| L[Accumulate full response]
    L --> M[Save to Session Memory\nuser turn + assistant turn]
    M --> N([✅ Grounded answer\nwith Source citations])

    style A fill:#4f46e5,color:#fff
    style N fill:#16a34a,color:#fff
    style EMPTY fill:#d97706,color:#fff
```

**Key steps:**
1. Query is embedded using the same model as ingestion (embedding space consistency)
2. Pinecone returns the 20 closest chunks by cosine similarity
3. Cross-Encoder reranker re-scores all 20 pairs with full attention — no hallucination shortcut
4. Only chunks with reranker logit ≥ -5.0 pass to the prompt
5. A strict system prompt forbids the LLM from going beyond the provided context
6. Response is streamed token-by-token (SSE) and saved to session memory

---

## 📝 Flow 3: AI Quiz Generation (Topic → JSON Quiz)

Describes how a grounded, evidence-backed quiz is created from document content.

```mermaid
flowchart TD
    A([🖥️ Quiz Request\ntopic + num_questions]) -->|POST /quiz/generate| B[FastAPI Quiz Route]
    B --> C[QuizService]

    C --> D{Context\nProvided Directly?}
    D -->|Yes| F
    D -->|No — use topic| E[RetrieverService\ntop_k semantic search]
    E -->|Chunks + metadata| F{Context\nNon-empty?}

    F -->|No| REFUSE([⚠️ Refusal\n'No content found for topic'])
    F -->|Yes| G[Prompt Builder\nbuild_quiz_prompt\nStrict JSON schema]

    G -->|System: JSON only\nno commentary| H[LLM — OpenRouter]
    H -->|Raw LLM output| I[Multi-Layer JSON Parser]

    I --> I1{Has markdown\ncode block?}
    I1 -->|Yes| I2[Strip fences\nextract JSON substring]
    I1 -->|No| I3[Regex search for\n questions block]
    I2 --> I4[Clean trailing\ncommas]
    I3 --> I4
    I4 --> I5{JSON\ndecodable?}
    I5 -->|Yes| J[Validate each question\nNormalize answer to A-D]
    I5 -->|No| I6[Fallback: Markdown\nblock parser]
    I6 --> J

    J --> K([✅ QuizResult\nquestions · options · answer\nevidence_quote · hint])

    style A fill:#4f46e5,color:#fff
    style K fill:#16a34a,color:#fff
    style REFUSE fill:#d97706,color:#fff
```

**Key steps:**
1. If only a `topic` is provided, the quiz service calls the retriever to build context
2. If retrieval returns empty context the system refuses — no questions are generated from thin air
3. A strict prompt instructs the LLM to output **only** a JSON object with `questions[]`
4. The parser runs a 4-stage extraction strategy to handle any LLM output quirks
5. Answer normalization ensures the `answer` field is always a clean `A/B/C/D`

---

## 🔄 Cross-Cutting Concerns

```mermaid
flowchart LR
    ALL[Every Request] --> LOG[Structured Logger\napp/utils/logger.py]
    ALL --> VAL[Pydantic Validation\n422 on schema mismatch]
    ALL --> ERR[Exception Handlers\nHTTP 500 with detail]

    CHAT[Chat Requests] --> MEM[Session Memory\nmax 10 turns per session\nTTL = 3600s]
    LLM[LLM Calls] --> RETRY[Exponential Backoff\non HTTP 429 rate limits]
```

---

## ✅ Core Grounding Principles

| Principle | Implementation |
|---|---|
| **No Fabrication** | LLM system prompt: "Answer ONLY from the context below. If unsure, say 'I don't know'." |
| **Evidence Required** | Quiz questions must include a `evidence_quote` directly from the source PDF |
| **Refusal Logic** | Empty retrieval result → immediate refusal before any LLM call |
| **Source Citations** | Every chat answer includes `[Source N] (Page P, filename)` references |
| **Schema Contracts** | Pydantic enforces exact JSON structures for all API requests and responses |
| **Stale-Safe Ingestion** | Re-uploading a document first deletes all previous chunks for that source |
