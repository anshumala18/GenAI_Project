from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from models import AnalysisResponse, ErrorResponse, NoteCreate, NoteResponse
from processor import DocumentProcessor
from engine import IntelligenceEngine
from database import (
    get_db, save_analysis, save_document_file, get_all_analyses, 
    get_analysis_by_id, get_pdf_file_by_id, UPLOAD_DIR,
    save_note, get_notes_by_analysis_id
)
from converter import CloudConvertService
from sqlalchemy.orm import Session
import os

app = FastAPI(title="Enterprise Document Intelligence API")

# Setup CORS - Use explicit origin for reliability with credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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
converter = CloudConvertService()

CONVERTED_DIR = "converted_pdfs"
if not os.path.exists(CONVERTED_DIR):
    os.makedirs(CONVERTED_DIR)
app.mount("/converted_pdfs", StaticFiles(directory=CONVERTED_DIR), name="converted_pdfs")

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(('.pdf', '.docx', '.pptx')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, DOCX and PPTX are supported.")

    try:
        content = await file.read()
        
        # 1. Save document file to disk and database
        pdf_file = save_document_file(
            db=db,
            original_filename=file.filename,
            file_content=content,
            mime_type=file.content_type
        )
        print(f"Document saved successfully: {pdf_file.file_url}")
        
        # 2. Extract Text
        if file.filename.lower().endswith('.pdf'):
            text = processor.extract_text_from_pdf(content)
        elif file.filename.lower().endswith('.docx'):
            text = processor.extract_text_from_docx(content)
        elif file.filename.lower().endswith('.pptx'):
            text = processor.extract_text_from_pptx(content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
            
        if not text.strip():
            raise HTTPException(status_code=400, detail="Document appears to be empty or unreadable.")

        # 3. Clean and Chunk
        clean_text = processor.clean_text(text)
        chunks = processor.get_chunks(clean_text)

        # 4. Vectorize
        engine.create_vector_store(chunks)

        # 5. Analyze
        analysis = engine.analyze_document()

        # 6. Handle Preview URL (Conversion if needed)
        preview_url = pdf_file.file_url
        if file.filename.lower().endswith(('.docx', '.pptx')):
            try:
                converted_path = converter.convert_to_pdf(pdf_file.file_path, CONVERTED_DIR)
                preview_url = f"http://localhost:8000/converted_pdfs/{os.path.basename(converted_path)}"
            except Exception as e:
                print(f"Conversion failed, using original file as preview (will fail in UI): {e}")

        # 7. Save analysis to database with PDF file reference and preview URL
        db_record = save_analysis(
            db=db,
            pdf_file_id=pdf_file.id,
            filename=file.filename,
            extracted_text=text,
            analysis=analysis,
            preview_url=preview_url
        )
        
        print(f"Analysis saved to database with ID: {db_record.id}")

        return AnalysisResponse(
            executive_summary=analysis.get("executive_summary", []),
            key_risks=analysis.get("key_risks", []),
            opportunities=analysis.get("opportunities", []),
            strategic_recommendations=analysis.get("strategic_recommendations", []),
            filename=file.filename,
            pdf_file_url=pdf_file.file_url,
            preview_url=preview_url
        )

    except Exception as e:
        print(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/notes", response_model=NoteResponse)
async def create_note(note_data: NoteCreate, db: Session = Depends(get_db)):
    try:
        from database import save_note
        note = save_note(
            db=db,
            analysis_id=note_data.analysis_id,
            selected_text=note_data.selected_text,
            note_text=note_data.note_text
        )
        return NoteResponse(**note.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notes/{analysis_id}", response_model=NoteResponse)
async def get_notes(analysis_id: int, db: Session = Depends(get_db)):
    try:
        from database import Note
        note = db.query(Note).filter(Note.analysis_id == analysis_id).first()
        if not note:
            return {
                "id": 0,
                "analysis_id": analysis_id,
                "selected_text": "",
                "note_text": "",
                "created_at": ""
            }
        return NoteResponse(**note.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyses")
async def get_analyses(db: Session = Depends(get_db)):
    """Get summarized list of last 10 document analyses for history sidebar"""
    analyses = get_all_analyses(db)
    return [a.to_summary_dict() for a in analyses]

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

@app.post("/analysis/{analysis_id}/pin")
async def toggle_pin(analysis_id: int, db: Session = Depends(get_db)):
    """Toggle pin status of an analysis"""
    from database import toggle_pin_analysis
    analysis = toggle_pin_analysis(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis.to_summary_dict()

@app.delete("/analysis/{analysis_id}")
async def delete_analysis_endpoint(analysis_id: int, db: Session = Depends(get_db)):
    """Delete an analysis and its PDF file"""
    from database import delete_analysis
    success = delete_analysis(db, analysis_id)
    if not success:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"status": "success", "message": "Analysis deleted"}

if __name__ == "__main__":
    import uvicorn
    print("\nDOCUMENT AI BACKEND STARTING")
    print("URL: http://127.0.0.1:8000")
    print("--------------------------------")
    uvicorn.run(app, host="127.0.0.1", port=8000)
