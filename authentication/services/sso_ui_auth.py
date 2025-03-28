from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from sso_ui.config import SSOJWTConfig
from sso_ui.token import create_token
from sso_ui.ticket import validate_ticket, ValidateTicketError

User = get_user_model()

class SSOUIAuthService:
    def __init__(self, token_service):
        self.token_service = token_service
        self.config = SSOJWTConfig()
        
    def validate_sso_ticket(self, ticket):
        try:
            service_response = validate_ticket(self.config, ticket)
            return service_response
        except ValidateTicketError as e:
            raise AuthenticationFailed(f"SSO ticket validation failed: {str(e)}")
        
    def authenticate_or_create_user(self, auth_data):
        auth_success = auth_data.get("authentication_success")
        if not auth_success:
            raise AuthenticationFailed("Invalid SSO response")
            
        username = auth_success.get("user")
        if not username:
            raise AuthenticationFailed("Username not provided by SSO")
            
        user_attributes = auth_success.get("attributes", {})
        npm = user_attributes.get("npm")
        nama = user_attributes.get("nama", "")
        
        if nama and " " in nama:
            first_name, last_name = nama.split(" ", 1)
        else:
            first_name, last_name = nama, ""
            
        email = f"{username}@ui.ac.id"
        
        # Try to find user by SSO username or npm first
        try:
            if npm:
                user = User.objects.get(npm=npm)
            else:
                user = User.objects.get(username=username)
                
            user.email = email  # Ensure email is up to date
            
            if not user.first_name and first_name:
                user.first_name = first_name
            if not user.last_name and last_name:
                user.last_name = last_name
                
            user.save()
            is_new_user = False
        except User.DoesNotExist:
            # Then try by email
            try:
                user = User.objects.get(email=email)
                # Update NPM if not set
                if npm and not user.npm:
                    user.npm = npm
                    user.save()
                is_new_user = False
            except User.DoesNotExist:
                # Create new user if not found
                angkatan = npm[:2] if npm and len(npm) >= 2 else None
                
                user = User.objects.create_user(
                    email=email,
                    username=username,
                    npm=npm,
                    first_name=first_name,
                    last_name=last_name,
                    angkatan=angkatan,
                    role='pengguna'
                )
                is_new_user = True
                
        return user, is_new_user
        
    def process_sso_login(self, ticket):
        auth_data = self.validate_sso_ticket(ticket)
        user, is_new_user = self.authenticate_or_create_user(auth_data)
        
        # Generate access and refresh tokens
        tokens = self.token_service.generate_tokens(user)
        
        # Also create SSO tokens to maintain session with SSO system
        sso_access_token = create_token(self.config, "access_token", auth_data)
        sso_refresh_token = create_token(self.config, "refresh_token", auth_data)
        
        return {
            "user": user,
            "tokens": tokens,
            "sso_tokens": {
                "access_token": sso_access_token,
                "refresh_token": sso_refresh_token
            },
            "is_new_user": is_new_user
        }