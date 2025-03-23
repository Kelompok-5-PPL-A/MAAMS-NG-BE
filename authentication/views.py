from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, ValidationError, ParseError

from drf_spectacular.utils import extend_schema

from authentication.models import CustomUser
from authentication.serializers import (
    CustomUserSerializer, GoogleAuthRequestSerializer, LoginResponseSerializer
)
from authentication.services import GoogleAuthService, TokenService

@extend_schema(
    description='Authenticate with Google OAuth. Send the ID token received from Google.',
    request=GoogleAuthRequestSerializer,
    responses=LoginResponseSerializer,
)
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
   
        user_serializer = CustomUserSerializer(user)
        
        return Response(
            data={ 
                "access_token": tokens["access"],
                "refresh_token": tokens["refresh"],
                "data": user_serializer.data,
                "detail": "Successfully registered and logged in." if is_new_user else "Successfully logged in."
            }, 
            status=status.HTTP_200_OK
        )

    except ParseError as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except ValidationError as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except AuthenticationFailed as e:
        return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("Unexpected error in google_login: %s", str(e))
        return Response({'detail': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)