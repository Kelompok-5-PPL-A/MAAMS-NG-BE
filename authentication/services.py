import os
from rest_framework.exceptions import AuthenticationFailed, ParseError
from google.oauth2 import id_token
from google.auth.transport import requests

from authentication.models import CustomUser

class TokenService:
    def generate_tokens(self, user):
        return {
            'access': f"access_token_for_user_{user.id}",
            'refresh': f"refresh_token_for_user_{user.id}"
        }

class GoogleAuthService:
    def __init__(self, token_service):
        self.token_service = token_service
        self.google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    
    def verify_google_token(self, id_token_str):
        if not id_token_str:
            raise ParseError("ID token is required")
        
        try:
            user_info = id_token.verify_oauth2_token(
                id_token_str, 
                requests.Request(),
                self.google_client_id
            )
            
            if not user_info:
                raise AuthenticationFailed("Invalid authentication token")
                
            return user_info
            
        except ValueError:
            raise AuthenticationFailed("Invalid authentication token")
    
    def authenticate_or_create_user(self, user_info):
        if not user_info:
            raise AuthenticationFailed("Invalid user information")

        google_id = user_info.get('sub')
        email = user_info.get('email')
        
        if not email:
            raise AuthenticationFailed("Email is required")
        
        try:
            user = CustomUser.objects.get(google_id=google_id)
            return user, False
        except CustomUser.DoesNotExist:
            pass
        
        try:
            user = CustomUser.objects.get(email=email)
            # Update Google ID if not set
            user.google_id = google_id
            user.save()
            return user, False
        except CustomUser.DoesNotExist:
            pass

        given_name = user_info.get('given_name')
        family_name = user_info.get('family_name')
        
        user = CustomUser.objects.create_user(
            email=email,
            google_id=google_id,
            given_name=given_name,
            family_name=family_name
        )
        
        return user, True
    
    def process_google_login(self, id_token_str):
        user_info = self.verify_google_token(id_token_str)
        user, is_new_user = self.authenticate_or_create_user(user_info)
        tokens = self.token_service.generate_tokens(user)
        
        return {
            'user': user,
            'tokens': tokens,
            'is_new_user': is_new_user
        }