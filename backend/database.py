import os
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use DATABASE_URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the .env file. Please configure your PostgreSQL connection.")

# Create the database engine
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create uploads directory
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

class User(Base):
    """Store users and their credentials"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }

class PDFFile(Base):
    """Store PDF files and their metadata"""
    __tablename__ = "pdf_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    original_filename = Column(String)
    file_path = Column(String, unique=True)  # Path on disk
    file_url = Column(String)  # HTTP URL to download
    file_size = Column(Integer)
    mime_type = Column(String, default="application/pdf")
    
    # Relationship to analyses
    analyses = relationship("DocumentAnalysis", back_populates="pdf_file")
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_url": self.file_url,
            "file_size": self.file_size,
            "created_at": self.created_at.isoformat(),
        }

class DocumentAnalysis(Base):
    """Store document analysis results"""
    __tablename__ = "document_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    pdf_file_id = Column(Integer, ForeignKey("pdf_files.id"), index=True)
    filename = Column(String, index=True)
    extracted_text = Column(Text)
    
    executive_summary = Column(Text)  # JSON array
    key_risks = Column(Text)          # JSON array
    opportunities = Column(Text)      # JSON array
    strategic_recommendations = Column(Text)  # JSON array
    is_pinned = Column(Boolean, default=False)
    preview_url = Column(String, nullable=True)
    
    # Relationship to PDF file
    pdf_file = relationship("PDFFile", back_populates="analyses")
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "pdf_file_id": self.pdf_file_id,
            "pdf_file_url": self.pdf_file.file_url if self.pdf_file else None,
            "executive_summary": json.loads(self.executive_summary),
            "key_risks": json.loads(self.key_risks),
            "opportunities": json.loads(self.opportunities),
            "strategic_recommendations": json.loads(self.strategic_recommendations),
            "extracted_text": self.extracted_text,
            "preview_url": self.preview_url,
            "is_pinned": self.is_pinned,
            "created_at": self.created_at.strftime("%Y-%m-%d"),
        }

    def to_summary_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "is_pinned": self.is_pinned,
            "created_at": self.created_at.strftime("%Y-%m-%d"),
        }

class Note(Base):
    """Store user notes associated with analyses"""
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    analysis_id = Column(Integer, ForeignKey("document_analyses.id"), index=True)
    selected_text = Column(Text)
    note_text = Column(Text)
    
    user = relationship("User")
    analysis = relationship("DocumentAnalysis", back_populates="notes")
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "analysis_id": self.analysis_id,
            "selected_text": self.selected_text,
            "note_text": self.note_text,
            "created_at": self.created_at.isoformat(),
        }

# Update DocumentAnalysis to include notes relationship
DocumentAnalysis.notes = relationship(
    "Note",
    back_populates="analysis",
    cascade="all, delete-orphan"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_document_file(
    db: Session,
    original_filename: str,
    file_content: bytes,
    mime_type: str = "application/pdf"
) -> PDFFile:
    """Save PDF file and return file object with correct URL"""
    import uuid
    file_id = str(uuid.uuid4())[:8]
    # Clean the original filename to avoid URL issues
    safe_name = "".join(c for c in original_filename if c.isalnum() or c in "._- ").replace(" ", "_")
    final_filename = f"{file_id}_{safe_name}"
    file_path = os.path.join(UPLOAD_DIR, final_filename)
    
    # Save file to disk
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Construct the serving URL
    # Note: In production, this might be a full domain, but for local dev localhost:8000 works
    file_url = f"http://localhost:8000/uploads/{final_filename}"
    
    # Save metadata to database
    pdf_file = PDFFile(
        filename=final_filename,
        original_filename=original_filename,
        file_path=file_path,
        file_url=file_url,
        file_size=len(file_content),
        mime_type=mime_type
    )
    db.add(pdf_file)
    db.commit()
    db.refresh(pdf_file)
    return pdf_file

def save_analysis(
    db: Session,
    pdf_file_id: int,
    filename: str,
    extracted_text: str,
    analysis: dict,
    preview_url: str = None
) -> DocumentAnalysis:
    """Save document analysis to database"""
    doc = DocumentAnalysis(
        pdf_file_id=pdf_file_id,
        filename=filename,
        extracted_text=extracted_text,
        executive_summary=json.dumps(analysis.get("executive_summary", [])),
        key_risks=json.dumps(analysis.get("key_risks", [])),
        opportunities=json.dumps(analysis.get("opportunities", [])),
        strategic_recommendations=json.dumps(analysis.get("strategic_recommendations", [])),
        preview_url=preview_url
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def get_all_analyses(db: Session, limit: int = 10):
    """Retrieve the last N document analyses, pinned first"""
    from sqlalchemy import desc
    return db.query(DocumentAnalysis).order_by(
        desc(DocumentAnalysis.is_pinned),
        desc(DocumentAnalysis.created_at)
    ).limit(limit).all()

def get_analysis_by_id(db: Session, analysis_id: int):
    """Get specific analysis by ID"""
    return db.query(DocumentAnalysis).filter(
        DocumentAnalysis.id == analysis_id
    ).first()

def toggle_pin_analysis(db: Session, analysis_id: int):
    """Toggle the pinned state of an analysis"""
    analysis = get_analysis_by_id(db, analysis_id)
    if analysis:
        analysis.is_pinned = not analysis.is_pinned
        db.commit()
        db.refresh(analysis)
    return analysis

def delete_analysis(db: Session, analysis_id: int):
    """Delete analysis and its associated PDF file"""
    analysis = get_analysis_by_id(db, analysis_id)
    if not analysis:
        return False
        
    # Get PDF file info
    pdf_file = analysis.pdf_file
    
    # Delete from database
    db.delete(analysis)
    
    # If the PDF file is only associated with this analysis (common in current app), 
    # we can delete the PDF metadata too.
    if pdf_file:
        # Check if any other analysis uses this PDF
        other_analyses = db.query(DocumentAnalysis).filter(
            DocumentAnalysis.pdf_file_id == pdf_file.id
        ).count()
        
        if other_analyses == 0:
            # Delete file from disk
            if pdf_file.file_path and os.path.exists(pdf_file.file_path):
                try:
                    os.remove(pdf_file.file_path)
                except Exception as e:
                    print(f"Error removing file from disk: {e}")
            
            # Delete PDF record from database
            db.delete(pdf_file)
            
    db.commit()
    return True

def get_pdf_file_by_id(db: Session, pdf_id: int):
    """Get PDF file by ID"""
    return db.query(PDFFile).filter(PDFFile.id == pdf_id).first()

def get_all_pdf_files(db: Session, limit: int = 100):
    """Get all PDF files"""
    return db.query(PDFFile).order_by(PDFFile.created_at.desc()).limit(limit).all()

def save_note(
    db: Session,
    user_id: int,
    analysis_id: int,
    selected_text: str,
    note_text: str
):
    """Save user note in database (allows multiple notes)"""
    new_note = Note(
        user_id=user_id,
        analysis_id=analysis_id,
        selected_text=selected_text,
        note_text=note_text
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

def get_notes_by_analysis_id(db: Session, analysis_id: int, user_id: int):
    """Retrieve all notes for a specific analysis and user"""
    return db.query(Note).filter(
        Note.analysis_id == analysis_id,
        Note.user_id == user_id
    ).all()
