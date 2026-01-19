# PostgreSQL Setup Guide for DealGoat

This guide will help you set up PostgreSQL database for the DealGoat project.

---

## 📋 Prerequisites

1. **PostgreSQL installed** on your system
   - Download: https://www.postgresql.org/download/
   - Windows: Use the official installer
   - Linux: `sudo apt-get install postgresql postgresql-contrib` (Ubuntu/Debian)
   - Mac: `brew install postgresql` or use Postgres.app

2. **Python virtual environment** activated
3. **All Python dependencies** installed (`pip install -r requirements.txt`)

---

## 🔧 Step 1: Install PostgreSQL (if not installed)

### Windows
1. Download PostgreSQL installer from https://www.postgresql.org/download/windows/
2. Run the installer
3. **Remember the password** you set for the `postgres` user
4. Default port is `5432`

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Mac
```bash
brew install postgresql
brew services start postgresql
```

---

## 🗄️ Step 2: Create PostgreSQL Database

### Option A: Using psql Command Line

1. **Open PostgreSQL command line**:
   ```bash
   # Windows: Open Command Prompt or PowerShell
   psql -U postgres
   
   # Linux/Mac: Use terminal
   sudo -u postgres psql
   ```

2. **Create database**:
   ```sql
   CREATE DATABASE dealgoat_db;
   ```

3. **Verify database creation**:
   ```sql
   \l
   ```
   You should see `dealgoat_db` in the list.

4. **Exit psql**:
   ```sql
   \q
   ```

### Option B: Using pgAdmin (GUI)

1. Open **pgAdmin 4**
2. Connect to your PostgreSQL server
3. Right-click on **Databases** → **Create** → **Database**
4. Name: `dealgoat_db`
5. Click **Save**

### Option C: Using Python Script

Run the provided setup script:
```bash
cd backend
python setup_postgres.py
```

---

## ⚙️ Step 3: Configure Environment Variables

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create .env file** (if it doesn't exist):
   ```bash
   # Windows
   copy env_template.txt .env
   
   # Linux/Mac
   cp env_template.txt .env
   ```

3. **Edit .env file** and update PostgreSQL settings:
   ```env
   # Database Configuration
   DB_NAME=dealgoat_db
   DB_USER=postgres
   DB_PASSWORD=your_actual_postgres_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

   **Important**: Replace `your_actual_postgres_password` with the password you set during PostgreSQL installation.

---

## 🔍 Step 4: Verify Database Connection

### Test Connection Manually

```bash
cd backend
python manage.py dbshell
```

If successful, you'll see the PostgreSQL prompt. Type `\q` to exit.

### Test Connection via Django

```bash
cd backend
python manage.py check --database default
```

You should see: `System check identified no issues (0 silenced).`

---

## 🚀 Step 5: Run Database Migrations

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

   This will create all necessary tables in PostgreSQL:
   - `users` table (custom user model)
   - `otps` table (OTP verification)
   - Django auth tables (groups, permissions, etc.)
   - Django admin tables

3. **Verify tables were created**:
   ```bash
   python manage.py dbshell
   ```
   Then in PostgreSQL:
   ```sql
   \dt
   ```
   You should see tables like `users`, `otps`, `django_migrations`, etc.

---

## 👤 Step 6: Create Superuser (Optional)

Create an admin user to access Django admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts:
- Email: your-email@example.com
- Password: (enter a secure password)
- First Name: Admin
- Last Name: User

---

## ✅ Step 7: Verify Setup

1. **Start Django server**:
   ```bash
   python manage.py runserver
   ```

2. **Test API endpoints**:
   - Open: http://localhost:8000/api/auth/check-email/?email=test@example.com
   - Should return: `{"available": true, "message": "Email is available"}`

3. **Access Django Admin** (if superuser created):
   - Open: http://localhost:8000/admin/
   - Login with superuser credentials

---

## 🐛 Troubleshooting

### Issue: "FATAL: password authentication failed"

**Solution**:
1. Check your `.env` file - ensure `DB_PASSWORD` is correct
2. Try resetting PostgreSQL password:
   ```sql
   ALTER USER postgres PASSWORD 'new_password';
   ```
3. Update `.env` with the new password

### Issue: "FATAL: database 'dealgoat_db' does not exist"

**Solution**:
1. Create the database (see Step 2)
2. Verify database name in `.env` matches the created database

### Issue: "could not connect to server"

**Solution**:
1. Ensure PostgreSQL service is running:
   - Windows: Check Services → PostgreSQL
   - Linux: `sudo systemctl status postgresql`
   - Mac: `brew services list`
2. Check `DB_HOST` and `DB_PORT` in `.env`
3. Verify PostgreSQL is listening on port 5432

### Issue: "psycopg2" module not found

**Solution**:
```bash
pip install psycopg2-binary
```

### Issue: "permission denied for database"

**Solution**:
1. Grant permissions to your user:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE dealgoat_db TO postgres;
   ```

---

## 📊 Database Schema Overview

After running migrations, your PostgreSQL database will have:

### Main Tables

1. **users** - Custom user model
   - Primary key: `id`
   - Unique: `email`
   - Indexes: On `email`

2. **otps** - OTP verification codes
   - Primary key: `id`
   - Indexes: On `['email', 'is_used']`

3. **django_migrations** - Migration history
4. **django_content_type** - Content types
5. **auth_group**, **auth_permission** - Django auth system
6. **django_session** - Session storage
7. **django_admin_log** - Admin action logs

### View All Tables

```sql
\dt
```

### View Table Structure

```sql
\d users
\d otps
```

---

## 🔄 Migrating from SQLite to PostgreSQL

If you have existing SQLite data:

1. **Export data**:
   ```bash
   python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data.json
   ```

2. **Follow Steps 1-5** above to set up PostgreSQL

3. **Load data**:
   ```bash
   python manage.py loaddata data.json
   ```

**Note**: You may need to adjust the data export/import if there are foreign key constraints.

---

## 🎯 Quick Setup Checklist

- [ ] PostgreSQL installed
- [ ] Database `dealgoat_db` created
- [ ] `.env` file configured with correct credentials
- [ ] Database connection tested
- [ ] Migrations run successfully
- [ ] Superuser created (optional)
- [ ] Django server starts without errors
- [ ] API endpoints working

---

## 📝 Environment Variables Reference

Complete `.env` file structure:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# PostgreSQL Database
DB_NAME=dealgoat_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration (Optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

---

## 🚀 Next Steps

After PostgreSQL setup:

1. **Configure Email** (optional): See `backend/EMAIL_SETUP.md`
2. **Start Development**:
   ```bash
   # Backend
   cd backend
   python manage.py runserver
   
   # Frontend (in another terminal)
   npm run dev
   ```
3. **Test Registration Flow**: Register a new user through the frontend

---

## 📚 Additional Resources

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Django Database Setup: https://docs.djangoproject.com/en/4.2/ref/databases/
- psycopg2 Documentation: https://www.psycopg.org/docs/

---

**Need Help?** Check the troubleshooting section or review the error messages carefully. Most issues are related to incorrect credentials or PostgreSQL service not running.

