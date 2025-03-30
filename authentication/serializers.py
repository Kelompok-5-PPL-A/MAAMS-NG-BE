from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'uuid', 'email', 'username', 
            'first_name', 'last_name', 'date_joined',
            'is_active', 'role', 'npm', 'angkatan', 'noWA'
        ]
        read_only_fields = ['uuid', 'date_joined', 'is_active', 'role']

class GoogleAuthRequestSerializer(serializers.Serializer):
    id_token = serializers.CharField(required=True, help_text='Google ID token')

class SSOTicketSerializer(serializers.Serializer):
    ticket = serializers.CharField(required=True, help_text='SSO UI CAS ticket')

class ContactUpdateSerializer(serializers.Serializer):
    noWA = serializers.CharField(required=True, help_text='WhatsApp number')

class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True, help_text='Refresh token')

class TokenPairSerializer(serializers.Serializer):
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

class LoginResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    user = UserSerializer(read_only=True)
    is_new_user = serializers.BooleanField(read_only=True)
    detail = serializers.CharField(read_only=True)