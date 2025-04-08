from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import permission_classes
from drf_spectacular.utils import extend_schema
from question.models import Question
from question.services import QuestionService
from question.serializers import QuestionRequest, QuestionResponse
from rest_framework.permissions import AllowAny

@permission_classes([AllowAny])  # Mengizinkan guest user
class QuestionPost(APIView):
    @extend_schema(
        description='Request and Response data for creating a question',
        request=QuestionRequest,
        responses=QuestionResponse,
    )
    def post(self, request):
        try:
            request_serializer = QuestionRequest(data=request.data)
            request_serializer.is_valid(raise_exception=True)

            service_class = QuestionService()
            question = service_class.create(
                **request_serializer.validated_data,
                user=request.user
            )
            response_serializer = QuestionResponse(question)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except serializers.ValidationError:
            return Response(
                {"error": "Invalid input"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(
                {"error": "An unexpected error occurred"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@permission_classes([AllowAny])
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
        try:
            question = self.service_class.get(pk=pk)
            serializer = QuestionResponse(question)
            return Response(serializer.data)
        except Exception:
            return Response(
                {"error": "An unexpected error occurred"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )