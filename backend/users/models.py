from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import secrets
from datetime import timedelta


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('email_verified', True)
        
        # Set default values for required fields for superuser
        extra_fields.setdefault('phone', '0000000000')
        extra_fields.setdefault('location', 'Admin')
        extra_fields.setdefault('gender', 'other')
        extra_fields.setdefault('age', 18)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
            ('prefer-not-to-say', 'Prefer not to say'),
        ],
        blank=True
    )
    age = models.IntegerField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    # Email verification
    email_verified = models.BooleanField(default=False)
    
    # User status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Admin moderation fields
    is_suspended = models.BooleanField(default=False, help_text="Account suspended by admin")
    suspension_reason = models.TextField(blank=True, help_text="Reason for suspension")
    suspended_at = models.DateTimeField(null=True, blank=True)
    suspended_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suspended_users',
        help_text="Admin who suspended this user"
    )
    is_banned_from_messaging = models.BooleanField(default=False, help_text="Banned from sending messages")
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name


class OTP(models.Model):
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = 'otps'
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
        indexes = [
            models.Index(fields=['email', 'is_used']),
        ]

    def __str__(self):
        return f"OTP for {self.email}"

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    @classmethod
    def generate_otp(cls, email, expiry_minutes=10):
        """Generate a new OTP for the given email"""
        # Invalidate old OTPs for this email
        cls.objects.filter(email=email, is_used=False).update(is_used=True)
        
        # Generate new OTP
        otp_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
        
        otp = cls.objects.create(
            email=email,
            otp_code=otp_code,
            expires_at=expires_at
        )
        
        return otp

    @classmethod
    def verify_otp(cls, email, otp_code):
        """Verify OTP for the given email"""
        try:
            otp = cls.objects.get(
                email=email,
                otp_code=otp_code,
                is_used=False
            )
            
            if not otp.is_valid():
                return False, "OTP has expired"
            
            # Mark as used
            otp.is_used = True
            otp.save()
            
            return True, "OTP verified successfully"
        except cls.DoesNotExist:
            return False, "Invalid OTP"


class PasswordResetToken(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = 'password_reset_tokens'
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
        indexes = [
            models.Index(fields=['email', 'is_used']),
            models.Index(fields=['token', 'is_used']),
        ]

    def __str__(self):
        return f"Password reset token for {self.email}"

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    @classmethod
    def generate_token(cls, email, expiry_minutes=30):
        """Generate a new password reset token for the given email"""
        # Invalidate old tokens for this email
        cls.objects.filter(email=email, is_used=False).update(is_used=True)
        
        # Generate new token
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
        
        reset_token = cls.objects.create(
            email=email,
            token=token,
            expires_at=expires_at
        )
        
        return reset_token

    @classmethod
    def verify_token(cls, token):
        """Verify password reset token"""
        try:
            reset_token = cls.objects.get(
                token=token,
                is_used=False
            )
            
            if not reset_token.is_valid():
                return False, None, "Token has expired"
            
            return True, reset_token.email, "Token is valid"
        except cls.DoesNotExist:
            return False, None, "Invalid token"


class AdminActionLog(models.Model):
    """Model to track all admin actions for audit trail"""
    
    ACTION_TYPES = [
        ('user_suspend', 'User Suspended'),
        ('user_activate', 'User Activated'),
        ('user_delete', 'User Deleted'),
        ('user_verify', 'User Email Verified'),
        ('user_password_reset', 'User Password Reset'),
        ('listing_approve', 'Listing Approved'),
        ('listing_reject', 'Listing Rejected'),
        ('listing_flag', 'Listing Flagged as Fraud'),
        ('listing_delete', 'Listing Deleted'),
        ('listing_edit', 'Listing Edited'),
        ('message_delete', 'Message Deleted'),
        ('user_ban_messaging', 'User Banned from Messaging'),
        ('settings_update', 'System Settings Updated'),
        ('report_generate', 'Report Generated'),
        ('data_export', 'Data Exported'),
        ('other', 'Other Action'),
    ]
    
    admin_user = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='admin_actions'
    )
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    target_model = models.CharField(max_length=50, help_text="Model name (User, Listing, etc.)")
    target_id = models.IntegerField(null=True, blank=True, help_text="ID of the affected object")
    description = models.TextField(help_text="Detailed description of the action")
    
    # Request metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional action data")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'admin_action_logs'
        verbose_name = 'Admin Action Log'
        verbose_name_plural = 'Admin Action Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['admin_user', '-created_at']),
            models.Index(fields=['action_type', '-created_at']),
            models.Index(fields=['target_model', 'target_id']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.admin_user.email if self.admin_user else 'System'} - {self.get_action_type_display()} - {self.created_at}"
    
    @classmethod
    def log_action(cls, admin_user, action_type, target_model, target_id, description, request=None, **metadata):
        """Helper method to log admin actions"""
        log_data = {
            'admin_user': admin_user,
            'action_type': action_type,
            'target_model': target_model,
            'target_id': target_id,
            'description': description,
            'metadata': metadata,
        }
        
        if request:
            # Extract IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                log_data['ip_address'] = x_forwarded_for.split(',')[0]
            else:
                log_data['ip_address'] = request.META.get('REMOTE_ADDR')
            
            # Extract user agent
            log_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        return cls.objects.create(**log_data)

