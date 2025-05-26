# 🖥️ RAGBench Client

This is the **frontend** for the RAGBench project, built with [Next.js](https://nextjs.org/) and [Tailwind CSS](https://tailwindcss.com/). It provides an interactive UI to compare multiple Retrieval-Augmented Generation (RAG) architectures using PDF documents as knowledge sources.

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Run the Development Server

```bash
npm run dev
```

The app will be available at [http://localhost:3000](http://localhost:3000).

---

## ⚙️ Environment Variables

Create a `.env` file in the `client` directory and add your backend API URL:

```
NEXT_PUBLIC_API_URL=http://localhost:3000/api
```

---

## 🛠️ Tech Stack

- [Next.js](https://nextjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Shadcn/UI](https://ui.shadcn.com/) (for UI components)

---

## 📦 Project Structure

```
client/
├── public/         # Static assets
├── src/            # Source code
│   ├── app/        # Next.js app directory
│   └── styles/     # Global styles
├── .env            # Environment variables
├── package.json
└── README.md
```

---

## 📄 License

This project is licensed under the MIT License.