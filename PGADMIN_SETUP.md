# pgAdmin & PostgreSQL Setup with Docker

## ✅ Quick Start (Recommended)

### Step 1: Install Docker

Download and install from: https://www.docker.com/products/docker-desktop

### Step 2: Start Services

Run from the project root directory:
```bash
docker-compose up -d
```

This will start:
- ✅ PostgreSQL database (port 5432)
- ✅ pgAdmin web UI (port 5050)

### Step 3: Access pgAdmin

Open in your browser:
```
http://localhost:5050
```

**Login credentials:**
- Email: `admin@documentai.com`
- Password: `admin_password_123`

---

## 📊 pgAdmin - Add PostgreSQL Server

1. **Right-click on "Servers"** in left sidebar
2. **Select "Register > Server"**
3. **Fill in the form:**
   - **Name:** `DocumentAI`
   - **Hostname:** `postgres` (or `localhost`)
   - **Port:** `5432`
   - **Username:** `docuser`
   - **Password:** `nehu`
   - **Database:** `DocAI`

4. **Click "Save"**

Now you can:
- ✅ Browse tables
- ✅ View data
- ✅ Run SQL queries
- ✅ Manage backup/restore

---

## 🔧 Database Management in pgAdmin

### View All Analyses
```sql
SELECT id, filename, created_at 
FROM document_analyses 
ORDER BY created_at DESC;
```

### View Specific Analysis
```sql
SELECT * FROM document_analyses WHERE id = 1;
```

### Delete Old Analyses
```sql
DELETE FROM document_analyses 
WHERE created_at < NOW() - INTERVAL '30 days';
```

### Export Data
1. Right-click table → **Backup**
2. Choose location and settings
3. **Backup** button

---

## 🖥️ Run Backend with Database

```bash
# Install new dependencies
pip install -r requirements.txt

# Start backend (uses PostgreSQL from docker-compose)
python main.py
```

The backend will automatically:
- ✅ Connect to PostgreSQL
- ✅ Create tables if needed
- ✅ Save all document analyses

---

## 📝 Useful pgAdmin Features

### Query Editor
- `Tools → Query Tool` (Ctrl+Shift+Q)
- Run custom SQL
- See results instantly

### View Table Data
- Double-click table name
- See all stored documents
- Sort/filter/export

### Monitoring
- `Tools → Server → Database`
- View connections, queries, stats
- Monitor database health

---

## Troubleshooting

**Port already in use?**
```bash
# Change ports in docker-compose.yml
# PostgreSQL: "5432:5432" → "5433:5432"
# pgAdmin: "5050:80" → "5051:80"
```

**Forgot password?**
```bash
docker-compose down
docker-compose up -d
# Re-login with original credentials
```

**View logs:**
```bash
docker-compose logs postgres
docker-compose logs pgadmin
```

**Stop services:**
```bash
docker-compose down
```

**Restart services:**
```bash
docker-compose restart
```

---

## Current Setup

Your `.env` now configured for:
- ✅ PostgreSQL at `localhost:5432`
- ✅ Database: `DocAI`
- ✅ User: `docuser`
- ✅ Password: `nehu`

All future documents will be stored in PostgreSQL! 🎉
