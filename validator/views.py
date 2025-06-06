from rest_framework.views import APIView
from rest_framework.response import Response
from .services import CausesService
from cause.serializers import CausesResponse
from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import permission_classes

@permission_classes([])
class ValidateView(APIView):
    @extend_schema(
        description='Run Root Cause Analysis for a specific question and row',
        responses=CausesResponse,
    )
    def patch(self, request, question_id):
        service = CausesService() 
        updated_causes = service.validate(question_id=question_id, request=request)
        serializer = CausesResponse(updated_causes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)