from django.urls import path
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenRefreshView,
    TokenVerifyView
)

from authentication.views import google_login

app_name = 'authentication'

urlpatterns = [
    path('login-google/', google_login, name='google_login'),
    path('logout/', TokenBlacklistView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]