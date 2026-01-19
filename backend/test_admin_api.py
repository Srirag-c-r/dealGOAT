"""
Test admin dashboard API endpoint
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dealgoat.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.test import RequestFactory
from users.admin_views import admin_dashboard_stats

User = get_user_model()

print("=" * 60)
print("TESTING ADMIN DASHBOARD API")
print("=" * 60)

# Get admin user
try:
    admin_user = User.objects.get(email='sriragkeepsmiling@gmail.com')
    print(f"\n✓ Found user: {admin_user.email}")
    print(f"  is_staff: {admin_user.is_staff}")
    print(f"  is_superuser: {admin_user.is_superuser}")
    print(f"  is_active: {admin_user.is_active}")
    
    if not admin_user.is_staff and not admin_user.is_superuser:
        print("\n❌ ERROR: User is not an admin!")
        print("   Run: python admin_manager.py (option 5) to make user admin")
        exit(1)
    
    # Get or create token
    token, created = Token.objects.get_or_create(user=admin_user)
    print(f"\n✓ Token: {token.key}")
    if created:
        print("  (New token created)")
    
    # Test API endpoint
    print("\n" + "=" * 60)
    print("TESTING API ENDPOINT")
    print("=" * 60)
    
    factory = RequestFactory()
    request = factory.get('/api/users/admin/dashboard/stats/')
    request.user = admin_user
    
    response = admin_dashboard_stats(request)
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ API WORKING!")
        print("\nResponse data keys:")
        if hasattr(response, 'data'):
            for key in response.data.keys():
                print(f"  - {key}")
    else:
        print("❌ API ERROR!")
        if hasattr(response, 'data'):
            print(f"Error: {response.data}")
    
    # Test with curl command
    print("\n" + "=" * 60)
    print("TEST WITH CURL")
    print("=" * 60)
    print("\nRun this command in a new terminal:")
    print(f'\ncurl -H "Authorization: Token {token.key}" http://localhost:8000/api/users/admin/dashboard/stats/')
    
    # Test with browser
    print("\n" + "=" * 60)
    print("TEST IN BROWSER CONSOLE")
    print("=" * 60)
    print("\nOpen browser console (F12) and run:")
    print(f"""
fetch('http://localhost:8000/api/users/admin/dashboard/stats/', {{
  headers: {{
    'Authorization': 'Token {token.key}'
  }}
}})
.then(r => r.json())
.then(data => console.log('Success:', data))
.catch(err => console.error('Error:', err));
""")
    
    print("\n" + "=" * 60)
    print("FRONTEND CHECK")
    print("=" * 60)
    print("\nCheck localStorage in browser:")
    print("1. Open browser console (F12)")
    print("2. Go to Application/Storage tab")
    print("3. Check localStorage")
    print(f"4. Verify 'token' = '{token.key}'")
    print("\nIf token doesn't match, logout and login again!")
    
except User.DoesNotExist:
    print(f"\n❌ User 'sriragkeepsmiling@gmail.com' not found!")
    print("\nAvailable admin users:")
    admins = User.objects.filter(is_staff=True) | User.objects.filter(is_superuser=True)
    for admin in admins:
        print(f"  - {admin.email}")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
