"""
Script to make a user an admin
Run this to fix "Access Denied" error
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dealgoat.settings')
django.setup()

from users.models import User

def make_admin():
    print("=" * 50)
    print("Make User Admin - Fix Access Denied")
    print("=" * 50)
    
    # Get user email
    email = input("\nEnter your email address: ").strip()
    
    try:
        # Find user
        user = User.objects.get(email=email)
        
        print(f"\n✓ Found user: {user.email}")
        print(f"  Current status:")
        print(f"    - is_staff: {user.is_staff}")
        print(f"    - is_superuser: {user.is_superuser}")
        
        # Make admin
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        print(f"\n✅ SUCCESS! {user.email} is now an admin!")
        print(f"  New status:")
        print(f"    - is_staff: {user.is_staff}")
        print(f"    - is_superuser: {user.is_superuser}")
        print(f"\n🎉 You can now access the admin dashboard at /admin")
        print(f"   Just refresh your browser!")
        
    except User.DoesNotExist:
        print(f"\n❌ ERROR: User with email '{email}' not found")
        print(f"\nAvailable users:")
        users = User.objects.all()[:5]
        for u in users:
            print(f"  - {u.email}")
        if User.objects.count() > 5:
            print(f"  ... and {User.objects.count() - 5} more")
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    make_admin()
