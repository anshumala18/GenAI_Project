# Database Configuration Guide

## Quick Start (SQLite - No Setup Required)

SQLite is enabled by default and requires NO installation. Your data is stored in:
```
backend/documents.db
```

Just install dependencies:
```bash
pip install -r requirements.txt
python main.py
```

That's it! All analyses will be saved automatically.

---

## Production Setup (PostgreSQL - Recommended)

### Step 1: Install PostgreSQL

**Windows:**
- Download from: https://www.postgresql.org/download/windows/
- Run installer, set password for `postgres` user
- Remember the password!

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo service postgresql start
```

### Step 2: Create Database

```bash
# Connect to PostgreSQL as admin
psql -U postgres

# Create database
CREATE DATABASE documentai;

# Create user with password
CREATE USER docuser WITH PASSWORD 'your_secure_password_here';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE documentai TO docuser;

# Exit
\q
```

### Step 3: Update .env

```env
GROQ_API_KEY=gsk_your_key_here
DATABASE_URL=postgresql://docuser:your_secure_password_here@localhost:5432/documentai
```

### Step 4: Install & Run

```bash
pip install -r requirements.txt
python main.py
```

---

## Data Stored in Database

✅ **For Each Document:**
- ✅ Filename and file size
- ✅ Original PDF file (binary)
- ✅ Extracted text
- ✅ Executive summary
- ✅ Key risks
- ✅ Opportunities
- ✅ Strategic recommendations
- ✅ Timestamp of analysis

---

## View Stored Data

### List All Analyses
```bash
curl http://localhost:8000/analyses
```

### View Specific Analysis
```bash
curl http://localhost:8000/analysis/1
```

---

## Database Management

### SQLite (Using Command Line)

```bash
sqlite3 documents.db

# List all tables
.tables

# View all analyses
SELECT id, filename, created_at FROM document_analyses;

# View specific analysis
SELECT * FROM document_analyses WHERE id = 1;

# Exit
.quit
```

### PostgreSQL (Using psql)

```bash
psql -U docuser -d documentai

# List tables
\dt

# View analyses
SELECT id, filename, created_at FROM document_analyses;

# Exit
\q
```

---

## Backup & Export

### SQLite
```bash
# Copy database file
cp documents.db documents_backup.db
```

### PostgreSQL
```bash
# Backup database
pg_dump -U docuser documentai > backup.sql

# Restore database
psql -U docuser documentai < backup.sql
```

---

## Current Setup

You're currently using: **SQLite (Default)**
- ✅ No configuration needed
- ✅ Data saved in `backend/documents.db`
- ✅ Perfect for development
- ✅ Good for small projects

To switch to PostgreSQL later, just update the `DATABASE_URL` in `.env`
