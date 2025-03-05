from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from drf_spectacular.utils import extend_schema

from validator.services.questions import QuestionService
from validator.serializers import QuestionRequest, QuestionResponse


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
            user=request.user if request.user.is_authenticated else None,  # Mendukung guest
            **request_serializer.validated_data
        )

        response_serializer = QuestionResponse(question)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
