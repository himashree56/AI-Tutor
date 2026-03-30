# AI Tutor - RAG-Powered Learning Platform

An advanced Retrieval-Augmented Generation (RAG) backend designed for students. Upload educational PDFs, chat with your materials, and generate grounded quizzes with zero hallucinations.

## 🚀 Key Features

- **Grounded Chat:** Answers are extracted strictly from provided documents with verbatim citations.
- **AI Quiz Generator:** Automatically creates multiple-choice questions with evidence-based reasoning.
- **Cloud Vector Search:** Powered by **Pinecone** for high-speed, scaleable semantic retrieval.
- **Universal LLM Support:** Integrated with **OpenRouter** to use state-of-the-art models like nemotron and gpt-4o.
- **Real-time Streaming:** Token-by-token response streaming for a smooth user experience.

## 🛠️ Tech Stack

- **Framework:** FastAPI (Python)
- **Vector DB:** Pinecone (Serverless)
- **Embeddings:** OpenAI via OpenRouter (`text-embedding-3-small`)
- **Orchestration:** LangChain (Memory Management)
- **PDF Processing:** PyPDF2

## 📂 Project Structure

```text
AI-tutor/
├── backend/            # FastAPI Backend
│   ├── app/            # Core Application Logic
│   ├── tests/          # Unit & E2E Tests
│   ├── logs/           # Application Logs
│   └── requirements.txt
├── BEE654B-module-5-pdf.pdf  # Sample Document
└── README.md
```

## 🚦 Quick Start

1. **Clone & Setup:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   Update `.env` with your `OPENROUTER_API_KEY` and `PINECONE_API_KEY`.

3. **Run Server:**
   ```bash
   python -m uvicorn app.main:app --port 8001 --reload
   ```

4. **Test:**
   ```bash
   python test_tutor.py
   ```

---
> [!IMPORTANT]
> **Pinecone Setup:** Ensure your Pinecone index is set to **1536 dimensions** to match the OpenAI embedding standard used in this project.
