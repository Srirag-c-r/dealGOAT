# DealGoat - PostgreSQL Database Setup

## 🎯 Overview

This project has been **fully configured for PostgreSQL**. All necessary configurations, scripts, and documentation have been created.

---

## 📚 Documentation Files

| File | Description |
|------|-------------|
| **POSTGRESQL_QUICK_START.md** | ⚡ Start here! Quick 5-minute setup guide |
| **POSTGRESQL_SETUP.md** | 📖 Comprehensive setup guide with troubleshooting |
| **POSTGRESQL_MIGRATION_COMPLETE.md** | ✅ Migration summary and checklist |
| **PROJECT_ANALYSIS.md** | 📊 Complete project analysis |
| **README_POSTGRESQL.md** | 📋 This file - overview and navigation |

---

## 🚀 Quick Start

### 1. Install PostgreSQL
- **Windows**: https://www.postgresql.org/download/windows/
- **Linux**: `sudo apt-get install postgresql`
- **Mac**: `brew install postgresql`

### 2. Create Database
```bash
psql -U postgres
CREATE DATABASE dealgoat_db;
\q
```

### 3. Configure Environment
Edit `backend/.env`:
```env
DB_PASSWORD=your_actual_postgres_password
```

### 4. Run Setup
```bash
cd backend
python setup_postgres.py
```

### 5. Start Server
```bash
python manage.py runserver
```

**Done!** 🎉

For detailed instructions, see **POSTGRESQL_QUICK_START.md**

---

## 📁 Project Structure

```
DealGoat/
├── backend/
│   ├── dealgoat/
│   │   └── settings.py          # ✅ PostgreSQL configured
│   ├── users/
│   │   ├── models.py            # User & OTP models
│   │   └── migrations/          # Database migrations
│   ├── .env                     # ⚠️ Update with your password
│   ├── setup_postgres.py        # ✅ Automated setup script
│   └── requirements.txt         # ✅ psycopg2-binary included
│
├── POSTGRESQL_QUICK_START.md    # ⚡ Quick setup guide
├── POSTGRESQL_SETUP.md          # 📖 Detailed guide
├── POSTGRESQL_MIGRATION_COMPLETE.md  # ✅ Summary
└── PROJECT_ANALYSIS.md          # 📊 Project overview
```

---

## ✅ Configuration Status

### Completed
- ✅ PostgreSQL database configuration in `settings.py`
- ✅ Environment variable setup (`.env` template)
- ✅ Database models ready (User, OTP)
- ✅ Migrations ready to run
- ✅ Automated setup script created
- ✅ Comprehensive documentation

### Action Required
- ⚠️ Install PostgreSQL (if not installed)
- ⚠️ Create database `dealgoat_db`
- ⚠️ Update `.env` with PostgreSQL password
- ⚠️ Run migrations

---

## 🗄️ Database Models

### User Model
- Email-based authentication
- Profile fields (name, phone, location, gender, age)
- Email verification status
- Standard Django auth fields

### OTP Model
- 6-digit OTP codes
- 10-minute expiry
- Email verification tracking

---

## 🔧 Setup Options

### Option 1: Automated Setup (Recommended)
```bash
cd backend
python setup_postgres.py
```

### Option 2: Manual Setup
```bash
# 1. Create database
psql -U postgres -c "CREATE DATABASE dealgoat_db;"

# 2. Update .env with password

# 3. Run migrations
python manage.py migrate

# 4. Create superuser (optional)
python manage.py createsuperuser
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Password authentication failed | Update `DB_PASSWORD` in `.env` |
| Database does not exist | Run `CREATE DATABASE dealgoat_db;` |
| Could not connect to server | Check PostgreSQL service is running |
| psycopg2 not found | Run `pip install psycopg2-binary` |

For detailed troubleshooting, see **POSTGRESQL_SETUP.md**

---

## 📡 API Endpoints

All endpoints are ready to use with PostgreSQL:

- `POST /api/auth/register/` - User registration
- `POST /api/auth/send-otp/` - Send OTP
- `POST /api/auth/verify-otp/` - Verify OTP
- `POST /api/auth/complete-registration/` - Complete profile
- `GET /api/auth/check-email/` - Check email availability
- `POST /api/auth/login/` - User login

---

## 🎯 Next Steps

1. **Follow Quick Start** → `POSTGRESQL_QUICK_START.md`
2. **Run Setup Script** → `python backend/setup_postgres.py`
3. **Test Application** → Register a user, test OTP
4. **Configure Email** (optional) → See `backend/EMAIL_SETUP.md`

---

## 📝 Important Notes

1. **.env File**: 
   - Located in `backend/.env`
   - Contains sensitive credentials
   - Never commit to version control
   - Update `DB_PASSWORD` with your actual password

2. **Database Password**:
   - Default in template: `postgres` or `admin`
   - **Must be updated** with your actual PostgreSQL password

3. **Migrations**:
   - Already created and ready
   - Run with: `python manage.py migrate`
   - Creates all necessary tables

---

## 🔗 Related Documentation

- **Frontend Setup**: See main `README.md`
- **Email Configuration**: `backend/EMAIL_SETUP.md`
- **Project Overview**: `PROJECT_ANALYSIS.md`

---

## ✨ Summary

Your project is **100% ready for PostgreSQL**. All you need to do is:

1. Install PostgreSQL
2. Create the database
3. Update `.env` with your password
4. Run the setup script

**Everything else is already configured!** 🎉

---

**Status**: ✅ Ready for PostgreSQL Setup
**Next**: Follow `POSTGRESQL_QUICK_START.md`

