from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from models import AnalysisResponse, ErrorResponse
from processor import DocumentProcessor
from engine import IntelligenceEngine
from database import get_db, save_analysis, save_pdf_file, get_all_analyses, get_analysis_by_id, get_pdf_file_by_id, UPLOAD_DIR
from sqlalchemy.orm import Session
import os

app = FastAPI(title="Enterprise Document Intelligence API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files as static files
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

processor = DocumentProcessor()
engine = IntelligenceEngine()

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(('.pdf', '.docx')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX are supported.")

    try:
        content = await file.read()
        
        # 1. Save PDF file to disk and database
        pdf_file_url = f"http://localhost:8000/uploads/{file.filename}"
        pdf_file = save_pdf_file(
            db=db,
            original_filename=file.filename,
            file_content=content,
            file_url=pdf_file_url
        )
        print(f"✅ PDF saved: {pdf_file.file_url}")
        
        # 2. Extract Text
        if file.filename.lower().endswith('.pdf'):
            text = processor.extract_text_from_pdf(content)
        else:
            text = processor.extract_text_from_docx(content)
            
        if not text.strip():
            raise HTTPException(status_code=400, detail="Document appears to be empty or unreadable.")

        # 3. Clean and Chunk
        clean_text = processor.clean_text(text)
        chunks = processor.get_chunks(clean_text)

        # 4. Vectorize
        engine.create_vector_store(chunks)

        # 5. Analyze
        analysis = engine.analyze_document()

        # 6. Save analysis to database with PDF file reference
        db_record = save_analysis(
            db=db,
            pdf_file_id=pdf_file.id,
            filename=file.filename,
            extracted_text=text,
            analysis=analysis
        )
        
        print(f"✅ Analysis saved to database with ID: {db_record.id}")

        return AnalysisResponse(
            executive_summary=analysis.get("executive_summary", []),
            key_risks=analysis.get("key_risks", []),
            opportunities=analysis.get("opportunities", []),
            strategic_recommendations=analysis.get("strategic_recommendations", []),
            filename=file.filename
        )

    except Exception as e:
        print(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/analyses")
async def get_analyses(db: Session = Depends(get_db)):
    """Get all stored document analyses with PDF download links"""
    analyses = get_all_analyses(db)
    return {
        "total": len(analyses),
        "analyses": [a.to_dict() for a in analyses]
    }

@app.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Get specific analysis by ID with PDF download link"""
    analysis = get_analysis_by_id(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis.to_dict()

@app.get("/pdfs")
async def get_all_pdfs(db: Session = Depends(get_db)):
    """Get all stored PDF files with download links"""
    from database import get_all_pdf_files
    pdfs = get_all_pdf_files(db)
    return {
        "total": len(pdfs),
        "pdfs": [p.to_dict() for p in pdfs]
    }

@app.get("/pdf/{pdf_id}")
async def get_pdf(pdf_id: int, db: Session = Depends(get_db)):
    """Get specific PDF metadata with download link"""
    pdf = get_pdf_file_by_id(db, pdf_id)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    return pdf.to_dict()

@app.get("/download/{pdf_id}")
async def download_pdf(pdf_id: int, db: Session = Depends(get_db)):
    """Download PDF file by ID"""
    pdf = get_pdf_file_by_id(db, pdf_id)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    file_path = pdf.file_path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")
    
    return FileResponse(
        path=file_path,
        filename=pdf.original_filename,
        media_type="application/pdf"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
