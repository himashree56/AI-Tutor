# AI Tutor — Backend Architecture

A production-grade, RAG-focused **FastAPI** service that integrates Pinecone, OpenRouter, and local Sentence-Transformers to deliver hallucination-free educational responses.

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Streamlit Frontend                  │
│                     (app.py)                        │
└───────────────────────┬─────────────────────────────┘
                        │ HTTP / SSE
┌───────────────────────▼─────────────────────────────┐
│               FastAPI Application                    │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │  /ingest │  │    /chat     │  │ /quiz/generate │ │
│  └────┬─────┘  └──────┬───────┘  └───────┬────────┘ │
│       │               │                  │           │
│  ┌────▼──────┐  ┌─────▼────────┐  ┌─────▼────────┐  │
│  │Ingestion  │  │ RAG Pipeline │  │ Quiz Service  │  │
│  │Service    │  │              │  │               │  │
│  └────┬──────┘  └──────┬───────┘  └──────┬───────┘  │
└───────┼────────────────┼─────────────────┼──────────┘
        │                │                 │
        ▼                ▼                 ▼
   ┌─────────┐     ┌──────────┐     ┌──────────┐
   │Pinecone │     │Pinecone  │     │Pinecone  │
   │(Upsert) │     │(Query)   │     │(Query)   │
   └─────────┘     └────┬─────┘     └──────────┘
                        │
                   ┌────▼──────┐
                   │Cross-Enc. │
                   │Reranker   │
                   └────┬──────┘
                        │
                   ┌────▼──────┐
                   │  LLM      │
                   │(OpenRouter│
                   │ /Ollama)  │
                   └───────────┘
```

---

## 💾 Core Infrastructure

### 1. Vector Database — Pinecone (Serverless)
- **Role:** High-performance similarity search over document chunk embeddings.
- **Metric:** Cosine Similarity
- **Dimensions:** 1536 (matches `openai/text-embedding-3-small`)
- **Metadata:** Each vector stores `text`, `source`, `page`, and `chunk_index` for citation generation.

### 2. Embeddings — Dual-Provider
| Mode | Model | Use Case |
|---|---|---|
| `openrouter` (default) | `openai/text-embedding-3-small` | High accuracy, cloud API |
| `local` | `all-MiniLM-L6-v2` (Sentence-Transformers) | Offline / cost-free |

### 3. LLM Provider — OpenRouter
- **Default Model:** `google/gemma-2-9b-it:free`
- **Streaming:** Token-by-token via SSE (`stream_generate`)
- **Retry Logic:** Exponential backoff on rate-limit (HTTP 429) errors
- **Alternatives:** Ollama (local), HuggingFace Transformers (self-hosted)

### 4. Reranker — Cross-Encoder (Local)
- **Model:** `cross-encoder/ms-marco-MiniLM-L-6-v2`
- **Role:** Re-scores Pinecone candidates with a full-attention relevance model.
- **Threshold:** Scores ≥ -5.0 (logit space) are accepted to the final context window.

---

## 🧩 Component Architecture

| Component | Class / Module | Responsibility |
|:---|:---|:---|
| **PDF Processor** | `utils/pdf_processor.py` | Extracts text from PDF bytes via PyPDF2 |
| **Text Chunker** | `utils/chunking.py` | Splits text using `RecursiveCharacterTextSplitter` (1000 chars, 200 overlap) |
| **BM25 Manager** | `utils/bm25_manager.py` | Builds & persists per-document keyword indexes (BM25Okapi) |
| **Embeddings Service** | `rag/embeddings.py` | Generates vectors; owns the Pinecone client (upsert, query, delete) |
| **Reranker Service** | `rag/reranker.py` | Local Cross-Encoder re-scores candidate chunks |
| **Retriever Service** | `rag/retriever.py` | Orchestrates: Pinecone query → Reranker → `RetrievedChunk` list |
| **Prompt Builder** | `rag/prompt_builder.py` | Constructs strict grounding prompts and extracts source citations |
| **RAG Pipeline** | `rag/pipeline.py` | End-to-end: retrieve → prompt → LLM generate/stream → memory save |
| **Session Memory** | `memory/session_memory.py` | `ConversationBufferMemory` per session; TTL-controlled |
| **Chat Service** | `services/chat_service.py` | Business logic wrapper over RAG Pipeline |
| **Ingestion Service** | `services/ingestion_service.py` | PDF → chunks → embed → Pinecone upsert |
| **Quiz Service** | `services/quiz_service.py` | Topic → retrieval → LLM → JSON parse → `QuizResult` |
| **LLM Service** | `llm/local_model.py` | Unified client for OpenRouter / Ollama / HuggingFace |

---

## 📡 API Endpoints

All endpoints use **Pydantic Schema Validation** to prevent `422 Unprocessable Entity` errors.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/ingest/upload` | Upload a PDF file (multipart/form-data) |
| `POST` | `/ingest/text` | Ingest raw text with a source name |
| `GET` | `/ingest/stats` | Get total chunk count from Pinecone |
| `DELETE` | `/ingest/reset` | Delete all vectors in the Pinecone index |
| `POST` | `/chat` | Non-streaming RAG chat |
| `GET` | `/chat/stream` | SSE token-streaming RAG chat |
| `DELETE` | `/chat/history/{session_id}` | Clear conversation memory for a session |
| `POST` | `/quiz/generate` | Generate an evidence-based multiple-choice quiz |

---

## 🔑 Key Design Decisions

1. **Grounding First:** The LLM system prompt explicitly instructs the model to answer only from the provided context and to say "I don't know" when context is absent.
2. **Two-Stage Retrieval:** Pinecone retrieves `top_k=20` candidates; the Cross-Encoder re-scores them and returns only the top 10, dramatically reducing irrelevant context passed to the LLM.
3. **Pydantic Contracts:** Every API request and response uses strict Pydantic models, ensuring frontend ↔ backend schema compatibility.
4. **Lazy Initialization:** All heavy models (Sentence-Transformers, Cross-Encoder) are loaded on first use and cached in-process, keeping startup time fast.
5. **Quiz Resiliency:** The quiz parser multi-layer strategy: JSON extraction → trailing comma cleanup → markdown fallback parser, ensuring robust question parsing from any LLM output format.

---

## 🗂️ Folder Structure

```text
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── chat.py         # Chat endpoints
│   │       ├── ingest.py       # Ingestion endpoints
│   │       └── quiz.py         # Quiz endpoints
│   ├── core/
│   │   └── config.py           # Pydantic Settings (reads .env)
│   ├── llm/
│   │   └── local_model.py      # Multi-provider LLM client
│   ├── memory/
│   │   └── session_memory.py   # Per-session conversation buffer
│   ├── rag/
│   │   ├── embeddings.py       # Embedding + Pinecone CRUD
│   │   ├── retriever.py        # Retrieve + Rerank orchestrator
│   │   ├── reranker.py         # Cross-Encoder reranker
│   │   ├── pipeline.py         # Full RAG pipeline
│   │   └── prompt_builder.py   # Prompt templates + citation extractor
│   ├── services/
│   │   ├── chat_service.py
│   │   ├── ingestion_service.py
│   │   └── quiz_service.py
│   └── utils/
│       ├── bm25_manager.py     # BM25 keyword indexing (rank-bm25)
│       ├── chunking.py         # Text chunking
│       ├── logger.py           # Structured logging
│       └── pdf_processor.py    # PDF text extraction
├── tests/                      # Automated test suite (pytest)
├── data/
│   └── bm25/                   # Persisted per-document BM25 indexes
├── logs/                       # Application log files
├── .env                        # Secrets & runtime config
├── .env.example                # Config template
└── requirements.txt
```
