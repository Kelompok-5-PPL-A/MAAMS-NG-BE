from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from .services import CausesService
from .serializers import BaseCauses, CausesRequest, CausesResponse
from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import permission_classes

@permission_classes([])
class CausesPost(APIView):
    @extend_schema(
        description='Request and Response data for creating a cause',
        request=CausesRequest,
        responses=CausesResponse,
    )
    def post(self, request):
        request_serializer = CausesRequest(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        cause = CausesService.create(self=CausesService, **request_serializer.validated_data)
        response_serializer = CausesResponse(cause)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

@permission_classes([])
class CausesGet(ViewSet):
    @extend_schema(
        description='Request and Response data to get a cause',
        responses=CausesResponse,
    )
    def get(self, request, question_id, pk):
        cause = CausesService.get(self=CausesService, question_id=question_id, pk=pk)
        serializer = CausesResponse(cause)

        return Response(serializer.data)
    
    @extend_schema(
        description='Request and Response data to get list of causes based on the question',
        responses=CausesResponse,
    )
    def get_list(self, request, question_id):
        cause = CausesService.get_list(self=CausesService, question_id=question_id)
        serializer = CausesResponse(cause, many=True)

        return Response(serializer.data)

@permission_classes([])
class CausesPatch(ViewSet):
    @extend_schema(
        description='Request and Response data for updating a cause',
        request=BaseCauses,
        responses=CausesResponse,
    )
    def patch_cause(self, request, question_id, pk):
        request_serializer = BaseCauses(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        cause = CausesService.patch_cause(self=CausesService, question_id=question_id, pk=pk, **request_serializer.validated_data)
        response_serializer = CausesResponse(cause)

        return Response(response_serializer.data)