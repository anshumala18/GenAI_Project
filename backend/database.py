import os
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
import json

# SQLite database file
DATABASE_URL = "sqlite:///./documentai.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create uploads directory
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

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
            "created_at": self.created_at.isoformat(),
        }

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_pdf_file(
    db: Session,
    original_filename: str,
    file_content: bytes,
    file_url: str
) -> PDFFile:
    """Save PDF file and return file object with URL"""
    # Generate safe filename
    import uuid
    file_id = str(uuid.uuid4())[:8]
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{original_filename}")
    
    # Save file to disk
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Save metadata to database
    pdf_file = PDFFile(
        filename=f"{file_id}_{original_filename}",
        original_filename=original_filename,
        file_path=file_path,
        file_url=file_url,
        file_size=len(file_content),
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
    analysis: dict
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
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def get_all_analyses(db: Session, limit: int = 100):
    """Retrieve all document analyses"""
    return db.query(DocumentAnalysis).order_by(
        DocumentAnalysis.created_at.desc()
    ).limit(limit).all()

def get_analysis_by_id(db: Session, analysis_id: int):
    """Get specific analysis by ID"""
    return db.query(DocumentAnalysis).filter(
        DocumentAnalysis.id == analysis_id
    ).first()

def get_pdf_file_by_id(db: Session, pdf_id: int):
    """Get PDF file by ID"""
    return db.query(PDFFile).filter(PDFFile.id == pdf_id).first()

def get_all_pdf_files(db: Session, limit: int = 100):
    """Get all PDF files"""
    return db.query(PDFFile).order_by(PDFFile.created_at.desc()).limit(limit).all()
