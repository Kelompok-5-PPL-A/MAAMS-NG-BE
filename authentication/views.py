from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from django.contrib.auth import login, logout
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed, ParseError

from drf_spectacular.utils import extend_schema

from authentication.serializers import (
    UserSerializer, GoogleAuthRequestSerializer, 
    SSOTicketSerializer, LoginResponseSerializer, 
    TokenRefreshSerializer
)
from authentication.services.auth import AuthenticationService
from authentication.services.jwt_token import JWTTokenService
from sso_ui.config import SSOJWTConfig
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings
from sso_ui.ticket import validate_ticket, ValidateTicketError

User = get_user_model()
token_service = JWTTokenService()
auth_service = AuthenticationService(token_service)

ERROR_MEESSAGE = 'This field is required.'

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        description='Authenticate with Google OAuth. Send the ID token received from Google.',
        request=GoogleAuthRequestSerializer,
        responses=LoginResponseSerializer,
    )
    def post(self, request):
        try:
            id_token_value = request.data.get('id_token')
            if not id_token_value:
                return Response(
                    {'id_token': [ERROR_MEESSAGE]}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Duplicate code: Directly validate the token instead of using the provider
            try:
                # Verify the ID token with Google
                client_id = settings.GOOGLE_CLIENT_ID
                user_info = id_token.verify_oauth2_token(
                    id_token_value, 
                    google_requests.Request(),
                    audience=client_id
                )
                
                # Validate token data
                if not user_info or 'sub' not in user_info:
                    raise AuthenticationFailed("Invalid Google token data")
                    
                if not user_info.get('email'):
                    raise AuthenticationFailed("Email not provided by Google")
                
                # Duplicate code: Get or create user logic
                google_id = user_info['sub']
                email = user_info['email']
                
                # First try to find by Google ID
                is_new_user = False
                try:
                    user = User.objects.get(google_id=google_id)
                    # User exists, update their information if needed
                    self._update_user_if_needed(user, user_info)
                except User.DoesNotExist:
                    # Then try by email
                    try:
                        user = User.objects.get(email=email)
                        # User exists but wasn't linked to this Google account
                        if not user.google_id:
                            user.google_id = google_id
                            user.save(update_fields=['google_id'])
                    except User.DoesNotExist:
                        # Create a new user
                        user = self._create_new_user(user_info)
                        is_new_user = True
                
                # Generate tokens directly
                tokens = token_service.generate_tokens(user)
                
            except ValueError as e:
                raise AuthenticationFailed(f"Invalid Google token: {str(e)}")
            except Exception as e:
                raise AuthenticationFailed(f"Token verification failed: {str(e)}")
            
            # Return response with tokens and user info
            user_serializer = UserSerializer(user)
            
            return Response(
                data={
                    "access_token": tokens["access"],
                    "refresh_token": tokens["refresh"],
                    "user": user_serializer.data,
                    "is_new_user": is_new_user,
                    "detail": "Successfully registered and logged in." if is_new_user else "Successfully logged in."
                }, 
                status=status.HTTP_200_OK
            )
        
        except ParseError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except AuthenticationFailed as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        
        except Exception as e:
            return Response({'detail': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def _create_new_user(self, user_info: dict) -> User:
        """
        Create a new user from Google account information.
        """
        google_id = user_info['sub']
        email = user_info['email']
        username = email.split('@')[0]
        
        user = User.objects.create_user(
            email=email,
            username=username,
            google_id=google_id,
            first_name=user_info.get('given_name'),
            last_name=user_info.get('family_name'),
            role='user'
        )
        
        return user
    
    def _update_user_if_needed(self, user: User, user_info: dict) -> None:
        """
        Update user information if needed.
        """
        update_fields = []
        
        if not user.first_name and user_info.get('given_name'):
            user.first_name = user_info['given_name']
            update_fields.append('first_name')
            
        if not user.last_name and user_info.get('family_name'):
            user.last_name = user_info['family_name']
            update_fields.append('last_name')
            
        if update_fields:
            user.save(update_fields=update_fields)

class SSOLoginView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        description='Authenticate with SSO UI CAS. Send the ticket received from SSO UI.',
        parameters=[SSOTicketSerializer],
        responses=LoginResponseSerializer,
    )
    def get(self, request):
        ticket = request.GET.get("ticket")
        if not ticket:
            return Response({"error": "Missing ticket"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Duplicate code: Directly validate the ticket instead of using the provider
            config = SSOJWTConfig()
            
            try:
                # Validate the ticket with SSO UI
                response = validate_ticket(config, ticket)
                
                # Extract user info
                user_info = response.get("authentication_success")
                if not user_info:
                    raise AuthenticationFailed("Invalid ticket response")
                
                # Duplicate code: Get or create user logic
                username = user_info.get("user")
                attributes = user_info.get("attributes", {})
                npm = attributes.get("npm")
                nama = attributes.get("nama", "")
                
                if not username or not npm:
                    raise AuthenticationFailed("Missing required user information")
                    
                is_new_user = False
                
                # Try to find existing user by NPM
                user = User.objects.filter(npm=npm).first()
                
                if not user:
                    # Try to find by username
                    user = User.objects.filter(username=username).first()
                    
                if not user:
                    # Try to find by email
                    email = f"{username}@ui.ac.id"
                    user = User.objects.filter(email=email).first()
                    
                if not user:
                    # Create new user
                    first_name, *last_name_parts = nama.split()
                    last_name = " ".join(last_name_parts) if last_name_parts else ""
                    
                    user = User.objects.create_user(
                        username=username,
                        email=f"{username}@ui.ac.id",
                        npm=npm,
                        first_name=first_name,
                        last_name=last_name
                    )
                    is_new_user = True
                else:
                    # Update user info
                    self._update_user_info(user, username, f"{username}@ui.ac.id", npm, nama)
                
                # Generate tokens directly
                tokens = token_service.generate_tokens(user)
                
            except ValidateTicketError as e:
                raise AuthenticationFailed(str(e))
            except Exception as e:
                raise AuthenticationFailed(f"Unexpected error: {str(e)}")
            
            # Login the user to the session
            request.session["sso_token"] = tokens["access"]
            request.session.modified = True
            
            # Return response with tokens and user info
            user_serializer = UserSerializer(user)
            
            return Response({
                "access_token": tokens["access"],
                "refresh_token": tokens["refresh"],
                "user": user_serializer.data,
                "is_new_user": is_new_user,
                "detail": "Successfully registered and logged in." if is_new_user else "Successfully logged in."
            }, status=status.HTTP_200_OK)
            
        except AuthenticationFailed as e:
            if hasattr(e, 'detail') and isinstance(e.detail, dict):
                return Response(e.detail, status=status.HTTP_403_FORBIDDEN)
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
            
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _update_user_info(self, user: User, username: str, email: str, npm: str, nama: str) -> None:
        """
        Update user information from SSO UI.
        """
        # Only update email if it's from UI domain
        if email.endswith("@ui.ac.id"):
            user.email = email
            
        # Update other fields
        user.username = username
        user.npm = npm
        
        # Update name if provided
        if nama:
            first_name, *last_name_parts = nama.split()
            last_name = " ".join(last_name_parts) if last_name_parts else ""
            user.first_name = first_name
            user.last_name = last_name
            
        user.save()

class SSOLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        logout(request)
        config = SSOJWTConfig()
        url = f"{config.cas_url}/logout?url={config.service_url}"
        return HttpResponseRedirect(url)

class TokenRefreshView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        description='Refresh an access token using a refresh token.',
        request=TokenRefreshSerializer,
        responses={
            200: {
                'description': 'Token refresh successful',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'access': {'type': 'string'},
                                'refresh': {'type': 'string'}
                            }
                        }
                    }
                }
            },
            401: {'description': 'Invalid refresh token'}
        }
    )
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'refresh': [ERROR_MEESSAGE]}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Refresh the token
            new_tokens = auth_service.refresh_token(refresh_token)
            
            return Response(new_tokens, status=status.HTTP_200_OK)
            
        except AuthenticationFailed as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
            
        except Exception as e:
            return Response({'detail': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'refresh': [ERROR_MEESSAGE]}, status=status.HTTP_400_BAD_REQUEST)
            
        # Blacklist the token
        success = auth_service.logout(refresh_token)
        
        # Also log out from Django session
        logout(request)
        
        if success:
            return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Logout failed.'}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        description='Get current user profile information.',
        responses={
            200: UserSerializer,
            401: {'description': 'Authentication credentials were not provided.'}
        }
    )
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)