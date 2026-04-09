# Backend Architecture - AI Tutor

The AI Tutor backend is a production-ready, RAG-focused FastAPI service that integrates multiple cloud components to provide a grounded educational experience.

## 💾 Core Infrastructure

### 1. Vector Database: Pinecone (Serverless)
- **Role:** High-performance similarity search for document chunks.
- **Metric:** Cosine Similarity.
- **Dimensions:** 1536 (Optimized for OpenAI `text-embedding-3-small`).
- **Isolation:** Uses metadata filtering (`source`) to isolate document contexts for specific queries or quizzes.

### 2. LLM Provider: OpenRouter
- **Role:** Unified API for high-quality LLMs (Nemotron, GPT-4o, Claude, etc.).
- **Streaming:** Token-by-token streaming enabled via SSE (Server-Sent Events).
- **Control:** Temperature and max tokens are configurable per service (Chat vs Quiz).

### 3. Embeddings: OpenAI (via OpenRouter)
- **Model:** `openai/text-embedding-3-small` for consistent, high-accuracy semantic representation.

## 🧩 Component Architecture

| Component | Responsibility | Technical Tooling |
| :--- | :--- | :--- |
| **PDF Processor** | Extract & Clean text from PDF | `PyPDF2` |
| **Text Chunker** | Hierarchical / Overlap Splitting | `LangChain RecursiveCharacterSplitter` |
| **Ingestion Service** | Chunk -> Embed -> Pinecone Upsert | `app/services/ingestion_service.py` |
| **Retrieval Engine** | Semantic Search + Local Reranking | `Pinecone` + `Sentence-Transformers` |
| **Chat Service** | Conversational Logic & Memory | `LangChain ConversationBufferMemory` |
| **Quiz Generator** | Evidence-Based Question Creation | `Prompt Engineering` + `JSON Schema` |

## 📡 API Design

The backend enforces strict **Pydantic Schema Validation** for all primary endpoints:
- **Chat**: Receives a JSON body with `query` and `session_id`.
- **Quiz**: Receives a JSON body with `topic` or `context` and `num_questions`.

This synchronization ensures a robust contract between the frontend (Streamlit) and the backend (FastAPI), preventing "422 Unprocessable Entity" errors.

---

## 🏗️ Folder Structure

```text
backend/
├── app/
│   ├── api/          # FastAPI Routes (Chat, Ingest, Quiz)
│   ├── core/         # Settings & Environment Config
│   ├── rag/          # Embeddings, Retriever, Prompt Templates
│   ├── services/     # Business logic (Quiz, Chat, Ingestion)
│   ├── memory/       # Session-based memory management
│   └── utils/        # Logger, PDF Processor
├── tests/            # Automated test suite
├── venv/             # Python Virtual Environment
├── .env              # Secrets & Keys
└── requirements.txt  # Project Dependencies
```
