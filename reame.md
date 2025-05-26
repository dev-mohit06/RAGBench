# 🔍 RAGBench — Compare Multiple RAG Architectures with PDF Inputs

**RAGBench** is a full-stack playground designed to **compare Retrieval-Augmented Generation (RAG) architectures** using PDF documents as knowledge sources. Built with **FastAPI**, **Next.js**, and **Qdrant**, it allows developers, researchers, and enthusiasts to explore how different RAG pipelines behave for the same query and dataset.

> 🚧 **This project is currently under active development by [@dev-mohit06](https://github.com/dev-mohit06). Contributions and suggestions are welcome!**


---

## ✨ Features

- **🧠 Multiple RAG Architectures**
  - 🔹 Basic RAG (Standard embedding-based retrieval)
  - 🔹 Re-Ranker RAG (Retrieval + reranking using a second model)
  - 🔹 HyDE RAG (Hypothetical Document Embeddings — generates hypothetical answers to queries and embeds them for improved retrieval)
- **📄 PDF Upload and Embedding**
  - Automatically splits, embeds, and stores documents in Qdrant vector DB.

- **🔎 Multi-Architecture Querying**
  - Select one or more architectures to compare answers for the same query.

- **🧾 Source Transparency**
  - View retrieved chunks, page numbers, and context per architecture.

- **📊 Metrics Display**
  - Response time per architecture.
  - Visual differences in retrieved contexts and LLM answers.
  - Confidence or relevance scores (when available).

- **⚡ Fast and Interactive UI**
  - Built using **Next.js**, **Tailwind CSS**.
  - Tabbed or side-by-side result views.
  - Feedback indicators for long-running operations.

---

## 🧰 Tech Stack

| Layer       | Tech Used                                   |
|-------------|---------------------------------------------|
| Frontend    | Next.js, Tailwind CSS, Shadcn/UI            |
| Backend     | FastAPI, LangChain                          |
| Embeddings  | Jina AI                 |
| LLM APIs    | Gemini                    |
| Vector DB   | Qdrant                                      |
| Hosting     | Vercel (Frontend), Render/Railway (Backend) |

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/dev-mohit06/RAGBench.git
cd RAGBench
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Make sure you configure your .env with the appropriate API keys and Qdrant setup.

### 3. Frontend Setup
```
cd frontend
npm install
npm run dev
```

Update the .env.local file in the frontend with your backend API URL.

---

## 🧪 Example Use Case

1. **Upload your PDF(s):** Add one or more PDF documents as your knowledge base.
2. **Select RAG Architectures:** Choose up to three RAG architectures to compare.
3. **Enter a Query:** For example, _“What are the key takeaways from chapter 3?”_
4. **Compare Results:** View answers from each architecture side-by-side or in tabbed views.
5. **Evaluate Responses:** Determine which architecture provides the most relevant or accurate answer.

---

## 🔗 Live Demo

- 🧠 **Frontend:** [https://ragbench.vercel.app](https://ragbench.vercel.app)
- 🚀 **Backend:** [https://ragbench-api.render.com](https://ragbench-api.render.com)

---

## 📚 Inspiration & References

- [VARAG](https://github.com/adithya-s-k/VARAG) — Reference implementation for multiple RAG architectures.
- [AI Engineering Academy](https://aiengineering.academy/)
- [LangChain](https://github.com/langchain-ai/langchain)
- [Qdrant](https://qdrant.tech/)

---

⭐️ Support

If you found this project helpful, consider giving us a ⭐ on GitHub!

---

📄 License

This project is licensed under the MIT License.

---