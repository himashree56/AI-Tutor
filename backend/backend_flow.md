# AI Tutor Flow Diagrams

Below are the operational flows of the AI Tutor platform. These diagrams illustrate the path from raw data to a grounded, AI-generated response.

## 📥 Ingestion Flow (PDF -> Vector DB)

This flow describes how a student's document is processed and indexed for future search.

```mermaid
graph TD
    A[Upload PDF] --> B[PDF Processor]
    B -->|Extract Text| C[Text Chunker]
    C -->|Recursive Split| D[List of Chunks]
    D --> E[Embeddings Service]
    E -->|OpenRouter API| F[1536-dim Vectors]
    F --> G[Pinecone Upsert]
    G --> H[Document Ready for Chat]
```

---

## 💬 RAG Chat Flow (JSON -> Answer)

This flow explains the Retrieval-Augmented Generation (RAG) process used to answer user questions using only document context.

```mermaid
graph TD
    A[JSON Chat Request] --> B[Embeddings Service]
    B -->|Generate Query Vector| C[Pinecone Query]
    C -->|Top-K Chunks| D[Retriever Service]
    D --> E[Local Reranker]
    E -->|Scored Relevance| F[Grounded Context]
    F --> G[Prompt Builder]
    G -->|Strict System Instructions| H[LLM (OpenRouter)]
    H -->|Verified Response| I[User Answer]
```

---

## 📝 Quiz Generation Flow (JSON -> JSON Quiz)

The flow for creating grounded, educational assessments.

```mermaid
graph TD
    A[JSON Quiz Request] --> B{Topic or Context?}
    B -->|Topic| C[Pinecone Semantic Search]
    B -->|Context| D[Direct Context]
    C --> E[Topic Context Chunks]
    E --> F[Strict Quiz Prompt]
    D --> F
    F -->|Evidence-Based Quoting| G[LLM (OpenRouter)]
    G --> H[Pydantic Schema Validation]
    H --> I[JSON Quiz with Citations]
```

---

### Core Grounding Principles:

1. **Schema Synchronization:** Both backend and frontend agree on exact JSON structures for chat and quizzes, preventing 422 errors.
2. **Verbatim Evidence:** For every quiz question, the AI must provide a direct quote from the source PDF.
3. **Refusal Logic:** If the Pinecone search returns no relevant chunks for a topic, the system automatically refuses to generate a quiz, preventing hallucinations.
4. **Citations:** Every chat answer includes `[Source X]` tags mapping to specific page numbers and document names.
