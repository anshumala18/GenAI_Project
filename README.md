# 📄 DocAI: Enterprise Document Intelligence Platform

**DocAI** is a high-performance, AI-driven intelligence workspace designed to transform complex business documents (PDF, DOCX, PPTX) into actionable strategic insights. Leveraging a custom **RAG (Retrieval-Augmented Generation)** pipeline, it provides deep analysis, risk assessment, and smart internal document search.

---

## 🚀 Key Features

### 🧠 Advanced Intelligence Engine
- **Strategic Analysis**: Generates Executive Summaries, Critical Risks, Growth Opportunities, and Actionable Recommendations.
- **Multi-Format Support**: Processes PDFs, Word Documents (`.docx`), and PowerPoint Presentations (`.pptx`).
- **Interactive RAG Chat**: Ask specific questions about your document and get context-aware answers instantly.

### 👤 Premium User Experience
- **Secure Authentication**: Built-in login and registration system with user-specific data isolation.
- **Profile Management**: Personalized user avatars and profile dropdowns.
- **Smart History Sidebar**: Search, pin, and manage your past document analyses.

### 🎨 Modern UI/UX
- **Glassmorphic Design**: A stunning, premium interface built with Tailwind CSS and Framer Motion.
- **Dual-Mode Aesthetics**: Sophisticated Dark and Light modes with persistence.
- **Integrated Document Viewer**: Professional-grade previewer for seamless analysis.

---

## 🛠 Tech Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Styling**: Tailwind CSS, Lucide Icons
- **State Management**: React Context API
- **Animations**: Framer Motion

### Backend
- **Core**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **OCR & Processing**: CloudConvert API, PyPDF2, python-docx
- **Authentication**: JWT (JSON Web Tokens) with Passlib

### AI & Vector Engine
- **LLM**: Llama 3.1 8B (via Groq) / xAI Grok
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **Embeddings**: Sentence-Transformers (`all-MiniLM-L6-v2`)

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL Server

### 2. Backend Setup
```bash
cd backend
# Install dependencies
pip install -r requirements.txt

# Configure Environment
# Create a .env file with:
# DATABASE_URL=postgresql://user:password@localhost:5432/documentai
# GROQ_API_KEY=your_groq_key
# CLOUDCONVERT_API_KEY=your_key

# Initialize Database
python init_db.py

# Run Server
python main.py
```

### 3. Frontend Setup
```bash
cd frontend
# Install dependencies
npm install

# Run Development Server
npm run dev
```

---

## 📂 Project Structure

```text
├── backend/
│   ├── rag/               # RAG Pipeline (Chunking, Embedding, Vector Store)
│   ├── converted_pdfs/    # Storage for processed documents
│   ├── main.py            # FastAPI Application Entry
│   ├── database.py        # SQLAlchemy Database Configuration
│   └── models.py          # Pydantic & SQLAlchemy Models
├── frontend/
│   ├── src/app/          # Next.js App Router Pages
│   ├── src/components/   # Reusable UI Components
│   └── src/context/      # Auth & Global State
└── docker-compose.yml     # Containerization support (Optional)
```

---

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

---

## 🏆 Acknowledgments
Special thanks to the **Groq** and **HuggingFace** teams for providing the powerful models that drive this platform.

**DocAI - Empowering Data-Driven Decisions.**
