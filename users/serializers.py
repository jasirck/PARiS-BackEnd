from rest_framework import serializers 
from .models import User
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model



class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()



class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone_number', 'user_image', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        """
        Validates the password for minimum length, digits, and letters.
        """
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Password must contain at least one letter.")
        return value

    def validate_email(self, value):
        """
        Validates email to ensure it's in the proper format and not already in use.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone_number(self, value):
        """
        Validates phone number to ensure uniqueness if provided.
        """
        if value and User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def create(self, validated_data):
        """
        Hashes the password and creates the user.
        Handles database integrity errors gracefully.
        """
        try:
            validated_data['password'] = make_password(validated_data['password'])
            return super().create(validated_data)
        except IntegrityError as e:
            # Handle unique constraints or other database errors
            if 'username' in str(e):
                raise serializers.ValidationError({"username": "This username is already taken."})
            if 'email' in str(e):
                raise serializers.ValidationError({"email": "This email is already registered."})
            if 'phone_number' in str(e):
                raise serializers.ValidationError({"phone_number": "This phone number is already in use."})
            raise serializers.ValidationError({"detail": "An unexpected error occurred."})
        except DjangoValidationError as e:
            raise serializers.ValidationError({"detail": str(e)})


class PasswordResetSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)  
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        # Check if passwords match
        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")
        
        # Validate password strength using Django's password validators
        try:
            validate_password(new_password)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        return attrs

    def save(self):
        phone_number = self.validated_data['phone_number']
        new_password = self.validated_data['new_password']
        
        # Find the user by phone number
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this phone number does not exist.")
        
        # Set the new password and save
        user.set_password(new_password)
        user.save()
        return user
