# Setup Guide - AI Tutor Backend

This guide provides step-by-step instructions for installing and running the AI Tutor platform.

## 🛠 Prerequisites

- Python 3.10+
- [Pinecone Account](https://www.pinecone.io/) (Free tier)
- [OpenRouter API Key](https://openrouter.ai/) (For LLM and Embeddings)

## 📋 Installation

1. **Clone & Navigate:**
   ```bash
   cd AI-Tutor/backend
   ```

2. **Virtual Environment Setup:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

Create a `.env` file in the `backend/` folder and update it with your credentials.

| Variable | Description | Example |
| :--- | :--- | :--- |
| `OPENROUTER_API_KEY` | Your OpenRouter API Key | `sk-or-v1-...` |
| `PINECONE_API_KEY` | Your Pinecone API Key | `pcsk_...` |
| `PINECONE_INDEX_NAME` | The name of your index | `ai-tutor` |

---
> [!IMPORTANT]
> **Pinecone Index Configuration:**
> - **Dimension:** 1536
> - **Metric:** Cosine
> - **Serverless Spec:** `aws-us-east-1` (or your preferred region)

## 🎯 Running the System

### 1. Start the FastAPI Server
```bash
# From the backend directory
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

### 2. Verify with CLI Test Tool
Ensure the server is running, then in a new terminal:
```bash
cd backend
python test_tutor.py
```

### 3. Upload a Document
Use the `test_ingest.py` script to upload your first PDF:
```bash
cd backend
python test_ingest.py
```
*(This will process and upsert your document to Pinecone)*

---

## 🧪 Testing

To run the full suite of automated tests:
```bash
pytest tests/
```
