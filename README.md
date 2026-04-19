# 🎓 AI Tutor — RAG-Powered Learning Platform

> **An intelligent tutoring system** that lets students upload educational PDFs and interact with their materials through grounded chat and AI-generated quizzes — with **zero hallucinations**.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 📄 **Document Ingestion** | Upload PDFs up to 50 MB; text is extracted, chunked, embedded, and indexed automatically. |
| 💬 **Grounded Chat** | Every answer is sourced strictly from your uploaded documents with `[Source N]` citations. |
| 🧠 **Two-Stage Retrieval** | Pinecone vector search followed by a Cross-Encoder reranker for maximum precision. |
| 📝 **AI Quiz Generator** | Evidence-based multiple-choice quizzes with verbatim quote evidence and answer hints. |
| 🔒 **Hallucination Guard** | If no document context is found the system refuses to answer — no fabricated content. |
| 🌊 **Token Streaming** | Real-time token-by-token response streaming via Server-Sent Events (SSE). |
| 💾 **Session Memory** | Conversational history is maintained per-session for multi-turn dialogue. |
| 🔌 **Multi-LLM Support** | Configurable: OpenRouter (default), Ollama (local), or HuggingFace models. |

---

## 🛠️ Tech Stack

### Backend (FastAPI)

| Layer | Technology | Details |
|---|---|---|
| **API Framework** | FastAPI | Async, type-checked, OpenAPI docs at `/docs` |
| **Vector Database** | Pinecone (Serverless) | 1536-dim Cosine index for semantic retrieval |
| **Embeddings** | `openai/text-embedding-3-small` via OpenRouter | Swappable to local `all-MiniLM-L6-v2` |
| **Reranker** | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Local Cross-Encoder for result precision |
| **LLM Provider** | OpenRouter | Default: `google/gemma-2-9b-it:free` |
| **Memory** | LangChain `ConversationBufferMemory` | Session-scoped, TTL-controlled |
| **PDF Processing** | PyPDF2 | Text extraction + LangChain RecursiveCharacterSplitter |
| **Keyword Index** | BM25 (rank-bm25) | Local per-document keyword index (available) |

### Frontend (Streamlit)
- **`app.py`** — Full Streamlit UI for document upload, chat, and quiz interaction.

---

## 📂 Project Structure

```text
AI-Tutor/
├── app.py                      # Streamlit Frontend
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/         # FastAPI route handlers
│   │   │       ├── chat.py     # POST /chat, GET /chat/history
│   │   │       ├── ingest.py   # POST /ingest/upload, /ingest/text
│   │   │       └── quiz.py     # POST /quiz/generate
│   │   ├── core/
│   │   │   └── config.py       # Pydantic Settings (reads .env)
│   │   ├── llm/
│   │   │   └── local_model.py  # LLM service (OpenRouter/Ollama/HF)
│   │   ├── memory/
│   │   │   └── session_memory.py  # Session-scoped conversation buffer
│   │   ├── rag/
│   │   │   ├── embeddings.py   # EmbeddingsService + Pinecone client
│   │   │   ├── retriever.py    # Two-stage retrieval orchestrator
│   │   │   ├── reranker.py     # Cross-Encoder reranking service
│   │   │   ├── pipeline.py     # End-to-end RAG pipeline
│   │   │   └── prompt_builder.py  # Strict grounding prompt templates
│   │   ├── services/
│   │   │   ├── chat_service.py    # Chat business logic
│   │   │   ├── ingestion_service.py  # PDF ingest + embed + upsert
│   │   │   └── quiz_service.py    # Quiz generation + JSON parsing
│   │   └── utils/
│   │       ├── bm25_manager.py    # BM25 keyword index manager
│   │       ├── chunking.py        # Text chunking utility
│   │       ├── logger.py          # Structured logging
│   │       └── pdf_processor.py   # PDF text extraction
│   ├── tests/                  # Automated test suite
│   ├── .env                    # Secrets & configuration
│   ├── .env.example            # Template for environment setup
│   └── requirements.txt        # Python dependencies
└── README.md
```

---

## 🚦 Quick Start

### 1. Clone & Set Up Environment

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate          # Windows
# source venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

Required variables:

```env
OPENROUTER_API_KEY=sk-or-...       # From openrouter.ai
PINECONE_API_KEY=pcsk_...          # From pinecone.io
PINECONE_INDEX_NAME=ai-tutor       # Must be 1536-dim, Cosine metric
LLM_PROVIDER=openrouter
EMBEDDING_PROVIDER=openrouter
```

### 3. Start the Backend

```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

API docs available at: `http://127.0.0.1:8001/docs`

### 4. Start the Frontend

In a **new terminal**:

```bash
streamlit run app.py
```

### 5. Verify End-to-End

```bash
cd backend
python test_tutor.py
```

---

## ⚙️ Configuration Reference

Key settings in `backend/.env`:

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `openrouter` | `openrouter` \| `ollama` \| `huggingface` |
| `OPENROUTER_MODEL` | `google/gemma-2-9b-it:free` | Any model on openrouter.ai |
| `EMBEDDING_PROVIDER` | `openrouter` | `openrouter` (cloud) \| `local` (CPU) |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Used when `EMBEDDING_PROVIDER=local` |
| `RETRIEVAL_TOP_K` | `20` | Candidates fetched from Pinecone |
| `RERANKER_TOP_K` | `10` | Top results after Cross-Encoder reranking |
| `CHUNK_SIZE` | `1000` | Characters per document chunk |
| `CHUNK_OVERLAP` | `200` | Character overlap between chunks |

---

> [!IMPORTANT]
> **Pinecone Index Setup:** Your Pinecone index **must** be configured with **384 dimensions** and **Cosine** similarity metric. This matches the `openai/text-embedding-3-small` embedding dimension used by default.

> [!TIP]
> **Local Mode:** Set `EMBEDDING_PROVIDER=local` and `LLM_PROVIDER=ollama` to run the entire stack offline with no API keys required.
