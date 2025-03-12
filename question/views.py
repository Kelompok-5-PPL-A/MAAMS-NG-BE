from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import permission_classes
from drf_spectacular.utils import extend_schema

from .services import QuestionService
from .serializers import QuestionRequest, QuestionResponse


@permission_classes([])  # Mengizinkan guest user
class QuestionPost(APIView):
    @extend_schema(
        description='Request and Response data for creating a question',
        request=QuestionRequest,
        responses=QuestionResponse,
    )
    def post(self, request):
        request_serializer = QuestionRequest(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        service_class = QuestionService()
        question = service_class.create(
            **request_serializer.validated_data
        )

        response_serializer = QuestionResponse(question)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

@permission_classes([])
class QuestionGet(ViewSet):    
    """
    ViewSet to return all or specific questions.
    """

    service_class = QuestionService()
    
    @extend_schema(
        description='Request and Response data to get a question',
        responses=QuestionResponse,
    )
    def get(self, request, pk):
        question = self.service_class.get(pk=pk)
        serializer = QuestionResponse(question)
        
        return Response(serializer.data)