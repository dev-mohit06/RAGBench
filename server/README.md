# 🚀 RAGBench Server — FastAPI Backend for Multi-Architecture RAG Comparison

This is the **FastAPI backend** for [RAGBench](https://github.com/dev-mohit06/RAGBench), a playground for comparing multiple Retrieval-Augmented Generation (RAG) architectures using PDF documents as knowledge sources.

---

## 🏗️ Architecture

- **FastAPI**: High-performance Python API framework.
- **LangChain**: For LLM orchestration and document processing.
- **Qdrant**: Vector database for storing and retrieving document embeddings.
- **Jina AI**: Embedding provider.
- **Gemini**: LLM for answer generation.

The backend exposes REST endpoints for document upload, processing, querying, and architecture comparison.

---

## 📦 Folder Structure

```
.
├── main.py                # FastAPI app entrypoint
├── controllers/           # API route controllers
├── models/                # Pydantic models for requests/responses
├── services/              # Business logic (RAGService)
├── RAGs/                  # RAG architecture implementations & factory
├── .env                   # Environment variables (API keys, etc.)
```

---

## 🛠️ Setup

1. **Clone and enter the server directory:**
    ```bash
    git clone https://github.com/dev-mohit06/RAGBench.git
    cd RAGBench/server
    ```

2. **Install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3. **Configure environment variables:**
    - Copy `.example.env` to `.env` and fill in your API keys:
      ```
      GOOGLE_API_KEY=...
      LANGSMITH_API_KEY=...
      JINA_API_KEY=...
      ```

4. **Run the server:**
    ```bash
    uvicorn main:app --reload
    ```

---

## 🔌 API Endpoints

All endpoints are prefixed with `/api/v1`.

| Method | Endpoint                | Description                                 |
|--------|-------------------------|---------------------------------------------|
| GET    | `/health`               | Health check/status                         |
| POST   | `/upload-documents`     | Upload and process PDF files                |
| GET    | `/status`               | Get document processing status              |
| POST   | `/query`                | Query one or more RAG architectures         |
| GET    | `/architectures`        | List available RAG architectures            |
| DELETE | `/documents`            | Clear all indexed documents                 |

---

## 🧠 Supported RAG Architectures

- **Simple RAG**: Standard embedding-based retrieval.
- **Reranking RAG**: Retrieval + semantic reranking.
- **HyDE RAG**: Hypothetical Document Embeddings.

---

## 📝 Example Query

```json
POST /api/v1/query
{
  "query": "What are the main findings in the uploaded documents?",
  "architectures": ["simple", "reranking", "hyde"],
  "k": 5,
  "show_context": true
}
```

---

## 🧪 Development

- All business logic is in [`services/rag_service.py`](services/rag_service.py).
- RAG architectures are implemented in [`RAGs/implementations/`](RAGs/implementations/).
- API models are in [`models/`](models/).

---

## 🤝 Contributing

Contributions and suggestions are welcome! Please open issues or PRs.

---

## 📄 License

MIT License

---

**See the [parent README](../README.md) for full-stack setup and frontend instructions.**