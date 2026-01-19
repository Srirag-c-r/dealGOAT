"""
Admin User Management Script
Check all admin users, their status, and permissions
"""
import os
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dealgoat.settings')
django.setup()

from users.models import User, AdminActionLog
from django.db.models import Count, Q

def print_separator(char='=', length=80):
    """Print a separator line"""
    print(char * length)

def print_header(title):
    """Print a formatted header"""
    print_separator()
    print(f"  {title}")
    print_separator()

def display_all_admins():
    """Display all admin users with their details"""
    print_header("ALL ADMIN USERS")
    
    # Get all admin users (staff or superuser)
    admins = User.objects.filter(
        Q(is_staff=True) | Q(is_superuser=True)
    ).order_by('-is_superuser', '-is_staff', 'email')
    
    if not admins.exists():
        print("\n❌ No admin users found!")
        print("   Run 'python manage.py createsuperuser' to create one.\n")
        return
    
    print(f"\n📊 Total Admin Users: {admins.count()}\n")
    
    for i, admin in enumerate(admins, 1):
        print(f"{i}. {admin.email}")
        print(f"   {'─' * 60}")
        print(f"   Name:          {admin.first_name} {admin.last_name}")
        print(f"   Superuser:     {'✅ Yes' if admin.is_superuser else '❌ No'}")
        print(f"   Staff:         {'✅ Yes' if admin.is_staff else '❌ No'}")
        print(f"   Active:        {'✅ Yes' if admin.is_active else '❌ No'}")
        print(f"   Suspended:     {'⚠️  Yes' if admin.is_suspended else '✅ No'}")
        print(f"   Email Verified: {'✅ Yes' if admin.email_verified else '❌ No'}")
        print(f"   Joined:        {admin.date_joined.strftime('%Y-%m-%d %H:%M')}")
        
        if admin.last_login:
            print(f"   Last Login:    {admin.last_login.strftime('%Y-%m-%d %H:%M')}")
        else:
            print(f"   Last Login:    Never")
        
        # Get admin action count
        action_count = AdminActionLog.objects.filter(admin_user=admin).count()
        print(f"   Admin Actions: {action_count}")
        
        if admin.is_suspended:
            print(f"   Suspension Reason: {admin.suspension_reason}")
            print(f"   Suspended At: {admin.suspended_at.strftime('%Y-%m-%d %H:%M') if admin.suspended_at else 'N/A'}")
        
        print()

def display_regular_users():
    """Display regular (non-admin) users"""
    print_header("REGULAR USERS (Non-Admin)")
    
    regular_users = User.objects.filter(
        is_staff=False, 
        is_superuser=False
    ).order_by('-date_joined')[:10]
    
    if not regular_users.exists():
        print("\n❌ No regular users found!\n")
        return
    
    total_regular = User.objects.filter(is_staff=False, is_superuser=False).count()
    print(f"\n📊 Total Regular Users: {total_regular}")
    print(f"   Showing latest 10:\n")
    
    for i, user in enumerate(regular_users, 1):
        status = "✅ Active" if user.is_active else "❌ Inactive"
        verified = "✅" if user.email_verified else "❌"
        suspended = "⚠️ SUSPENDED" if user.is_suspended else ""
        
        print(f"{i}. {user.email:40} | {status:12} | Verified: {verified} {suspended}")

def display_user_statistics():
    """Display user statistics"""
    print_header("USER STATISTICS")
    
    total_users = User.objects.count()
    superusers = User.objects.filter(is_superuser=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    active_users = User.objects.filter(is_active=True).count()
    verified_users = User.objects.filter(email_verified=True).count()
    suspended_users = User.objects.filter(is_suspended=True).count()
    
    print(f"""
    Total Users:        {total_users}
    Superusers:         {superusers}
    Staff Users:        {staff_users}
    Active Users:       {active_users}
    Verified Users:     {verified_users}
    Suspended Users:    {suspended_users}
    Regular Users:      {total_users - staff_users}
    """)

def display_recent_admin_actions():
    """Display recent admin actions"""
    print_header("RECENT ADMIN ACTIONS (Last 10)")
    
    recent_actions = AdminActionLog.objects.select_related('admin_user').order_by('-created_at')[:10]
    
    if not recent_actions.exists():
        print("\n❌ No admin actions recorded yet!\n")
        return
    
    print()
    for i, action in enumerate(recent_actions, 1):
        admin_email = action.admin_user.email if action.admin_user else "System"
        timestamp = action.created_at.strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i}. [{timestamp}] {action.get_action_type_display()}")
        print(f"   Admin: {admin_email}")
        print(f"   Target: {action.target_model} #{action.target_id if action.target_id else 'N/A'}")
        if action.description:
            print(f"   Description: {action.description}")
        print()

def make_user_admin():
    """Interactive function to make a user admin"""
    print_header("MAKE USER ADMIN")
    
    email = input("\nEnter user email: ").strip()
    
    try:
        user = User.objects.get(email=email)
        
        print(f"\n✓ Found user: {user.email}")
        print(f"  Current status:")
        print(f"    - is_staff: {user.is_staff}")
        print(f"    - is_superuser: {user.is_superuser}")
        
        print("\nWhat type of admin access?")
        print("1. Superuser (full access)")
        print("2. Staff only (limited access)")
        print("3. Remove admin access")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            user.is_staff = True
            user.is_superuser = True
            user.save()
            print(f"\n✅ {user.email} is now a SUPERUSER!")
        elif choice == '2':
            user.is_staff = True
            user.is_superuser = False
            user.save()
            print(f"\n✅ {user.email} is now STAFF!")
        elif choice == '3':
            user.is_staff = False
            user.is_superuser = False
            user.save()
            print(f"\n✅ Admin access removed from {user.email}")
        else:
            print("\n❌ Invalid choice!")
            return
        
        print(f"  New status:")
        print(f"    - is_staff: {user.is_staff}")
        print(f"    - is_superuser: {user.is_superuser}")
        
    except User.DoesNotExist:
        print(f"\n❌ User with email '{email}' not found!")
        print("\nAvailable users:")
        users = User.objects.all()[:10]
        for u in users:
            print(f"  - {u.email}")

def search_user():
    """Search for a user by email"""
    print_header("SEARCH USER")
    
    query = input("\nEnter email or name to search: ").strip()
    
    users = User.objects.filter(
        Q(email__icontains=query) | 
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query)
    )[:20]
    
    if not users.exists():
        print(f"\n❌ No users found matching '{query}'")
        return
    
    print(f"\n✓ Found {users.count()} user(s):\n")
    
    for i, user in enumerate(users, 1):
        admin_badge = ""
        if user.is_superuser:
            admin_badge = " [SUPERUSER]"
        elif user.is_staff:
            admin_badge = " [STAFF]"
        
        print(f"{i}. {user.email}{admin_badge}")
        print(f"   Name: {user.first_name} {user.last_name}")
        print(f"   Active: {'✅' if user.is_active else '❌'} | Verified: {'✅' if user.email_verified else '❌'}")
        print()

def main_menu():
    """Display main menu and handle user choice"""
    while True:
        print_separator('=')
        print("  DEALGOAT ADMIN USER MANAGEMENT")
        print_separator('=')
        print("\n1. View All Admins")
        print("2. View Regular Users")
        print("3. View User Statistics")
        print("4. View Recent Admin Actions")
        print("5. Make User Admin")
        print("6. Search User")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        print()
        
        if choice == '1':
            display_all_admins()
        elif choice == '2':
            display_regular_users()
        elif choice == '3':
            display_user_statistics()
        elif choice == '4':
            display_recent_admin_actions()
        elif choice == '5':
            make_user_admin()
        elif choice == '6':
            search_user()
        elif choice == '7':
            print("👋 Goodbye!\n")
            break
        else:
            print("❌ Invalid choice! Please enter 1-7.\n")
        
        input("\nPress Enter to continue...")
        print("\n" * 2)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
