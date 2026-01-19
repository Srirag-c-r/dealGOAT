"""
Admin Management Utility for DealGoat
======================================

This script allows you to:
1. View all admin users (staff and superusers)
2. Create new admin users
3. Promote users to admin/superadmin
4. Demote admin users to regular users
5. Delete admin users

Usage:
    python manage_admins.py list
    python manage_admins.py create <email> <password> [--superadmin]
    python manage_admins.py promote <email> [--superadmin]
    python manage_admins.py demote <email>
    python manage_admins.py delete <email>
"""

import os
import sys
import django
from getpass import getpass

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dealgoat.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


def list_admins():
    """List all admin users."""
    print("\n" + "="*80)
    print("DEALGOAT ADMIN USERS")
    print("="*80 + "\n")
    
    # Get all staff users
    admins = User.objects.filter(is_staff=True).order_by('-is_superuser', 'email')
    
    if not admins.exists():
        print("❌ No admin users found!")
        return
    
    print(f"Total Admin Users: {admins.count()}\n")
    
    # Table header
    print(f"{'ID':<5} {'EMAIL':<35} {'NAME':<25} {'TYPE':<15} {'STATUS':<10}")
    print("-" * 95)
    
    for admin in admins:
        admin_type = "🔴 SUPER ADMIN" if admin.is_superuser else "🟡 ADMIN"
        status = "✅ Active" if not admin.is_suspended else "❌ Suspended"
        name = f"{admin.first_name} {admin.last_name}".strip() or "N/A"
        
        print(f"{admin.id:<5} {admin.email:<35} {name:<25} {admin_type:<15} {status:<10}")
    
    print("\n" + "="*80 + "\n")
    
    # Summary
    super_admins = admins.filter(is_superuser=True).count()
    regular_admins = admins.filter(is_staff=True, is_superuser=False).count()
    
    print(f"Summary:")
    print(f"  🔴 Super Admins: {super_admins}")
    print(f"  🟡 Regular Admins: {regular_admins}")
    print()


def create_admin(email, password=None, first_name='', last_name='', is_superuser=False):
    """Create a new admin user."""
    try:
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            print(f"❌ User with email {email} already exists!")
            existing_user = User.objects.get(email=email)
            if existing_user.is_staff:
                print(f"   This user is already an admin.")
            else:
                print(f"   Use 'promote' command to make this user an admin.")
            return False
        
        # Get password if not provided
        if not password:
            password = getpass("Enter password: ")
            password_confirm = getpass("Confirm password: ")
            if password != password_confirm:
                print("❌ Passwords don't match!")
                return False
        
        # Create user
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
            is_superuser=is_superuser,
            email_verified=True  # Auto-verify admin accounts
        )
        
        admin_type = "Super Admin" if is_superuser else "Admin"
        print(f"✅ {admin_type} created successfully!")
        print(f"   Email: {email}")
        print(f"   ID: {user.id}")
        return True
        
    except IntegrityError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        return False


def promote_user(email, to_superuser=False):
    """Promote a user to admin or superadmin."""
    try:
        user = User.objects.get(email=email)
        
        if user.is_superuser:
            print(f"ℹ️  User {email} is already a Super Admin!")
            return False
        
        if user.is_staff and not to_superuser:
            print(f"ℹ️  User {email} is already an Admin!")
            print(f"   Use --superadmin flag to promote to Super Admin.")
            return False
        
        # Promote user
        user.is_staff = True
        if to_superuser:
            user.is_superuser = True
        user.save()
        
        new_role = "Super Admin" if to_superuser else "Admin"
        print(f"✅ User promoted to {new_role}!")
        print(f"   Email: {email}")
        print(f"   ID: {user.id}")
        return True
        
    except User.DoesNotExist:
        print(f"❌ User with email {email} not found!")
        return False
    except Exception as e:
        print(f"❌ Error promoting user: {e}")
        return False


def demote_user(email):
    """Demote an admin user to regular user."""
    try:
        user = User.objects.get(email=email)
        
        if not user.is_staff:
            print(f"ℹ️  User {email} is not an admin!")
            return False
        
        # Confirm action
        confirm = input(f"⚠️  Are you sure you want to demote {email}? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Action cancelled.")
            return False
        
        # Demote user
        user.is_staff = False
        user.is_superuser = False
        user.save()
        
        print(f"✅ User demoted to regular user!")
        print(f"   Email: {email}")
        return True
        
    except User.DoesNotExist:
        print(f"❌ User with email {email} not found!")
        return False
    except Exception as e:
        print(f"❌ Error demoting user: {e}")
        return False


def delete_admin(email):
    """Delete an admin user."""
    try:
        user = User.objects.get(email=email)
        
        if not user.is_staff:
            print(f"⚠️  Warning: {email} is not an admin user!")
        
        # Confirm action
        print(f"\n⚠️  WARNING: This will permanently delete the user!")
        print(f"   Email: {email}")
        print(f"   Name: {user.first_name} {user.last_name}")
        print(f"   Admin: {'Yes' if user.is_staff else 'No'}")
        print(f"   Super Admin: {'Yes' if user.is_superuser else 'No'}\n")
        
        confirm = input("Type 'DELETE' to confirm: ")
        if confirm != 'DELETE':
            print("❌ Action cancelled.")
            return False
        
        # Delete user
        user.delete()
        
        print(f"✅ User deleted successfully!")
        return True
        
    except User.DoesNotExist:
        print(f"❌ User with email {email} not found!")
        return False
    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        return False


def print_help():
    """Print help message."""
    print(__doc__)
    print("\nExamples:")
    print("  python manage_admins.py list")
    print("  python manage_admins.py create admin@dealgoat.com mypassword123")
    print("  python manage_admins.py create superadmin@dealgoat.com --superadmin")
    print("  python manage_admins.py promote user@example.com")
    print("  python manage_admins.py promote user@example.com --superadmin")
    print("  python manage_admins.py demote admin@dealgoat.com")
    print("  python manage_admins.py delete user@example.com")
    print()


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_admins()
    
    elif command == 'create':
        if len(sys.argv) < 3:
            print("❌ Error: Email required!")
            print("Usage: python manage_admins.py create <email> [password] [--superadmin]")
            return
        
        email = sys.argv[2]
        password = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else None
        is_superuser = '--superadmin' in sys.argv
        
        create_admin(email, password, is_superuser=is_superuser)
    
    elif command == 'promote':
        if len(sys.argv) < 3:
            print("❌ Error: Email required!")
            print("Usage: python manage_admins.py promote <email> [--superadmin]")
            return
        
        email = sys.argv[2]
        to_superuser = '--superadmin' in sys.argv
        
        promote_user(email, to_superuser)
    
    elif command == 'demote':
        if len(sys.argv) < 3:
            print("❌ Error: Email required!")
            print("Usage: python manage_admins.py demote <email>")
            return
        
        email = sys.argv[2]
        demote_user(email)
    
    elif command == 'delete':
        if len(sys.argv) < 3:
            print("❌ Error: Email required!")
            print("Usage: python manage_admins.py delete <email>")
            return
        
        email = sys.argv[2]
        delete_admin(email)
    
    elif command in ['help', '-h', '--help']:
        print_help()
    
    else:
        print(f"❌ Unknown command: {command}")
        print_help()


if __name__ == '__main__':
    main()
