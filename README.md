# DocAI: Enterprise Document Intelligence Generator

A high-performance intelligence workspace that transforms complex business documents (PDF/DOCX) into actionable strategic insights using a custom RAG (Retrieval-Augmented Generation) pipeline.

---

## 🛠 Tech Stack & Libraries

### Frontend (User Interface)
- **Framework**: Next.js 15 (App Router)
- **Styling**: Tailwind CSS (Glassmorphism & Dark Mode)
- **Animations**: Framer Motion (Smooth transitions & sidebar toggles)
- **Icons**: Lucide React (Premium iconography)
- **Data Fetching**: Axios (API communication)

### Backend (Logic & PDF Processing)
- **Framework**: FastAPI (High-performance Python API)
- **Server**: Uvicorn (ASGI implementation)
- **Database ORM**: SQLAlchemy (PostgreSQL driver)
- **File Handling**: python-multipart, PyPDF2, python-docx
- **Environment**: python-dotenv

### Artificial Intelligence & Vector Engine
- **LLM**: Llama 3.1 8B (via Groq Cloud) or xAI Grok-2
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2) for semantic mapping
- **Orchestration**: Custom RAG Pipeline for context-aware analysis

---

## 🧠 GenAI Pipeline Flow

1.  **Ingestion & Extraction**: Documents are uploaded and parsed into raw text using specialized extractors for PDF and DOCX formats.
2.  **Semantic Chunking**: The extracted text is cleaned and split into optimized chunks to preserve context for the Large Language Model.
3.  **Vectorization**: Each chunk is converted into high-dimensional embeddings and indexed in a FAISS vector store.
4.  **Contextual Retrieval**: The system performs a semantic search within the vector index to retrieve the most relevant sections of the document.
5.  **Intelligence Generation**: The retrieved context is passed to the LLM (Groq/xAI) with a specialized strategic prompt to generate:
    - **Executive Summary**: Core highlights of the document.
    - **Critical Risks**: High-priority red flags and vulnerabilities.
    - **Growth Opportunities**: Potential areas for expansion or improvement.
    - **Strategic Recommendations**: Direct, actionable advice.
6.  **Persistence**: Final insights and file metadata are saved to PostgreSQL for instant history retrieval.

---

## ✨ Key Features

- **Intelligence Dashboard**: A dual-pane workspace featuring extracted insights alongside a professional PDF viewer.
- **Smart History Sidebar**:
    - **Search**: Instantly filter through past analyses.
    - **You can Pin the Important Reports**: Pin your most important reports to the top of the list.
    - **Permanent Deletion**: Securely remove reports and their associated PDF files from the server and database.
- **Integrated PDF Viewer**: High-quality document previewer with fit-to-width (`FitH`) viewing mode.
- **Theme Support**: Fully responsive design with deep dark-mode and light-mode aesthetics.
- **Production-Ready Backend**: Structured PostgreSQL database for reliable history management.

---

## 🚀 Quick Start

### 1. Database Setup
Ensure PostgreSQL is running. (Docker-compose support included).

### 2. Backend Initialization
```bash
cd backend
pip install -r requirements.txt
python init_db.py  # Initialize schema
python main.py     # Start server
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to start generating insights.
