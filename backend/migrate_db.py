import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def migrate():
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not found.")
        return
        
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            print("Adding preview_url column to document_analyses...")
            conn.execute(text('ALTER TABLE document_analyses ADD COLUMN IF NOT EXISTS preview_url VARCHAR'))
            conn.commit()
            print("Migration successful.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
