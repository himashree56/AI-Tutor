# AI Tutor Backend

A production-ready RAG-based AI Tutor with fully local LLM support using FastAPI, ChromaDB, and Ollama.

## Features

- **PDF Ingestion**: Upload and process PDF documents
- **RAG Pipeline**: Semantic search with vector embeddings
- **Local LLM**: Run Mistral/LLaMA locally via Ollama
- **Streaming Responses**: SSE-based token streaming
- **Session Memory**: Conversation history per session
- **Quiz Generation**: Auto-generate MCQs from content
- **Evaluation Metrics**: Faithfulness and relevance scoring
- **Cross-Encoder Reranking**: Improved retrieval quality

## Tech Stack

| Component | Technology |
|-----------|------------|
| API Framework | FastAPI |
| Vector Database | ChromaDB |
| Embeddings | SentenceTransformers |
| LLM | Ollama (Mistral/LLaMA) |
| Reranking | Cross-Encoder |
| PDF Processing | PyMuPDF |
| Chunking | LangChain RecursiveCharacterTextSplitter |

## Prerequisites

### 1. Python 3.10+

```bash
python --version  # >= 3.10
```

### 2. Ollama

Install Ollama for your platform:

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from https://ollama.com/download

### 3. Pull LLM Model

```bash
ollama pull mistral
# or
ollama pull llama2
```

### 4. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the `backend/` directory:

```bash
cp .env.example .env
```

Key settings in `.env`:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
OLLAMA_TEMPERATURE=0.7

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# ChromaDB
CHROMA_PERSIST_DIR=./data/chroma_db

# Retrieval
RETRIEVAL_TOP_K=20
RERANKER_TOP_K=10

# Chunking
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## Running the Server

### Start Ollama (in separate terminal)

```bash
ollama serve
```

### Start the API Server

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or:

```bash
cd backend
python -m app.main
```

## API Endpoints

### Health Check

```bash
GET /
GET /health
```

### Ingestion

```bash
# Upload PDF
POST /ingest/upload
Content-Type: multipart/form-data
file: <pdf_file>

# Ingest text directly
POST /ingest/text
{
    "text": "Your educational content here",
    "source_name": "custom_source"
}

# Get collection stats
GET /ingest/stats

# Reset collection
DELETE /ingest/reset
```

### Chat

```bash
# Non-streaming chat
POST /chat/?query=What is Python?&session_id=abc123

# Streaming chat
POST /chat/stream?query=What is Python?&session_id=abc123

# Get conversation history
GET /chat/history/{session_id}

# Clear conversation history
DELETE /chat/history/{session_id}
```

### Quiz

```bash
# Generate quiz from topic
POST /quiz/
{
    "topic": "machine learning",
    "num_questions": 5
}

# Or from specific context
POST /quiz/
{
    "context": "Your educational content...",
    "num_questions": 5
}
```

## Example Usage

### 1. Upload a PDF

```bash
curl -X POST "http://localhost:8000/ingest/upload" \
  -F "file=@/path/to/your/document.pdf"
```

### 2. Ask Questions

```bash
curl -X POST "http://localhost:8000/chat/?query=Explain the main topic&session_id=session1"
```

### 3. Stream Response

```bash
curl -N -X POST "http://localhost:8000/chat/stream?query=Explain the main topic&session_id=session1"
```

### 4. Generate Quiz

```bash
curl -X POST "http://localhost:8000/quiz/" \
  -H "Content-Type: application/json" \
  -d '{"topic": "your topic", "num_questions": 5}'
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── api/
│   │   ├── routes/          # API endpoints
│   │   │   ├── ingest.py    # Ingestion endpoints
│   │   │   ├── chat.py      # Chat endpoints
│   │   │   └── quiz.py      # Quiz endpoints
│   │   └── dependencies.py  # Dependency injection
│   ├── core/
│   │   └── config.py        # Settings management
│   ├── rag/
│   │   ├── pipeline.py      # RAG orchestration
│   │   ├── embeddings.py    # Embedding service
│   │   ├── retriever.py     # Retrieval logic
│   │   ├── reranker.py      # Cross-encoder reranking
│   │   └── prompt_builder.py # Prompt templates
│   ├── llm/
│   │   └── local_model.py   # Ollama/HuggingFace abstraction
│   ├── memory/
│   │   └── session_memory.py # Session management
│   ├── services/
│   │   ├── ingestion_service.py
│   │   ├── chat_service.py
│   │   └── quiz_service.py
│   ├── evaluation/
│   │   └── metrics.py       # Evaluation metrics
│   └── utils/
│       ├── logger.py        # Logging setup
│       ├── chunking.py       # Text chunking
│       └── pdf_processor.py  # PDF text extraction
├── tests/                   # Unit tests
├── requirements.txt
├── .env.example
└── README.md
```

## Testing

```bash
cd backend
pytest tests/ -v
```

## Alternative: HuggingFace Local Model

If you prefer not to use Ollama, you can switch to HuggingFace Transformers:

```env
USE_OLLAMA=false
HF_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2
HF_DEVICE_MAP=auto
```

Note: This requires significant GPU memory (7B+ model needs ~14GB VRAM).
267: 
268: ## Using OpenRouter (Cloud LLM)
269: 
270: If you want better performance without local RAM constraints, you can use OpenRouter:
271: 
272: 1. Get an API key at [openrouter.ai](https://openrouter.ai)
273: 2. Update your `.env`:
274:    ```env
275:    LLM_PROVIDER=openrouter
276:    OPENROUTER_API_KEY=your_key_here
277:    OPENROUTER_MODEL=mistralai/mistral-7b-instruct:free
278:    ```
279: 
280: OpenRouter offers many **completely free** models that are more intelligent than the smallest local models.

## Performance Tips

1. **GPU Acceleration**: Ensure CUDA is available for faster inference
2. **Batch Processing**: Adjust `EMBEDDING_BATCH_SIZE` based on RAM
3. **Chunk Size**: Tune `CHUNK_SIZE` for your document types
4. **Retrieval K**: Adjust `RETRIEVAL_TOP_K` for precision vs recall

## Troubleshooting

### Ollama Connection Error
```bash
# Check if Ollama is running
ollama list

# Restart Ollama
pkill ollama && ollama serve
```

### Model Not Found
```bash
ollama pull mistral
```

### Out of Memory
- Reduce `RETRIEVAL_TOP_K`
- Use a smaller embedding model
- Reduce LLM context window

## License

MIT License
