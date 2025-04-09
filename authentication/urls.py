from django.urls import path

from authentication.views import (
    GoogleLoginView, SSOLoginView, SSOLogoutView,
    TokenRefreshView, LogoutView, UserProfileView
)

app_name = 'authentication'

urlpatterns = [
    # Google OAuth
    path('login-google/', GoogleLoginView.as_view(), name='google_login'),
    
    # SSO UI
    path('login-sso/', SSOLoginView.as_view(), name='sso_login'),
    path('logout-sso/', SSOLogoutView.as_view(), name='sso_logout'),
    
    # Token management
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # User profile management
    path('profile/', UserProfileView.as_view(), name='user_profile'),
]