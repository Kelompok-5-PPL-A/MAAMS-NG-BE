from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import permission_classes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated
from question.models import Question
from question.services import QuestionService
from question.serializers import FieldValuesResponse, QuestionRequest, QuestionResponse, PaginatedQuestionResponse, BaseQuestion, QuestionTagRequest, QuestionTitleRequest
from rest_framework.permissions import AllowAny
from rest_framework.generics import DestroyAPIView
from validator.exceptions import NotFoundRequestException
from utils.pagination import CustomPageNumberPagination

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
                user=request.user if request.user.is_authenticated else None
            )
            response_serializer = QuestionResponse(question)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except serializers.ValidationError:
            return Response(
                {"error": "Invalid input"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"}, 
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
    def retrieve(self, request, pk=None):
        try:
            question = self.service_class.get(pk=pk)
            serializer = QuestionResponse(question)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@permission_classes([AllowAny])
class QuestionGetMatched(APIView):
    pagination_class = CustomPageNumberPagination()
    service_class = QuestionService()

    @extend_schema(
        description='Returns user question that matched with certain keyword',
        responses=PaginatedQuestionResponse,
        parameters=[
            OpenApiParameter(
                name='filter',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Specify query filter mode.'
            ),
            OpenApiParameter(
                name='time_range',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Specify the time range for the query.'
            ),
            OpenApiParameter(
                name='keyword',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Specify the keyword to match user questions.'
            ),
            OpenApiParameter(
                name='count',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Specify the count of results to return per page.'
            ),
            OpenApiParameter(
                name='p',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Specify the page number for paginated results.'
            ),
        ]
    )
    def get(self, request):
        try:
            q_filter = request.query_params.get('filter', 'semua')
            time_range = request.query_params.get('time_range') 
            keyword = request.query_params.get('keyword', '') 

            questions = self.service_class.get_matched(q_filter=q_filter, 
                                           user=request.user, 
                                           time_range=time_range, 
                                           keyword=keyword)

            serializer = QuestionResponse(questions, many=True)

            paginator = self.pagination_class
            page = paginator.paginate_queryset(serializer.data, request)

            return paginator.get_paginated_response(page)

        except Exception as e:
            return Response(
                {'detail': f'Unexpected error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@permission_classes([IsAuthenticated])
class QuestionGetRecent(APIView):
    def get(self, request):
        try:
            recent_question = QuestionService.get_recent(self, user=request.user)
            
            if recent_question is None:
                return Response(status=status.HTTP_204_NO_CONTENT)
                
            serializer = QuestionResponse(recent_question)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response({'detail': "No recent questions found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@permission_classes([IsAuthenticated])
class QuestionGetAll(APIView):
    pagination_class = CustomPageNumberPagination()
    service_class = QuestionService()
    @extend_schema(
        description='Returns all questions corresponding to a specified user.',
        responses=PaginatedQuestionResponse,
    )
    def get(self, request):
        try:
            time_range = request.query_params.get('time_range')
            questions = self.service_class.get_all(user=request.user, time_range=time_range)
            serializer = QuestionResponse(questions, many=True)
            paginator = self.pagination_class
            page = paginator.paginate_queryset(serializer.data, request)
            return paginator.get_paginated_response(page)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@permission_classes([AllowAny])
class QuestionDelete(DestroyAPIView):
    """
    APIView to delete a specific question.
    """
    def delete(self, request, pk=None):
        try:
            service_class = QuestionService()
            question = service_class.get(pk=pk)
            
            if question.user != request.user and question.user is not None:
                return Response(
                    {"detail": "You do not have permission to delete this question."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            service_class.delete(pk=pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except NotFoundRequestException as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
@permission_classes([IsAuthenticated])
class QuestionGetPrivileged(APIView):
    """
    Returns privileged questions for authenticated users based on filter and keyword.
    """

    pagination_class = CustomPageNumberPagination()
    service_class = QuestionService()

    @extend_schema(
        description='Returns questions with mode PENGAWASAN for privileged users based on keyword and time range.',
        responses=PaginatedQuestionResponse,
        parameters=[
            OpenApiParameter(
                name='filter',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Specify query filter mode.'
            ),
            OpenApiParameter(
                name='keyword',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Specify the keyword to match user questions.'
            ),
            OpenApiParameter(
                name='count',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Specify the count of results to return per page.'
            ),
            OpenApiParameter(
                name='p',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Specify the page number for paginated results.'
            ),
        ]
    )
    def get(self, request):
        try:
            q_filter = request.query_params.get('filter') # ini untuk filter nya
            keyword = request.query_params.get('keyword', '')

            questions = self.service_class.get_privileged(
                q_filter=q_filter,
                user=request.user,
                keyword=keyword
            )

            serializer = QuestionResponse(questions, many=True)

            paginator = self.pagination_class
            page = paginator.paginate_queryset(serializer.data, request)

            return paginator.get_paginated_response(page)

        except Exception as e:
            return Response(
                {'detail': f'Unexpected error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@permission_classes([IsAuthenticated])
class QuestionGetFieldValues(APIView):
    service_class = QuestionService()

    @extend_schema(
        description="Returns all unique question fields' values that are attached to available questions.",
        responses=FieldValuesResponse
    )
    def get(self, request):
        values = self.service_class.get_field_values(user=request.user)
        serializer = FieldValuesResponse(values)
        
        return Response(serializer.data)

@permission_classes([AllowAny])
class QuestionPatch(ViewSet):
    service_class = QuestionService()
    
    @extend_schema(
        description='Request and Response data for updating question mode',
        request=BaseQuestion,
        responses=QuestionResponse,
    )
    def patch_mode(self, request, pk):
        request_serializer = BaseQuestion(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        question = self.service_class.update_question(user=request.user if request.user.is_authenticated else None, pk=pk, mode=request_serializer.validated_data.get('mode'))
        response_serializer = QuestionResponse(question)
        
        return Response(response_serializer.data)
    
    @extend_schema(
        description='Request and Response data for updating question title',
        request=QuestionTitleRequest,
        responses=QuestionResponse,
    )
    def patch_title(self, request, pk):
        request_serializer = QuestionTitleRequest(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        question = self.service_class.update_question(user=request.user if request.user.is_authenticated else None, pk=pk, title=request_serializer.validated_data.get('title'))
        response_serializer = QuestionResponse(question)
        
        return Response(response_serializer.data)
    
    @extend_schema(
        description='Request and Response data for updating question tags',
        request=QuestionTagRequest,
        responses=QuestionResponse,
    )
    def patch_tags(self, request, pk):
        request_serializer = QuestionTagRequest(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        question = self.service_class.update_question(user=request.user if request.user.is_authenticated else None, pk=pk, tags=request_serializer.validated_data.get('tags'))
        response_serializer = QuestionResponse(question)
        
        return Response(response_serializer.data)
