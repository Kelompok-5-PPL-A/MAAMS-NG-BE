import logging
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import ValidationError as DjangoValidationError

def handle_django_validation_error(exc):
    if hasattr(exc, 'message_dict'):
        detail = exc.message_dict
    else:
        detail = {'error': [str(msg) for msg in exc.messages]}
    return Response(detail, status=status.HTTP_400_BAD_REQUEST)

def handle_404_error():
    return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

def handle_other_exceptions(exc):
    return Response({'detail': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF.
    
    This centralizes error handling and ensures consistent error responses
    across the API. It extends the default DRF exception handler with
    additional capabilities.
    """
    response = exception_handler(exc, context)
    
    if response is None:
        if isinstance(exc, DjangoValidationError):
            response = handle_django_validation_error(exc)
            
        elif isinstance(exc, Http404):
            response = handle_404_error()
            
        elif isinstance(exc, Exception):
            response = handle_other_exceptions(exc)
            
    return response

class ServiceException(APIException):
    """
    Base exception for service layer errors.
    
    This helps separate business logic errors from API errors and allows
    for cleaner exception handling in services.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A service error occurred.'
    default_code = 'service_error'
    
    def __init__(self, detail=None, code=None, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        super().__init__(detail, code)