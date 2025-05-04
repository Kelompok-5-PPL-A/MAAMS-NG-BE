from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import logging

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.blacklist.models import Blacklist
from apps.blacklist.serializers import (
    BlacklistResponseSerializer, 
    BlacklistCreateSerializer,
    BlacklistRemoveSerializer,
    BlacklistHistorySerializer
)
from apps.blacklist.services import BlacklistService
from authentication.permissions import IsAdmin

class BlacklistCheckView(APIView):
    @swagger_auto_schema(
        operation_description="Check if a student is currently blacklisted by their NPM number",
        operation_summary="Check blacklist status",
        manual_parameters=[
            openapi.Parameter(
                'npm', 
                openapi.IN_QUERY, 
                description="Student's NPM number to check blacklist status", 
                type=openapi.TYPE_STRING,
                required=True,
                example="2206081534"
            )
        ],
        responses={
            200: BlacklistResponseSerializer,
            400: openapi.Response(
                description="Bad request - NPM parameter missing",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                    }
                )
            )
        },
        tags=['Blacklist'],
    )
    def get(self, request):
        """
        Check if a student is blacklisted based on their NPM number provided as a query parameter.
        """
        npm = request.GET.get('npm')
        
        if not npm:
            return Response(
                {"error": "No NPM provided. Please include the 'npm' parameter."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Use the service to check blacklist status
        response_data = BlacklistService.check_blacklist_status(npm)
        
        return Response(response_data)


class CurrentUserBlacklistCheckView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Check if the current authenticated user is blacklisted",
        operation_summary="Check current user blacklist status",
        responses={
            200: BlacklistResponseSerializer,
            401: "Authentication required"
        },
        tags=['Blacklist'],
    )
    def get(self, request):
        """
        Check if the current authenticated user is blacklisted.
        """
        user = request.user
        
        if not user.npm:
            return Response({
                "npm": None,
                "is_blacklisted": False,
                "blacklist_info": None,
                "message": "User does not have an NPM number assigned"
            })
        
        # Use the service to check blacklist status
        response_data = BlacklistService.check_blacklist_status(user.npm)
        
        return Response(response_data)


class BlacklistAddView(APIView):
    permission_classes = [IsAdmin]
    
    @swagger_auto_schema(
        operation_description="Add a student to the blacklist",
        operation_summary="Add to blacklist",
        request_body=BlacklistCreateSerializer,
        responses={
            201: openapi.Response(
                description="Student added to blacklist successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'blacklist_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid')
                    }
                )
            ),
            400: "Bad request - invalid parameters",
            401: "Authentication credentials were not provided",
            403: "User does not have admin permission"
        },
        tags=['Blacklist'],
    )
    def post(self, request):
        """
        Add a student to the blacklist.
        Requires admin privileges.
        """
        serializer = BlacklistCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Extract validated data
            npm = serializer.validated_data['npm']
            reason = serializer.validated_data['reason']
            end_date = serializer.validated_data['end_date']
            
            # Use the service to add to blacklist
            result = BlacklistService.add_to_blacklist(npm, reason, end_date)
            
            return Response(result, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Failed to add student to blacklist: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)


class BlacklistRemoveView(APIView):
    permission_classes = [IsAdmin]
    
    @swagger_auto_schema(
        operation_description="Remove a student from the blacklist",
        operation_summary="Remove from blacklist",
        request_body=BlacklistRemoveSerializer,
        responses={
            200: openapi.Response(
                description="Student removed from blacklist successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: "Student not found in blacklist",
            401: "Authentication credentials were not provided",
            403: "User does not have admin permission"
        },
        tags=['Blacklist'],
    )
    def delete(self, request):
        """
        Remove a student from the blacklist.
        Requires admin privileges.
        """
        serializer = BlacklistRemoveSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Extract validated data
            npm = serializer.validated_data['npm']
            
            # Use the service to remove from blacklist
            result = BlacklistService.remove_from_blacklist(npm)
            
            if not result['success']:
                return Response(result, status=status.HTTP_404_NOT_FOUND)
                
            return Response(result)
                
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Failed to remove student from blacklist: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)


class BlacklistHistoryView(APIView):
    permission_classes = [IsAdmin]
    
    @swagger_auto_schema(
        operation_description="Get blacklist history for a student",
        operation_summary="Get blacklist history",
        manual_parameters=[
            openapi.Parameter(
                'npm', 
                openapi.IN_QUERY, 
                description="Student's NPM number", 
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: BlacklistHistorySerializer(many=True),
            400: "NPM parameter missing",
            401: "Authentication credentials were not provided",
            403: "User does not have admin permission"
        },
        tags=['Blacklist'],
    )
    def get(self, request):
        """
        Get blacklist history for a student.
        Requires admin privileges.
        """
        npm = request.GET.get('npm')
        
        if not npm:
            return Response(
                {"error": "No NPM provided. Please include the 'npm' parameter."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Use the service to get blacklist history
        history = BlacklistService.get_blacklist_history(npm)
        
        serializer = BlacklistHistorySerializer(history, many=True)
        return Response(serializer.data)


class ActiveBlacklistsView(APIView):
    permission_classes = [IsAdmin]
    
    @swagger_auto_schema(
        operation_description="Get all currently active blacklists",
        operation_summary="Get active blacklists",
        responses={
            200: BlacklistHistorySerializer(many=True),
            401: "Authentication credentials were not provided",
            403: "User does not have admin permission"
        },
        tags=['Blacklist'],
    )
    def get(self, request):
        """
        Get all currently active blacklists.
        Requires admin privileges.
        """
        # Use the service to get all active blacklists
        active_blacklists = BlacklistService.get_all_active_blacklists()
        
        serializer = BlacklistHistorySerializer(active_blacklists, many=True)
        return Response(serializer.data)