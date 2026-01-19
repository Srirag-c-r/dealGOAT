"""
Utility functions for admin dashboard
"""
from users.models import AdminActionLog
from recommendations.models import SystemMetric
from django.utils import timezone


def log_admin_action(admin_user, action_type, target_model, target_id, description, request=None, **metadata):
    """
    Helper function to log admin actions.
    
    Args:
        admin_user: User object of the admin performing the action
        action_type: Type of action (from AdminActionLog.ACTION_TYPES)
        target_model: Name of the model being affected
        target_id: ID of the affected object
        description: Detailed description of the action
        request: Django request object (optional, for IP and user agent)
        **metadata: Additional data to store
    
    Returns:
        AdminActionLog instance
    """
    return AdminActionLog.log_action(
        admin_user=admin_user,
        action_type=action_type,
        target_model=target_model,
        target_id=target_id,
        description=description,
        request=request,
        **metadata
    )


def record_metric(metric_name, metric_value, metric_type='gauge', **metadata):
    """
    Helper function to record system metrics.
    
    Args:
        metric_name: Name of the metric
        metric_value: Numeric value
        metric_type: Type of metric (counter, gauge, histogram, timing)
        **metadata: Additional metric data
    
    Returns:
        SystemMetric instance
    """
    return SystemMetric.record(
        metric_name=metric_name,
        metric_value=metric_value,
        metric_type=metric_type,
        **metadata
    )


def check_admin_permission(user, required_role='staff'):
    """
    Check if user has required admin permission.
    
    Args:
        user: User object
        required_role: 'superuser', 'moderator', or 'staff'
    
    Returns:
        bool: True if user has permission
    """
    if not user or not user.is_authenticated:
        return False
    
    if required_role == 'superuser':
        return user.is_superuser
    elif required_role == 'moderator':
        return user.is_superuser or user.groups.filter(name='Moderator').exists()
    elif required_role == 'staff':
        return user.is_staff
    
    return False


def get_client_ip(request):
    """
    Get client IP address from request.
    
    Args:
        request: Django request object
    
    Returns:
        str: IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def format_duration(seconds):
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        str: Formatted duration (e.g., "2h 30m", "45s")
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"


def calculate_percentage_change(current, previous):
    """
    Calculate percentage change between two values.
    
    Args:
        current: Current value
        previous: Previous value
    
    Returns:
        float: Percentage change (positive for increase, negative for decrease)
    """
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    
    return ((current - previous) / previous) * 100
