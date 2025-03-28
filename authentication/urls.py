from django.urls import path
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenRefreshView,
    TokenVerifyView
)

from authentication.views import (
    google_login, SSOLoginView, SSOLogoutView,
    UserProfileView, UpdateContactView
)

app_name = 'authentication'

urlpatterns = [
    # Google OAuth
    path('login-google/', google_login, name='google_login'),
    
    # SSO UI
    path('login-sso/', SSOLoginView.as_view(), name='sso_login'),
    path('logout-sso/', SSOLogoutView.as_view(), name='sso_logout'),
    
    # Token management
    path('logout/', TokenBlacklistView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # User profile management
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('update-contact/', UpdateContactView.as_view(), name='update_contact'),
]