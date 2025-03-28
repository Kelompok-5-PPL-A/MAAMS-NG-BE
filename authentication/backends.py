from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
import jwt
from sso_ui.config import SSOJWTConfig
from sso_ui.token import decode_token

User = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authenticate against the settings AUTHENTICATION_BACKENDS using email or username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Check if the given username is actually an email
            user = User.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

class GoogleOAuthBackend(ModelBackend):
    """
    Authenticate using Google OAuth 2.0.
    """
    def authenticate(self, request, google_id=None, **kwargs):
        if not google_id:
            return None

        try:
            user = User.objects.get(google_id=google_id)
            return user
        except User.DoesNotExist:
            return None
            
class SSOUIBackend(ModelBackend):
    """
    Authenticate using SSO UI.
    """
    def authenticate(self, request, token=None, **kwargs):
        if not token:
            return None
            
        config = SSOJWTConfig()
        try:
            claims = decode_token(config, "access_token", token)
            if not claims:
                return None  # Token invalid or expired
                
            username = claims.get("username")
            npm = claims.get("npm")
            
            if not username:
                return None
                
            # Try to find user by SSO username first, then by npm
            try:
                if npm:
                    user = User.objects.get(Q(username=username) | Q(npm=npm))
                else:
                    user = User.objects.get(username=username)
                return user
            except User.DoesNotExist:
                return None
                
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None