from django.conf import settings
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
    ContactUpdateSerializer
)
from authentication.services.token import TokenService
from authentication.services.google_auth import GoogleAuthService
from authentication.services.sso_ui_auth import SSOUIAuthService
from apps.blacklist.models import Blacklist

@extend_schema(
    description='Authenticate with Google OAuth. Send the ID token received from Google.',
    request=GoogleAuthRequestSerializer,
    responses=LoginResponseSerializer,
)
@require_POST
@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    try:
        if not request.data.get('id_token'):
            return Response({'id_token': ['This field may not be blank.']}, status=status.HTTP_400_BAD_REQUEST)
            
        token_service = TokenService()
        auth_service = GoogleAuthService(token_service=token_service)
            
        result = auth_service.process_google_login(request.data.get('id_token'))
            
        user = result.get("user")
        tokens = result.get("tokens")
        is_new_user = result.get("is_new_user")
            
        if not user or not tokens.get('access') or not tokens.get('refresh'):
            return Response({'detail': 'Invalid response from authentication service'}, status=status.HTTP_400_BAD_REQUEST)
        
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
            token_service = TokenService()
            auth_service = SSOUIAuthService(token_service=token_service)
            
            # Check if the user is blacklisted
            result = auth_service.process_sso_login(ticket)
            
            user = result.get("user")
            tokens = result.get("tokens")
            sso_tokens = result.get("sso_tokens")
            is_new_user = result.get("is_new_user")
            
            # Check if user is blacklisted
            if user.npm:
                blacklist_entry = Blacklist.is_user_blacklisted(user.npm)
                if blacklist_entry:
                    return Response({
                        "error": "User is blacklisted",
                        "blacklist_info": {
                            "npm": user.npm,
                            "reason": blacklist_entry.keterangan,
                            "blacklisted_at": blacklist_entry.startDate.isoformat(),
                            "expires_at": blacklist_entry.endDate.isoformat() if blacklist_entry.endDate else None
                        }
                    }, status=status.HTTP_403_FORBIDDEN)
            
            login(request, user)
            request.session["sso_token"] = sso_tokens["access_token"]
            request.session.modified = True
            
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

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

class UpdateContactView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        description='Update user contact information (WhatsApp number).',
        request=ContactUpdateSerializer,
        responses=UserSerializer,
    )
    def post(self, request):
        data = request.data
        phone_number = data.get("noWA")
        
        if not phone_number:
            return Response({"error": "Field noWA is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validator for phone number
        validator_no_wa = RegexValidator(
            regex=r'^\d{8,15}$',
            message="Phone number must be 8-15 digits without '+' sign"
        )
        
        try:
            validator_no_wa(phone_number)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        user.noWA = phone_number
        user.save(update_fields=['noWA'])
        
        serializer = UserSerializer(user)
        return Response(serializer.data)