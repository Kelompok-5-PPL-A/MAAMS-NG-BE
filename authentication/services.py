import os
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, ParseError

from authentication.models import CustomUser

class TokenService:
    @staticmethod
    def generate_tokens(user: CustomUser) -> dict:
        refresh = RefreshToken.for_user(user)
        refresh['user_id'] = str(user.uuid)
        refresh['email'] = user.email
        
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

class GoogleAuthService:
    def __init__(self, token_service):
        self.token_service = token_service
    
    def verify_google_token(self, token):
        try:
            if not token:
                raise ParseError("id_token is required")
                
            user_info = id_token.verify_oauth2_token(
                token, google_requests.Request()
            )
            
            if not user_info:
                raise AuthenticationFailed("Invalid Google token")
                
            return user_info
            
        except ValueError as e:
            raise AuthenticationFailed(f"Invalid Google token: {str(e)}")
        except Exception as e:
            raise AuthenticationFailed(f"Token verification failed: {str(e)}")
    
    def authenticate_or_create_user(self, user_info):
        if 'sub' not in user_info:
            raise AuthenticationFailed("Invalid user info from Google")
            
        google_id = user_info['sub']
        email = user_info.get('email')
        
        if not email:
            raise AuthenticationFailed("Email not provided by Google")
        
        try:
            user = CustomUser.objects.get(google_id=google_id)
            is_new_user = False
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(email=email)

                # Update the Google ID if it's not set
                if not user.google_id:
                    user.google_id = google_id
                    user.save(update_fields=['google_id'])

                is_new_user = False
            except CustomUser.DoesNotExist:
                # Create a new user if not found
                user = CustomUser.objects.create_user(
                    email=email,
                    username=email,
                    google_id=google_id,
                    first_name=user_info.get('given_name'),
                    last_name=user_info.get('family_name')
                )
                is_new_user = True
                
        return user, is_new_user
    
    def process_google_login(self, id_token_value):
        user_info = self.verify_google_token(id_token_value)
        user, is_new_user = self.authenticate_or_create_user(user_info)
        tokens = self.token_service.generate_tokens(user)
        
        return {
            "user": user,
            "tokens": tokens,
            "is_new_user": is_new_user
        }