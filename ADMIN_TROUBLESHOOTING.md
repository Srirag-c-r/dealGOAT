# Admin Dashboard Troubleshooting Guide

## Issue: "Failed to fetch dashboard stats"

### Root Cause
The login API was updated to include `is_staff` and `is_superuser` fields, but your browser has cached old user data without these fields.

### Solution

**Step 1: Logout**
- Click the logout button in the admin sidebar
- OR go to `/login` and clear localStorage

**Step 2: Login Again**
- Email: `sriragkeepsmiling@gmail.com`
- Password: [your password]

**Step 3: Access Admin**
- Navigate to `http://localhost:5173/admin`
- Dashboard should now load successfully

### Alternative: Clear Cache Manually

Open browser console (F12) and run:
```javascript
localStorage.clear();
location.reload();
```

Then login again.

### Verify Backend is Working

Test the API directly:
```bash
cd backend
python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dealgoat.settings'); django.setup(); from django.test import RequestFactory; from users.admin_views import admin_dashboard_stats; from users.models import User; factory = RequestFactory(); request = factory.get('/api/users/admin/dashboard/stats/'); request.user = User.objects.filter(is_staff=True).first(); response = admin_dashboard_stats(request); print('Status:', response.status_code)"
```

Should show: `Status: 200`

### Still Not Working?

Check browser console (F12) for detailed error messages. The updated dashboard now shows:
- Token status
- Connection errors
- Permission issues
- Troubleshooting steps

**The fix is simple: Logout and login again!**
