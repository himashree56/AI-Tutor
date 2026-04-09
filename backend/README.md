# AI Tutor Backend

A production-ready RAG-based AI Tutor with cloud-scale search powered by FastAPI, Pinecone, and OpenRouter.

## Features

- **PDF Ingestion**: Upload and process PDF documents with metadata tracking.
- **RAG Pipeline**: Advanced semantic search with vector embeddings and reranking.
- **Cloud LLM**: Integration with OpenRouter for state-of-the-art models (GPT-4, Nemotron, etc.).
- **Streaming Responses**: Token-by-token streaming via Server-Sent Events (SSE).
- **Session Memory**: Persistent conversation history per session using LangChain.
- **Quiz Generation**: Auto-generate MCQs with evidence quotes directly from your documents.
- **Source Filtering**: Ground your queries or quizzes in specific uploaded documents.
- **Evaluation Metrics**: Built-in faithfulness and relevance scoring for responses.

## Tech Stack

| Component | Technology |
|-----------|------------|
| API Framework | FastAPI |
| Vector Database | Pinecone (Serverless) |
| Embeddings | OpenAI `text-embedding-3-small` (via OpenRouter) |
| LLM Provider | OpenRouter |
| Reranking | Sentence-Transformers (Local) |
| PDF Processing | PyPDF2 |
| Chunking | LangChain RecursiveCharacterTextSplitter |

## Prerequisites

### 1. Python 3.10+
```bash
python --version  # >= 3.10
```

### 2. API Keys
You will need:
- **Pinecone**: [Get a free API key](https://app.pinecone.io/)
- **OpenRouter**: [Get an API key](https://openrouter.ai/)

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the `backend/` directory:

```env
# Cloud Providers
OPENROUTER_API_KEY=your_openrouter_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=ai-tutor

# Retrieval Settings
RETRIEVAL_TOP_K=10
RERANKER_TOP_K=3

# Quiz Settings
QUIZ_NUM_QUESTIONS=5
QUIZ_TEMPERATURE=0.7
```

> [!IMPORTANT]
> **Pinecone Index Configuration:**
> - **Dimension:** 1536
> - **Metric:** Cosine

## Running the Server

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

## API Endpoints

### Ingestion

```bash
# Upload PDF
POST /ingest/upload
Content-Type: multipart/form-data
file: <pdf_file>

# Get collection stats
GET /ingest/stats

# Reset collection
DELETE /ingest/reset
```

### Chat (JSON Body)

```bash
# Non-streaming chat
POST /chat/
Content-Type: application/json
{
    "query": "What is the main topic?",
    "session_id": "user_123",
    "top_k": 5
}

# Streaming chat
POST /chat/stream
Content-Type: application/json
{
    "query": "Explain the concept of RAG",
    "session_id": "user_123"
}

# History
GET /chat/history/{session_id}
DELETE /chat/history/{session_id}
```

### Quiz (JSON Body)

```bash
# Generate quiz
POST /generate-quiz/
Content-Type: application/json
{
    "topic": "machine learning",
    "num_questions": 3
}

# Or from specific context/source
POST /generate-quiz/
{
    "context": "Context extracted from a specific document...",
    "num_questions": 5
}
```

## Project Structure

```text
backend/
├── app/
│   ├── api/          # FastAPI Routes (Chat, Ingest, Quiz)
│   ├── core/         # Settings & Config
│   ├── rag/          # RAG Pipeline, Retriever, Prompts
│   ├── services/     # Business logic
│   ├── memory/       # Session-based history
│   └── utils/        # Logger, PDF Processing
├── tests/            # Automated tests
└── requirements.txt
```

## Testing

```bash
pytest tests/ -v
```

## License

MIT License
