# Enterprise Document Intelligence Generator

A full-stack application for extracting executive summaries and strategic insights from complex business documents.

## Tech Stack
- **Frontend**: Next.js 15+, Tailwind CSS, Framer Motion
- **Backend**: FastAPI (Python)
- **Intelligence**: RAG (Retrieval Augmented Generation) with FAISS, Sentence Transformers (BGE Large), and Llama 3 (via Groq API)

## Setup Instructions

### Backend
1. Navigate to `backend/`
2. Create a `.env` file based on `.env.example`:
   ```env
   GROQ_API_KEY=your_key_here
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   python -m uvicorn main:app --reload
   ```

### Frontend
1. Navigate to `frontend/`
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## Key Features
- **PDF/DOCX Upload**: Handles long-form business documents.
- **Strategic Analysis**: Extracts Risks, Opportunities, and Actionable Recommendations.
- **RAG-based Insights**: Uses semantic search to provide contextually accurate summaries.
- **Premium Dashboard**: Professional UI with animations and dark mode support.
