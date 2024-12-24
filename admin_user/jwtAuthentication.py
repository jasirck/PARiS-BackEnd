from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Admin
from users.models import User

class CustomAdminJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        is_admin = validated_token.get("is_admin", False)
        # is_user = validated_token.get("is_user", False)
        
        user_id = validated_token.get("user_id")
        if not user_id:
            raise AuthenticationFailed("Token contained no recognizable user identifier")
        
        try:
            if is_admin:
                user = Admin.objects.get(pk=user_id, is_active=True)
            # elif is_user:
            #     user = User.objects.get(pk=user_id, is_active=True)
            else:
                raise AuthenticationFailed("Invalid token claims.")
        except (Admin.DoesNotExist, User.DoesNotExist):
            raise AuthenticationFailed("No active user found matching the token.")
        
        return user
    

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        is_admin = validated_token.get("is_admin", False)
        user_id = validated_token.get("user_id")
        if not user_id:
            raise AuthenticationFailed("Token contained no recognizable user identifier")
        try:
            if is_admin:
                user = Admin.objects.get(pk=user_id, is_active=True)
            else:
                user = User.objects.get(pk=user_id, is_active=True)
        except (Admin.DoesNotExist, User.DoesNotExist):
            raise AuthenticationFailed("No active user found matching the token.")        
        return user
