from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OTP
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()


class CompleteRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20)
    location = serializers.CharField(max_length=200)
    gender = serializers.CharField(max_length=20)
    age = serializers.IntegerField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                "password": "Passwords do not match."
            })
        return attrs

    def validate_age(self, value):
        if value < 18:
            raise serializers.ValidationError("You must be at least 18 years old.")
        if value > 120:
            raise serializers.ValidationError("Please enter a valid age.")
        return value

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone',
            'location', 'gender', 'age', 'password', 'confirm_password'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                "password": "Passwords do not match."
            })
        return attrs

    def validate_age(self, value):
        if value < 18:
            raise serializers.ValidationError("You must be at least 18 years old.")
        if value > 120:
            raise serializers.ValidationError("Please enter a valid age.")
        return value


    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email cannot be empty")
        return str(value).strip().lower()


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email cannot be empty")
        return str(value).strip().lower()


class EmailCheckSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email cannot be empty")
        return str(value).strip().lower()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email cannot be empty")
        return str(value).strip().lower()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email cannot be empty")
        return str(value).strip().lower()


class PasswordResetVerifySerializer(serializers.Serializer):
    token = serializers.CharField(max_length=100)

    def validate_token(self, value):
        if not value or len(value) < 10:
            raise serializers.ValidationError("Invalid token format")
        return value


class PasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=100)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                "password": "Passwords do not match."
            })
        return attrs

    def validate_token(self, value):
        if not value or len(value) < 10:
            raise serializers.ValidationError("Invalid token format")
        return value


