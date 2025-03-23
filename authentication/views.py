from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_yasg.utils import swagger_auto_schema

from authentication.serializers import (
    GoogleAuthRequestSerializer, 
    LoginResponseSerializer
)
from authentication.services import GoogleAuthService, TokenService

@swagger_auto_schema(
    method='post',
    request_body=GoogleAuthRequestSerializer,
    responses={
        status.HTTP_200_OK: LoginResponseSerializer,
        status.HTTP_400_BAD_REQUEST: 'Bad Request',
        status.HTTP_401_UNAUTHORIZED: 'Authentication Failed',
        status.HTTP_500_INTERNAL_SERVER_ERROR: 'Server Error'
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    serializer = GoogleAuthRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    id_token = serializer.validated_data.get('id_token')
    
    if not id_token:
        return Response({'id_token': ['This field may not be blank.']}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        token_service = TokenService()
        auth_service = GoogleAuthService(token_service=token_service, google_client_id=settings.GOOGLE_CLIENT_ID)
   
        result = auth_service.process_google_login(id_token)
        
        user = result.get('user')
        tokens = result.get('tokens')
        is_new_user = result.get('is_new_user')
        
        if not user or not tokens.get('access') or not tokens.get('refresh'):
            return Response({'detail': 'Invalid response from authentication service'}, status=status.HTTP_400_BAD_REQUEST)
        
        response_data = {
            'access_token': tokens['access'],
            'refresh_token': tokens['refresh'],
            'data': {
                'email': user.email,
                'uuid': str(user.uuid),
                'given_name': user.given_name,
                'family_name': user.family_name,
                'date_joined': user.date_joined,
                'is_active': user.is_active,
                'is_staff': user.is_staff
            },
            'detail': "Successfully registered and logged in." if is_new_user else "Successfully logged in."
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except AuthenticationFailed as e:
        return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        
    except ValidationError as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    except DjangoValidationError as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({'detail': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)