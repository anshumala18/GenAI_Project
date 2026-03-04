#!/usr/bin/env python3
"""Initialize database tables"""

import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

load_dotenv()

# Import database models
from database import Base, engine

print("=" * 60)
print("DATABASE INITIALIZATION")
print("=" * 60)

try:
    print(f"\n📁 Creating tables...")
    Base.metadata.create_all(bind=engine)
    print(f"✅ Tables created successfully!")
    
    # List created tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\n📊 Tables in database:")
    for table in tables:
        columns = inspector.get_columns(table)
        print(f"\n  ✓ {table}")
        for col in columns:
            print(f"    - {col['name']}: {col['type']}")
    
    print("\n" + "=" * 60)
    print("✅ Database is ready!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
