from rest_framework import status
from rest_framework.exceptions import APIException

class EmptyTagException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

class InvalidFiltersException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

class InvalidTagException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

class InvalidTimeRangeRequestException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    
class UniqueTagException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    
class ValueNotUpdatedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

class ForbiddenRequestException(APIException):
    status_code = status.HTTP_403_FORBIDDEN

class NotFoundRequestException(APIException):
    status_code = status.HTTP_404_NOT_FOUND

class RateLimitExceededException(APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS

class AIServiceErrorException(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE