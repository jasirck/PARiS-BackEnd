from rest_framework import serializers
from users.models import User
from admin_user.models import Admin


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "user_image",
            "first_join",
            "last_join",
        ]



class AdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Admin
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'password', 'confirm_password',
            'first_join', 'last_join', 'last_login'
        ]
        read_only_fields = ['id', 'first_join', 'last_join', 'last_login']
    
    def validate(self, data):
        if 'password' in data and 'confirm_password' in data:
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
            
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        
        admin = Admin.objects.create(**validated_data)
        
        if password:
            admin.set_password(password)
            admin.save()
        
        return admin
    
    def update(self, instance, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        
        # Update all other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Handle password separately
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance