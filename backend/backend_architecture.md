# Backend Architecture - AI Tutor

The AI Tutor backend is a production-ready, RAG-focused FastAPI service that integrates multiple cloud and local components to provide a grounded educational experience.

## 💾 Core Infrastructure

### 1. Vector Database: Pinecone (Serverless)
- **Role:** High-performance similarity search for document chunks.
- **Metric:** Cosine Similarity.
- **Dimensions:** 1536 (Optimized for OpenAI `text-embedding-3-small`).
- **Isolation:** Uses metadata filtering (`source`) to isolate document contexts.

### 2. LLM Provider: OpenRouter
- **Role:** Unified API for world-class LLMs (Nemotron, GPT-4o, etc.).
- **Fallback:** Configured with local model definitions for robustness.
- **Streaming:** Token-by-token streaming enabled via SSE (Server-Sent Events).

### 3. Embeddings: OpenRouter / Local
- **Cloud:** `openai/text-embedding-3-small` for maximum accuracy.
- **Local:** `all-MiniLM-L6-v2` for low-latency testing (optional).

## 🧩 Component Architecture

| Component | Responsibility | Technical Tooling |
| :--- | :--- | :--- |
| **PDF Processor** | Extract & Clean text from PDF | `PyPDF2` |
| **Text Chunker** | Hierarchical / Overlap Splitting | `LangChain RecursiveCharacterSplitter` |
| **Ingestion Service** | Chunk -> Embed -> Pinecone Upsert | `app/services/ingestion_service.py` |
| **Retrieval Engine** | Semantic Search + Reranking | `Pinecone` + `Sentence-Transformers` |
| **Chat Service** | Conversational Logic & Memory | `LangChain ConversationBufferMemory` |
| **Quiz Generator** | Evidence-Based Question Creation | `Prompt Engineering` + `JSON Schema` |

---

## 🏗️ Folder Structure

```text
backend/
├── app/
│   ├── api/          # FastAPI Routes
│   ├── core/         # Settings & Environment
│   ├── rag/          # Embeddings, Retriever, Prompts
│   ├── services/     # Business logic (Quiz, Chat, Ingestion)
│   ├── memory/       # Session-based LangChain memory
│   └── utils/        # Logger, PDF Processor
├── tests/            # E2E scripts
├── venv/             # Python Virtual Env
├── .env              # Secrets & Keys
└── requirements.txt  # Project Dependencies
```
