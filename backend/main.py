from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os
from datetime import datetime
import auth_utils
from models import (
    AnalysisResponse, ErrorResponse, NoteCreate, NoteResponse, 
    QuestionRequest, ChatResponse, UserCreate, UserResponse, Token
)
from processor import DocumentProcessor
from engine import IntelligenceEngine
from database import (
    get_db, User, save_analysis, save_document_file, get_all_analyses, 
    get_analysis_by_id, get_pdf_file_by_id, UPLOAD_DIR,
    save_note, get_notes_by_analysis_id
)
from converter import CloudConvertService
from rag.chunking import ChunkingService
from rag.vector_store import VectorStoreService
from rag.rag_pipeline import RAGPipeline
from database import Base, engine

# Create tables automatically
Base.metadata.create_all(bind=engine)

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
chunking_service = ChunkingService()
vector_store = VectorStoreService()
rag_pipeline = RAGPipeline(vector_store=vector_store)

CONVERTED_DIR = "converted_pdfs"
if not os.path.exists(CONVERTED_DIR):
    os.makedirs(CONVERTED_DIR)
app.mount("/converted_pdfs", StaticFiles(directory=CONVERTED_DIR), name="converted_pdfs")

# Auth setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = auth_utils.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        print(f"DEBUG: Registering user - Name: {user_data.name}, Email: {user_data.email}")
        hashed_pwd = auth_utils.get_password_hash(user_data.password)
        new_user = User(
            name=user_data.name,
            email=user_data.email, 
            hashed_password=hashed_pwd
        )
        print(f"DEBUG: User object before add - Name: {new_user.name}")
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"DEBUG: User object after refresh - ID: {new_user.id}, Name: {new_user.name}")
        return new_user
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Registration error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not auth_utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = auth_utils.create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": user.to_dict()
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_document(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

        # 3. Clean and Chunk for RAG
        chunks = chunking_service.create_chunks(text)
        
        # 4. Create Vector Index (Embeddings + FAISS)
        vector_store.create_index(chunks)

        # 5. Analyze (Existing structured insights)
        engine.create_vector_store(chunks)
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

@app.post("/ask", response_model=ChatResponse)
async def ask_docai(
    payload: QuestionRequest,
    current_user: User = Depends(get_current_user)
):
    answer = rag_pipeline.answer_question(payload.question)
    return ChatResponse(answer=answer)

@app.post("/notes", response_model=NoteResponse)
async def create_or_update_note(
    note_data: NoteCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        from database import save_note
        note = save_note(
            db=db,
            user_id=current_user.id,
            analysis_id=note_data.analysis_id,
            selected_text=note_data.selected_text,
            note_text=note_data.note_text
        )
        return NoteResponse(**note.to_dict())
    except Exception as e:
        print(f"Error saving note: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notes/{analysis_id}", response_model=list[NoteResponse])
async def get_notes(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notes = get_notes_by_analysis_id(db, analysis_id, current_user.id)
    return [NoteResponse(**note.to_dict()) for note in notes]

@app.get("/analyses")
async def get_analyses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get summarized list of last 10 document analyses for history sidebar"""
    analyses = get_all_analyses(db)
    return [a.to_summary_dict() for a in analyses]

@app.get("/analysis/{analysis_id}")
async def get_analysis(
    analysis_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific analysis by ID with PDF download link"""
    analysis_record = get_analysis_by_id(db, analysis_id)
    if not analysis_record:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # NEW: Ensure RAG index is prepared for this document if we're switching contexts
    if analysis_record.extracted_text:
        print(f"🔄 Preparing RAG index for loaded document: {analysis_record.filename}")
        chunks = chunking_service.create_chunks(analysis_record.extracted_text)
        vector_store.create_index(chunks)
        
    return analysis_record.to_dict()

@app.get("/pdfs")
async def get_all_pdfs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all stored PDF files with download links"""
    from database import get_all_pdf_files
    pdfs = get_all_pdf_files(db)
    return {
        "total": len(pdfs),
        "pdfs": [p.to_dict() for p in pdfs]
    }

@app.get("/pdf/{pdf_id}")
async def get_pdf(
    pdf_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific PDF metadata with download link"""
    pdf = get_pdf_file_by_id(db, pdf_id)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    return pdf.to_dict()

@app.get("/download/{pdf_id}")
async def download_pdf(
    pdf_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
async def toggle_pin(
    analysis_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle pin status of an analysis"""
    from database import toggle_pin_analysis
    analysis = toggle_pin_analysis(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis.to_summary_dict()

@app.delete("/analysis/{analysis_id}")
async def delete_analysis_endpoint(
    analysis_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
