#!/usr/bin/env python
"""
PostgreSQL Setup Script for DealGoat
This script helps set up the PostgreSQL database for the project.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the backend directory to the path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dealgoat.settings')

import django
django.setup()

from django.conf import settings
from django.db import connection
from django.core.management import call_command


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def print_success(text):
    """Print success message"""
    print(f"✅ {text}")


def print_error(text):
    """Print error message"""
    print(f"❌ {text}")


def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")


def check_postgresql_installed():
    """Check if PostgreSQL is installed"""
    print_header("Checking PostgreSQL Installation")
    
    try:
        result = subprocess.run(
            ['psql', '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print_success(f"PostgreSQL found: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print_error("PostgreSQL not found in PATH")
    print_info("Please install PostgreSQL from: https://www.postgresql.org/download/")
    return False


def check_database_connection():
    """Check if we can connect to the database"""
    print_header("Checking Database Connection")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print_success("Database connection successful!")
            print_info(f"PostgreSQL version: {version.split(',')[0]}")
            return True
    except Exception as e:
        print_error(f"Database connection failed: {str(e)}")
        print_info("Please check your .env file configuration:")
        print_info("  - DB_NAME")
        print_info("  - DB_USER")
        print_info("  - DB_PASSWORD")
        print_info("  - DB_HOST")
        print_info("  - DB_PORT")
        return False


def check_database_exists():
    """Check if the database exists"""
    print_header("Checking Database Existence")
    
    db_name = settings.DATABASES['default']['NAME']
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                [db_name]
            )
            exists = cursor.fetchone() is not None
            
            if exists:
                print_success(f"Database '{db_name}' exists")
                return True
            else:
                print_error(f"Database '{db_name}' does not exist")
                print_info(f"Please create the database:")
                print_info(f"  psql -U postgres")
                print_info(f"  CREATE DATABASE {db_name};")
                return False
    except Exception as e:
        print_error(f"Error checking database: {str(e)}")
        return False


def list_tables():
    """List all tables in the database"""
    print_header("Listing Database Tables")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            if tables:
                print_success(f"Found {len(tables)} table(s):")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print_info("No tables found. Run migrations to create tables.")
            return True
    except Exception as e:
        print_error(f"Error listing tables: {str(e)}")
        return False


def run_migrations():
    """Run Django migrations"""
    print_header("Running Database Migrations")
    
    try:
        call_command('migrate', verbosity=1, interactive=False)
        print_success("Migrations completed successfully!")
        return True
    except Exception as e:
        print_error(f"Migration failed: {str(e)}")
        return False


def check_env_file():
    """Check if .env file exists and has required variables"""
    print_header("Checking Environment Configuration")
    
    env_file = BASE_DIR / '.env'
    
    if not env_file.exists():
        print_error(".env file not found")
        print_info("Creating .env file from template...")
        
        template_file = BASE_DIR / 'env_template.txt'
        if template_file.exists():
            import shutil
            shutil.copy(template_file, env_file)
            print_success(".env file created from template")
            print_info("Please update the .env file with your PostgreSQL credentials")
            return False
        else:
            print_error("env_template.txt not found")
            return False
    
    print_success(".env file exists")
    
    # Check required variables
    required_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
    missing_vars = []
    
    from decouple import AutoConfig
    config = AutoConfig(search_path=str(BASE_DIR))
    
    for var in required_vars:
        value = config(var, default=None)
        if value is None or value == '':
            missing_vars.append(var)
    
    if missing_vars:
        print_error(f"Missing required variables: {', '.join(missing_vars)}")
        print_info("Please update your .env file")
        return False
    
    print_success("All required environment variables are set")
    return True


def main():
    """Main setup function"""
    print_header("DealGoat PostgreSQL Setup")
    
    # Step 1: Check .env file
    if not check_env_file():
        print("\n⚠️  Please configure your .env file and run this script again.")
        return False
    
    # Step 2: Check PostgreSQL installation (optional, may not be in PATH)
    # check_postgresql_installed()
    
    # Step 3: Check database connection
    if not check_database_connection():
        print("\n⚠️  Please fix database connection issues and run this script again.")
        return False
    
    # Step 4: Check if database exists
    if not check_database_exists():
        print("\n⚠️  Please create the database and run this script again.")
        return False
    
    # Step 5: Run migrations
    if not run_migrations():
        print("\n⚠️  Migrations failed. Please check the error messages above.")
        return False
    
    # Step 6: List tables
    list_tables()
    
    print_header("Setup Complete!")
    print_success("PostgreSQL database is ready to use!")
    print_info("Next steps:")
    print_info("  1. Create a superuser: python manage.py createsuperuser")
    print_info("  2. Start the server: python manage.py runserver")
    print_info("  3. Access admin panel: http://localhost:8000/admin/")
    
    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

