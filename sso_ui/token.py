import jwt
from datetime import datetime, timedelta
from django.utils import timezone

def create_token(config, token_type, service_response):
    user_attr = service_response.get("authentication_success")
    if not user_attr:
        raise Exception("Authentication failed: no user data")
    
    exp_time = (
        config.access_token_exp_time
        if token_type == "access_token"
        else config.refresh_token_exp_time
    )
    
    secret_key = (
        config.access_token_secret_key
        if token_type == "access_token"
        else config.refresh_token_secret_key
    )
    
    payload = {
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(seconds=exp_time),
        "username": user_attr.get("user"),
        "attributes": user_attr.get("attributes", {})
    }
    
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

def decode_token(config, token_type, token):
    secret_key = (
        config.access_token_secret_key
        if token_type == "access_token"
        else config.refresh_token_secret_key
    )
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        
        # Check if token is expired
        if "exp" in payload:
            exp_time = payload["exp"]
            if exp_time < timezone.now().timestamp():
                return None
        
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None