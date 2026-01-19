"""
Initialize default system settings for DealGoat admin panel.
Run this script to populate the SystemConfiguration table with default values.

Usage:
    python manage.py shell < initialize_settings.py
    OR
    python initialize_settings.py
"""

import os
import sys
import django

# Setup Django environment
if __name__ == '__main__':
    # Add the project directory to the path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dealgoat.settings')
    django.setup()

from recommendations.models import SystemConfiguration

def initialize_settings():
    """Create default system settings if they don't exist."""
    
    default_settings = [
        # System Settings
        {
            'key': 'max_upload_size_mb',
            'value': '10',
            'value_type': 'integer',
            'description': 'Maximum file upload size in megabytes',
            'category': 'system',
            'is_sensitive': False
        },
        {
            'key': 'session_timeout_minutes',
            'value': '60',
            'value_type': 'integer',
            'description': 'User session timeout duration in minutes',
            'category': 'system',
            'is_sensitive': False
        },
        {
            'key': 'maintenance_mode',
            'value': 'false',
            'value_type': 'boolean',
            'description': 'Enable maintenance mode (disables user access)',
            'category': 'system',
            'is_sensitive': False
        },
        {
            'key': 'debug_mode',
            'value': 'false',
            'value_type': 'boolean',
            'description': 'Enable debug mode (shows detailed error messages)',
            'category': 'system',
            'is_sensitive': False
        },
        
        # ML/AI Settings
        {
            'key': 'groq_api_key',
            'value': '',
            'value_type': 'string',
            'description': 'Groq API key for LLM-powered recommendations',
            'category': 'ml',
            'is_sensitive': True
        },
        {
            'key': 'model_confidence_threshold',
            'value': '0.85',
            'value_type': 'string',
            'description': 'Minimum confidence score for ML predictions (0.0 - 1.0)',
            'category': 'ml',
            'is_sensitive': False
        },
        {
            'key': 'max_recommendations',
            'value': '10',
            'value_type': 'integer',
            'description': 'Maximum number of product recommendations to return',
            'category': 'ml',
            'is_sensitive': False
        },
        {
            'key': 'enable_ml_predictions',
            'value': 'true',
            'value_type': 'boolean',
            'description': 'Enable ML-based price predictions',
            'category': 'ml',
            'is_sensitive': False
        },
        
        # Business Rules
        {
            'key': 'min_listing_price',
            'value': '1000',
            'value_type': 'integer',
            'description': 'Minimum allowed listing price in rupees',
            'category': 'business',
            'is_sensitive': False
        },
        {
            'key': 'max_listing_price',
            'value': '500000',
            'value_type': 'integer',
            'description': 'Maximum allowed listing price in rupees',
            'category': 'business',
            'is_sensitive': False
        },
        {
            'key': 'auto_approve_threshold',
            'value': '15',
            'value_type': 'integer',
            'description': 'Auto-approve listings with price deviation below this percentage',
            'category': 'business',
            'is_sensitive': False
        },
        {
            'key': 'listing_expiry_days',
            'value': '90',
            'value_type': 'integer',
            'description': 'Number of days before a listing expires',
            'category': 'business',
            'is_sensitive': False
        },
        {
            'key': 'max_listings_per_user',
            'value': '20',
            'value_type': 'integer',
            'description': 'Maximum number of active listings per user',
            'category': 'business',
            'is_sensitive': False
        },
        
        # Email Settings
        {
            'key': 'smtp_host',
            'value': 'smtp.gmail.com',
            'value_type': 'string',
            'description': 'SMTP server hostname',
            'category': 'email',
            'is_sensitive': False
        },
        {
            'key': 'smtp_port',
            'value': '587',
            'value_type': 'integer',
            'description': 'SMTP server port',
            'category': 'email',
            'is_sensitive': False
        },
        {
            'key': 'smtp_username',
            'value': '',
            'value_type': 'string',
            'description': 'SMTP authentication username',
            'category': 'email',
            'is_sensitive': True
        },
        {
            'key': 'smtp_password',
            'value': '',
            'value_type': 'string',
            'description': 'SMTP authentication password',
            'category': 'email',
            'is_sensitive': True
        },
        {
            'key': 'admin_email',
            'value': 'admin@dealgoat.com',
            'value_type': 'string',
            'description': 'Admin notification email address',
            'category': 'email',
            'is_sensitive': False
        },
        
        # Security Settings
        {
            'key': 'enable_2fa',
            'value': 'false',
            'value_type': 'boolean',
            'description': 'Enable two-factor authentication',
            'category': 'security',
            'is_sensitive': False
        },
        {
            'key': 'password_min_length',
            'value': '8',
            'value_type': 'integer',
            'description': 'Minimum password length',
            'category': 'security',
            'is_sensitive': False
        },
        {
            'key': 'max_login_attempts',
            'value': '5',
            'value_type': 'integer',
            'description': 'Maximum failed login attempts before lockout',
            'category': 'security',
            'is_sensitive': False
        },
        {
            'key': 'lockout_duration_minutes',
            'value': '30',
            'value_type': 'integer',
            'description': 'Account lockout duration after max failed attempts',
            'category': 'security',
            'is_sensitive': False
        },
        
        # Notification Settings
        {
            'key': 'enable_email_notifications',
            'value': 'true',
            'value_type': 'boolean',
            'description': 'Enable email notifications for users',
            'category': 'notifications',
            'is_sensitive': False
        },
        {
            'key': 'enable_push_notifications',
            'value': 'false',
            'value_type': 'boolean',
            'description': 'Enable push notifications (requires setup)',
            'category': 'notifications',
            'is_sensitive': False
        },
        {
            'key': 'notify_new_listing',
            'value': 'true',
            'value_type': 'boolean',
            'description': 'Notify admins of new listings',
            'category': 'notifications',
            'is_sensitive': False
        },
        {
            'key': 'notify_fraud_detection',
            'value': 'true',
            'value_type': 'boolean',
            'description': 'Notify admins when fraud is detected',
            'category': 'notifications',
            'is_sensitive': False
        },
    ]
    
    created_count = 0
    updated_count = 0
    
    for setting_data in default_settings:
        setting, created = SystemConfiguration.objects.get_or_create(
            key=setting_data['key'],
            defaults={
                'value': setting_data['value'],
                'value_type': setting_data['value_type'],
                'description': setting_data['description'],
                'category': setting_data['category'],
                'is_sensitive': setting_data['is_sensitive'],
            }
        )
        
        if created:
            created_count += 1
            print(f"✓ Created setting: {setting_data['key']}")
        else:
            # Update description and metadata if setting exists
            setting.description = setting_data['description']
            setting.category = setting_data['category']
            setting.is_sensitive = setting_data['is_sensitive']
            setting.value_type = setting_data['value_type']
            setting.save()
            updated_count += 1
            print(f"↻ Updated setting: {setting_data['key']}")
    
    print(f"\n✅ Initialization complete!")
    print(f"   Created: {created_count} settings")
    print(f"   Updated: {updated_count} settings")
    print(f"   Total: {SystemConfiguration.objects.count()} settings in database")

if __name__ == '__main__':
    print("🚀 Initializing DealGoat system settings...\n")
    initialize_settings()
