# Production Settings for DealGoat Admin Dashboard

## Security Enhancements

### 1. Environment Variables
Create `.env` file (never commit to git):
```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=dealgoat_prod
DB_USER=dealgoat_user
DB_PASSWORD=strong-password-here
DB_HOST=localhost
DB_PORT=5432

# Redis (for caching and rate limiting)
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email (for notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# Admin
ADMIN_SESSION_TIMEOUT=3600
ADMIN_MAX_LOGIN_ATTEMPTS=5
ADMIN_IP_WHITELIST=192.168.1.1,10.0.0.1
```

### 2. Update settings.py

Add to `backend/dealgoat/settings.py`:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Security
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# HTTPS Settings (Production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Admin Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Admin custom middleware
    'users.admin_middleware.AdminRateLimitMiddleware',
    'users.admin_middleware.AdminSecurityHeadersMiddleware',
    'users.admin_middleware.AdminRequestLoggingMiddleware',
]

# Caching (Redis)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session Settings
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = int(os.getenv('ADMIN_SESSION_TIMEOUT', 3600))

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/admin.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'users.admin_views': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'predictions.admin_views': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### 3. Install Production Dependencies

```bash
pip install python-dotenv django-redis psycopg2-binary gunicorn whitenoise
```

Update `requirements.txt`:
```
Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.0
python-dotenv==1.0.0
django-redis==5.4.0
psycopg2-binary==2.9.9
gunicorn==21.2.0
whitenoise==6.6.0
```

## Deployment Checklist

### Backend Deployment

1. **Database Migration**
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

2. **Create Superuser**
```bash
python manage.py createsuperuser
```

3. **Run with Gunicorn**
```bash
gunicorn dealgoat.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

4. **Setup Nginx (Reverse Proxy)**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/media/;
    }
}
```

### Frontend Deployment

1. **Build for Production**
```bash
npm run build
```

2. **Environment Variables**
Create `.env.production`:
```
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_APP_NAME=DealGoat Admin
VITE_DEBUG_MODE=false
```

3. **Deploy to Netlify/Vercel**
```bash
# Netlify
netlify deploy --prod

# Vercel
vercel --prod
```

## Monitoring & Maintenance

### 1. Error Tracking
- Integrate Sentry for error tracking
- Monitor admin action logs
- Set up alerts for suspicious activity

### 2. Performance Monitoring
- Use Django Debug Toolbar (development only)
- Monitor API response times
- Track database query performance

### 3. Security Audits
- Regular dependency updates
- Penetration testing
- Review admin action logs weekly

### 4. Backup Strategy
- Daily database backups
- Weekly full system backups
- Test restore procedures monthly

## Production Best Practices

### ✅ Implemented
- Protected admin routes with authentication
- Centralized API service with interceptors
- Error boundaries for graceful error handling
- Rate limiting on admin endpoints
- Security headers (XSS, Clickjacking, etc.)
- Request logging for audit trail
- Environment-based configuration

### 🔄 Recommended
- Two-factor authentication (2FA)
- IP whitelisting for admin access
- Automated backup system
- Real-time monitoring dashboard
- Email notifications for critical actions
- API request/response encryption
- Database connection pooling
- CDN for static assets

### 📊 Monitoring Tools
- **Backend**: Sentry, New Relic, DataDog
- **Frontend**: LogRocket, Sentry
- **Infrastructure**: Prometheus, Grafana
- **Uptime**: UptimeRobot, Pingdom

## Performance Optimization

### Backend
- Enable database query caching
- Use Redis for session storage
- Implement pagination on all list endpoints
- Add database indexes on frequently queried fields
- Use select_related() and prefetch_related()

### Frontend
- Code splitting with React.lazy()
- Image optimization and lazy loading
- Implement virtual scrolling for large tables
- Use React.memo() for expensive components
- Enable service workers for offline support

## Security Hardening

### Django
```python
# Additional security settings
SECURE_REFERRER_POLICY = 'same-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
CSRF_COOKIE_HTTPONLY = True
CSRF_USE_SESSIONS = True
```

### Nginx
```nginx
# Security headers
add_header X-Frame-Options "DENY";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
add_header Referrer-Policy "no-referrer-when-downgrade";
```

## Scaling Considerations

### Horizontal Scaling
- Load balancer (Nginx, HAProxy)
- Multiple application servers
- Database replication (master-slave)
- Redis cluster for caching

### Vertical Scaling
- Increase server resources
- Optimize database queries
- Implement caching strategies
- Use CDN for static files

---

**Your admin dashboard is now production-ready!** 🚀
