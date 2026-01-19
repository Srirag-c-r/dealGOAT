from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from django.conf import settings
from .serializers import (
    UserRegistrationSerializer,
    CompleteRegistrationSerializer,
    OTPSerializer,
    OTPVerifySerializer,
    EmailCheckSerializer,
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetVerifySerializer,
    PasswordResetSerializer,
)
from .models import OTP, PasswordResetToken

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user"""
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        # Check if email is verified
        email = serializer.validated_data['email']
        user_exists = User.objects.filter(email=email).first()
        
        if user_exists and not user_exists.email_verified:
            return Response(
                {'message': 'Please verify your email first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = serializer.save()
        
        return Response(
            {
                'success': True,
                'message': 'User registered successfully',
                'user_id': user.id
            },
            status=status.HTTP_201_CREATED
        )
    
    return Response(
        {
            'success': False,
            'message': 'Registration failed',
            'errors': serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    """Send OTP to user's email"""
    serializer = OTPSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {
                'success': False,
                'message': 'Invalid email address',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    email = serializer.validated_data['email']
    
    # Generate OTP first (always generate, even if email fails)
    otp = OTP.generate_otp(email, expiry_minutes=10)
    
    # Check email configuration
    email_backend = settings.EMAIL_BACKEND
    email_host_user = getattr(settings, 'EMAIL_HOST_USER', '')
    email_host_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    
    # Check if using console backend (development mode)
    if 'console' in email_backend.lower():
        # Print to console for development
        print(f"\n{'='*50}")
        print(f"📧 OTP EMAIL (Console Backend)")
        print(f"{'='*50}")
        print(f"To: {email}")
        print(f"OTP Code: {otp.otp_code}")
        print(f"Expires at: {otp.expires_at}")
        print(f"{'='*50}\n")
        
        return Response(
            {
                'success': True,
                'message': 'OTP generated successfully. Check Django terminal/console for the OTP code.',
                'otp': otp.otp_code if settings.DEBUG else None,
                'note': 'Using console email backend - configure SMTP in .env for real emails',
                'email_sent': False
            },
            status=status.HTTP_200_OK
        )
    
    # Check if email credentials are configured
    if not email_host_user or not email_host_password or \
       'your-email' in email_host_user.lower() or \
       'your-16-char' in email_host_password.lower() or \
       email_host_password == '':
        # Credentials not configured, use console fallback
        print(f"\n{'='*50}")
        print(f"⚠️  EMAIL CONFIGURATION MISSING")
        print(f"{'='*50}")
        print(f"Email credentials are not properly configured in .env file.")
        print(f"Please update EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in backend/.env")
        print(f"\n📧 OTP EMAIL (Fallback to Console)")
        print(f"To: {email}")
        print(f"OTP Code: {otp.otp_code}")
        print(f"Expires at: {otp.expires_at}")
        print(f"{'='*50}\n")
        
        return Response(
            {
                'success': True,
                'message': 'OTP generated successfully. Email not configured - check Django terminal for OTP code.',
                'otp': otp.otp_code if settings.DEBUG else None,
                'error': 'Email configuration incomplete. Please configure SMTP settings in .env file.',
                'email_sent': False,
                'note': 'Update EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in backend/.env to enable email sending'
            },
            status=status.HTTP_200_OK
        )
    
    # Try to send real email via SMTP
    try:
        # Create email message with better formatting
        email_subject = 'DealGoat - Email Verification OTP'
        email_message = f"""
Hello,

Your OTP for email verification is: {otp.otp_code}

This OTP will expire in 10 minutes.

If you didn't request this OTP, please ignore this email.

Best regards,
DealGoat Team
        """.strip()
        
        send_mail(
            subject=email_subject,
            message=email_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        print(f"\n{'='*50}")
        print(f"✅ OTP EMAIL SENT SUCCESSFULLY")
        print(f"{'='*50}")
        print(f"To: {email}")
        print(f"OTP Code: {otp.otp_code}")
        print(f"Expires at: {otp.expires_at}")
        print(f"{'='*50}\n")
        
        return Response(
            {
                'success': True,
                'message': 'OTP sent to your email successfully. Please check your inbox (and spam folder).',
                'email_sent': True
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        # If email sending fails, fallback to console
        error_message = str(e)
        print(f"\n{'='*50}")
        print(f"❌ EMAIL SENDING FAILED")
        print(f"{'='*50}")
        print(f"Error: {error_message}")
        print(f"\n📧 OTP EMAIL (Fallback to Console)")
        print(f"To: {email}")
        print(f"OTP Code: {otp.otp_code}")
        print(f"Expires at: {otp.expires_at}")
        print(f"{'='*50}\n")
        
        # Provide helpful error message based on error type
        error_message_lower = str(error_message).lower() if error_message else ""
        user_friendly_error = 'Email sending failed. Please check your email configuration.'
        if 'authentication failed' in error_message_lower or 'invalid credentials' in error_message_lower:
            user_friendly_error = 'Email authentication failed. Please check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env file.'
        elif 'connection' in error_message_lower or 'timeout' in error_message_lower:
            user_friendly_error = 'Could not connect to email server. Please check your internet connection and EMAIL_HOST settings.'
        
        return Response(
            {
                'success': True,
                'message': f'OTP generated successfully. {user_friendly_error} Check Django terminal for OTP code.',
                'otp': otp.otp_code if settings.DEBUG else None,
                'error': user_friendly_error,
                'error_detail': error_message if settings.DEBUG else None,
                'email_sent': False
            },
            status=status.HTTP_200_OK
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def complete_registration(request):
    serializer = CompleteRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email, is_active=False, password='')
            # Update user details
            user.first_name = serializer.validated_data['first_name']
            user.last_name = serializer.validated_data['last_name']
            user.phone = serializer.validated_data['phone']
            user.location = serializer.validated_data['location']
            user.gender = serializer.validated_data['gender']
            user.age = serializer.validated_data['age']
            user.set_password(serializer.validated_data['password'])
            user.is_active = True
            user.save()
            return Response({'success': True, 'message': 'Registration complete.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'success': False, 'message': 'User not found or already active.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """Verify OTP and mark email as verified"""
    serializer = OTPVerifySerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'message': 'Invalid data'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    email = serializer.validated_data['email']
    otp_code = serializer.validated_data['otp']
    
    # Verify OTP
    is_valid, message = OTP.verify_otp(email, otp_code)
    
    if not is_valid:
        return Response(
            {
                'success': False,
                'message': message
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Mark email as verified (create or update user)
    user, created = User.objects.get_or_create(
        email=email,
        defaults={'email_verified': True, 'is_active': False, 'password': ''}
    )
    
    if not created:
        user.email_verified = True
        user.save()
    
    return Response(
        {
            'success': True,
            'message': 'Email verified successfully'
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def check_email(request):
    """Check if email is available"""
    email = request.GET.get('email', '').lower()
    
    if not email:
        return Response(
            {'available': False, 'message': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # An email is only considered unavailable if it belongs to an active user.
    # This allows users who have verified their email but not completed their profile to try again.
    user = User.objects.filter(email=email).first()
    exists = user and user.is_active
    
    return Response(
        {
            'available': not exists,
            'message': 'Email is available' if not exists else 'Email already exists'
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login user with email and password"""
    serializer = LoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {
                'success': False,
                'message': 'Invalid data',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    user = authenticate(request, email=email, password=password)

    if user is None:
        return Response(
            {
                'success': False,
                'message': 'Invalid email or password.',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.is_active:
        return Response(
            {
                'success': False,
                'message': 'Your account is inactive. Please complete registration or contact support.',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Get or create auth token
    token, created = Token.objects.get_or_create(user=user)

    return Response(
        {
            'success': True,
            'message': 'Login successful.',
            'token': token.key,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'location': user.location,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'profile_picture': user.profile_picture.url if user.profile_picture else None,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """Request password reset - send reset token via email"""
    serializer = PasswordResetRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {
                'success': False,
                'message': 'Invalid email address',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    email = serializer.validated_data['email']
    
    # Check if user exists
    try:
        user = User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        # Don't reveal if email exists or not (security best practice)
        return Response(
            {
                'success': True,
                'message': 'If an account with that email exists, a password reset link has been sent.'
            },
            status=status.HTTP_200_OK
        )
    
    # Generate reset token
    reset_token = PasswordResetToken.generate_token(email, expiry_minutes=30)
    
    # Check email configuration
    email_backend = settings.EMAIL_BACKEND
    email_host_user = getattr(settings, 'EMAIL_HOST_USER', '')
    email_host_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    
    # Frontend URL for password reset (adjust based on your frontend URL)
    frontend_url = 'http://localhost:5173'
    reset_url = f"{frontend_url}/reset-password?token={reset_token.token}"
    
    # Check if using console backend (development mode)
    if 'console' in email_backend.lower():
        print(f"\n{'='*50}")
        print(f"🔐 PASSWORD RESET EMAIL (Console Backend)")
        print(f"{'='*50}")
        print(f"To: {email}")
        print(f"Reset Token: {reset_token.token}")
        print(f"Reset URL: {reset_url}")
        print(f"Expires at: {reset_token.expires_at}")
        print(f"{'='*50}\n")
        
        return Response(
            {
                'success': True,
                'message': 'Password reset token generated. Check Django terminal/console for the reset link.',
                'token': reset_token.token if settings.DEBUG else None,
                'reset_url': reset_url if settings.DEBUG else None,
                'note': 'Using console email backend - configure SMTP in .env for real emails',
                'email_sent': False
            },
            status=status.HTTP_200_OK
        )
    
    # Check if email credentials are configured
    if not email_host_user or not email_host_password or \
       'your-email' in email_host_user.lower() or \
       'your-16-char' in email_host_password.lower() or \
       email_host_password == '':
        print(f"\n{'='*50}")
        print(f"⚠️  EMAIL CONFIGURATION MISSING")
        print(f"{'='*50}")
        print(f"Email credentials are not properly configured in .env file.")
        print(f"Please update EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in backend/.env")
        print(f"\n🔐 PASSWORD RESET EMAIL (Fallback to Console)")
        print(f"To: {email}")
        print(f"Reset Token: {reset_token.token}")
        print(f"Reset URL: {reset_url}")
        print(f"Expires at: {reset_token.expires_at}")
        print(f"{'='*50}\n")
        
        return Response(
            {
                'success': True,
                'message': 'Password reset token generated. Email not configured - check Django terminal for reset link.',
                'token': reset_token.token if settings.DEBUG else None,
                'reset_url': reset_url if settings.DEBUG else None,
                'error': 'Email configuration incomplete. Please configure SMTP settings in .env file.',
                'email_sent': False,
                'note': 'Update EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in backend/.env to enable email sending'
            },
            status=status.HTTP_200_OK
        )
    
    # Try to send real email via SMTP
    try:
        email_subject = 'DealGoat - Password Reset Request'
        email_message = f"""
Hello {user.first_name or 'User'},

You requested to reset your password for your DealGoat account.

Click the link below to reset your password:
{reset_url}

This link will expire in 30 minutes.

If you didn't request a password reset, please ignore this email. Your password will remain unchanged.

Best regards,
DealGoat Team
        """.strip()
        
        send_mail(
            subject=email_subject,
            message=email_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        print(f"\n{'='*50}")
        print(f"✅ PASSWORD RESET EMAIL SENT SUCCESSFULLY")
        print(f"{'='*50}")
        print(f"To: {email}")
        print(f"Reset Token: {reset_token.token}")
        print(f"Expires at: {reset_token.expires_at}")
        print(f"{'='*50}\n")
        
        return Response(
            {
                'success': True,
                'message': 'Password reset link sent to your email successfully. Please check your inbox (and spam folder).',
                'email_sent': True
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        error_message = str(e)
        print(f"\n{'='*50}")
        print(f"❌ EMAIL SENDING FAILED")
        print(f"{'='*50}")
        print(f"Error: {error_message}")
        print(f"\n🔐 PASSWORD RESET EMAIL (Fallback to Console)")
        print(f"To: {email}")
        print(f"Reset Token: {reset_token.token}")
        print(f"Reset URL: {reset_url}")
        print(f"Expires at: {reset_token.expires_at}")
        print(f"{'='*50}\n")
        
        user_friendly_error = 'Email sending failed. Please check your email configuration.'
        error_message_lower = str(error_message).lower() if error_message else ""
        if 'authentication failed' in error_message_lower or 'invalid credentials' in error_message_lower:
            user_friendly_error = 'Email authentication failed. Please check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env file.'
        elif 'connection' in error_message_lower or 'timeout' in error_message_lower:
            user_friendly_error = 'Could not connect to email server. Please check your internet connection and EMAIL_HOST settings.'
        
        return Response(
            {
                'success': True,
                'message': f'Password reset token generated. {user_friendly_error} Check Django terminal for reset link.',
                'token': reset_token.token if settings.DEBUG else None,
                'reset_url': reset_url if settings.DEBUG else None,
                'error': user_friendly_error,
                'error_detail': error_message if settings.DEBUG else None,
                'email_sent': False
            },
            status=status.HTTP_200_OK
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_password_reset_token(request):
    """Verify password reset token"""
    serializer = PasswordResetVerifySerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {
                'success': False,
                'message': 'Invalid token',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    token = serializer.validated_data['token']
    is_valid, email, message = PasswordResetToken.verify_token(token)
    
    if not is_valid:
        return Response(
            {
                'success': False,
                'message': message
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response(
        {
            'success': True,
            'message': 'Token is valid',
            'email': email
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password using token"""
    serializer = PasswordResetSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {
                'success': False,
                'message': 'Invalid data',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    token = serializer.validated_data['token']
    new_password = serializer.validated_data['new_password']
    
    # Verify token
    is_valid, email, message = PasswordResetToken.verify_token(token)
    
    if not is_valid:
        return Response(
            {
                'success': False,
                'message': message
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get user and reset password
    try:
        user = User.objects.get(email=email, is_active=True)
        user.set_password(new_password)
        user.save()
        
        # Mark token as used
        reset_token = PasswordResetToken.objects.get(token=token)
        reset_token.is_used = True
        reset_token.save()
        
        return Response(
            {
                'success': True,
                'message': 'Password reset successfully. You can now login with your new password.'
            },
            status=status.HTTP_200_OK
        )
    except User.DoesNotExist:
        return Response(
            {
                'success': False,
                'message': 'User not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
def update_profile(request):
    """Update user profile (specifically profile picture)"""
    if not request.user.is_authenticated:
        return Response(
            {'success': False, 'message': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    user = request.user
    profile_picture = request.FILES.get('profile_picture')
    
    if profile_picture:
        user.profile_picture = profile_picture
        user.save()
        return Response({
            'success': True,
            'message': 'Profile picture updated successfully',
            'profile_picture': user.profile_picture.url
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': 'No profile picture provided'
    }, status=status.HTTP_400_BAD_REQUEST)

