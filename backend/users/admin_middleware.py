"""
Production-ready middleware for admin dashboard
"""
from django.conf import settings
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
import time


class AdminRateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware for admin endpoints
    Prevents abuse and DDoS attacks
    """
    
    def process_request(self, request):
        # Only apply to admin endpoints
        if not request.path.startswith('/api/') or '/admin/' not in request.path:
            return None
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Rate limit key
        cache_key = f'admin_rate_limit_{ip}'
        
        # Get request count
        request_count = cache.get(cache_key, 0)
        
        # Limit: 100 requests per minute
        if request_count >= 100:
            return JsonResponse({
                'error': 'Rate limit exceeded. Please try again later.'
            }, status=429)
        
        # Increment counter
        cache.set(cache_key, request_count + 1, 60)  # 60 seconds TTL
        
        return None


class AdminSecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to admin responses
    """
    
    def process_response(self, request, response):
        # Only apply to admin endpoints
        if request.path.startswith('/api/') and '/admin/' in request.path:
            # Prevent clickjacking
            response['X-Frame-Options'] = 'DENY'
            
            # Prevent MIME type sniffing
            response['X-Content-Type-Options'] = 'nosniff'
            
            # Enable XSS protection
            response['X-XSS-Protection'] = '1; mode=block'
            
            # Strict Transport Security (HTTPS only)
            if settings.DEBUG is False:
                response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            # Content Security Policy
            response['Content-Security-Policy'] = "default-src 'self'"
        
        return response


class AdminRequestLoggingMiddleware(MiddlewareMixin):
    """
    Log all admin requests for audit trail
    """
    
    def process_request(self, request):
        # Store request start time
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        # Only log admin endpoints
        if not (request.path.startswith('/api/') and '/admin/' in request.path):
            return response
        
        # Calculate request duration
        duration = time.time() - getattr(request, '_start_time', time.time())
        
        # Log request details (in production, send to logging service)
        if settings.DEBUG:
            print(f"[ADMIN] {request.method} {request.path} - {response.status_code} - {duration:.2f}s")
        
        # In production, you would send this to a logging service like:
        # logger.info(f"Admin request: {request.method} {request.path}", extra={
        #     'user': request.user.email if request.user.is_authenticated else 'anonymous',
        #     'status_code': response.status_code,
        #     'duration': duration,
        #     'ip': get_client_ip(request),
        # })
        
        return response
