from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from django.contrib.auth import login, logout
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

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

# Create service instances
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
            id_token = request.data.get('id_token')
            if not id_token:
                return Response(
                    {'id_token': [ERROR_MEESSAGE]}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Authenticate using the Google provider
            tokens, user, is_new_user = auth_service.authenticate_with_provider('google', id_token)
            
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
            # Authenticate using the SSO provider
            tokens, user, is_new_user = auth_service.authenticate_with_provider('sso', ticket)
            
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
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
            
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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