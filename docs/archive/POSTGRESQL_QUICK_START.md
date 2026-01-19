# PostgreSQL Quick Start Guide

## 🚀 Quick Setup (5 Minutes)

### Step 1: Install PostgreSQL
- **Windows**: Download from https://www.postgresql.org/download/windows/
- **Linux**: `sudo apt-get install postgresql`
- **Mac**: `brew install postgresql`

**Remember the password** you set for the `postgres` user!

---

### Step 2: Create Database

Open terminal/command prompt and run:

```bash
psql -U postgres
```

Then in PostgreSQL prompt:
```sql
CREATE DATABASE dealgoat_db;
\q
```

---

### Step 3: Update .env File

Edit `backend/.env` and update the password:

```env
DB_PASSWORD=your_actual_postgres_password
```

Replace `your_actual_postgres_password` with the password you set during PostgreSQL installation.

---

### Step 4: Run Setup Script

```bash
cd backend
python setup_postgres.py
```

This will:
- ✅ Check database connection
- ✅ Verify database exists
- ✅ Run migrations
- ✅ Create all tables

---

### Step 5: Start Server

```bash
python manage.py runserver
```

Open http://localhost:8000/api/auth/check-email/?email=test@example.com

If you see `{"available": true}`, you're all set! 🎉

---

## 🐛 Common Issues

### "password authentication failed"
- Check `DB_PASSWORD` in `backend/.env`
- Make sure it matches your PostgreSQL password

### "database does not exist"
- Run: `CREATE DATABASE dealgoat_db;` in psql

### "could not connect to server"
- Make sure PostgreSQL service is running
- Check `DB_HOST` and `DB_PORT` in `.env`

---

## 📚 Full Documentation

For detailed setup instructions, see:
- `POSTGRESQL_SETUP.md` - Complete setup guide
- `PROJECT_ANALYSIS.md` - Project overview

---

**Need Help?** Check the troubleshooting section in `POSTGRESQL_SETUP.md`

