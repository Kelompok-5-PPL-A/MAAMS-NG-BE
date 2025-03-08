from rest_framework.views import APIView
from rest_framework.response import Response
from serializers import CausesRequest, CausesResponse
from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import permission_classes

@permission_classes([])  # Mengizinkan guest user
class CausesPost(APIView):
    @extend_schema(
        description='Request and Response data for creating a cause',
        request=CausesRequest,
        responses=CausesResponse,
    )
    def post(self, request):
        request_serializer = CausesRequest(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        
        # Langsung menggunakan data yang divalidasi tanpa service
        cause_data = request_serializer.validated_data  
        
        response_serializer = CausesResponse(cause_data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
