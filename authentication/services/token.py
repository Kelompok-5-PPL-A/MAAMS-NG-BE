from rest_framework_simplejwt.tokens import RefreshToken

class TokenService:
    @staticmethod
    def generate_tokens(user):
        refresh = RefreshToken.for_user(user)
        refresh['user_id'] = str(user.uuid)
        refresh['email'] = user.email
        refresh['username'] = user.username
        refresh['role'] = user.role
        
        # Include additional user data if available
        if user.npm:
            refresh['npm'] = user.npm
        if user.noWA:
            refresh['noWA'] = user.noWA
            
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }