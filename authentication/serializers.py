from rest_framework import serializers
from authentication.models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'uuid', 'email', 
            'given_name', 'family_name', 'date_joined',
            'is_active', 'is_staff'
        ]
        read_only_fields = ['uuid', 'date_joined', 'is_active', 'is_staff']

class GoogleAuthRequestSerializer(serializers.Serializer):
    id_token = serializers.CharField(required=True, help_text='Google ID token')

class AuthTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

class LoginResponseSerializer(serializers.Serializer):
    class Meta:
        ref_name = 'LoginResponse'

    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    data = CustomUserSerializer(read_only=True)
    detail = serializers.CharField(read_only=True)