from django.shortcuts import render
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)

from app.blacklist.models import Blacklist
from app.blacklist.serializers import BlacklistResponseSerializer

from apps.users.permissions import IsAdmin

@swagger_auto_schema(
    method='get',
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
        200: openapi.Response(
            description="Blacklist check successful",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'npm': openapi.Schema(type=openapi.TYPE_STRING, description="Student's NPM number"),
                    'is_blacklisted': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Whether the student is currently blacklisted"),
                    'blacklist_info': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'start_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Blacklist start date"),
                            'end_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Blacklist end date"),
                            'reason': openapi.Schema(type=openapi.TYPE_STRING, description="Reason for blacklisting"),
                            'days_remaining': openapi.Schema(type=openapi.TYPE_INTEGER, description="Days remaining in the blacklist period")
                        },
                        nullable=True,
                        description="Detailed information about the blacklist, null if not blacklisted"
                    )
                }
            )
        ),
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
@api_view(['GET'])
def check_blacklist_status(request):
    """
    Check if a student is blacklisted based on their NPM number provided as a query parameter.
    """
    client_ip = request.META.get('REMOTE_ADDR')
    logger.info(f"Blacklist check request received from IP: {client_ip}")
    
    npm = request.GET.get('npm')
    
    if not npm:
        return Response(
            {"error": "No NPM provided. Please include the 'npm' parameter."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    blacklist = Blacklist.get_active_blacklist(npm)
    response_data = BlacklistResponseSerializer.format_response(npm, blacklist)
    
    return Response(response_data)

@swagger_auto_schema(
    method='post',
    operation_description="Add a student to the blacklist",
    operation_summary="Add to blacklist",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['npm', 'reason', 'end_date'],
        properties={
            'npm': openapi.Schema(type=openapi.TYPE_STRING, description="Student's NPM number"),
            'reason': openapi.Schema(type=openapi.TYPE_STRING, description="Reason for blacklisting"),
            'end_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="End date of blacklist period")
        }
    ),
    responses={
        201: openapi.Response(
            description="Student added to blacklist successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: "Bad request - invalid parameters",
        401: "Authentication credentials were not provided",
        403: "User does not have admin permission"
    },
    tags=['Blacklist'],
)
@api_view(['POST'])
@permission_classes([IsAdmin])
def add_blacklist(request):
    """
    Add a student to the blacklist.
    Requires admin privileges.
    """
    npm = request.data.get('npm')
    reason = request.data.get('reason')
    end_date = request.data.get('end_date')
    
    if not all([npm, reason, end_date]):
        return Response(
            {"error": "Missing required fields. 'npm', 'reason', and 'end_date' are required."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Create blacklist entry
        blacklist = Blacklist.objects.create(
            npm=npm,
            keterangan=reason,
            startDate=timezone.now().date(),
            endDate=end_date
        )

        logger.info(f"Added student with NPM {npm} to blacklist. Blacklist ID: {blacklist.id}")
        
        # Return a response with the created blacklist data
        return Response({
            "success": True,
            "message": f"Student with NPM {npm} added to blacklist successfully.",
            "blacklist_id": str(blacklist.id),
            "blacklist_start_date": blacklist.startDate.isoformat(),
            "blacklist_end_date": blacklist.endDate.isoformat(),
            "blacklist_reason": blacklist.keterangan
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Failed to add blacklist entry for NPM {npm} - {str(e)}")
        return Response({
            "success": False,
            "message": "Failed to add student to blacklist. Please try again."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='delete',
    operation_description="Remove a student from the blacklist",
    operation_summary="Remove from blacklist",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['npm'],
        properties={
            'npm': openapi.Schema(type=openapi.TYPE_STRING, description="Student's NPM number")
        }
    ),
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
@api_view(['DELETE'])
@permission_classes([IsAdmin])
def remove_blacklist(request):
    """
    Remove a student from the blacklist.
    Requires admin privileges.
    """
    npm = request.data.get('npm')
    
    if not npm:
        return Response(
            {"error": "Missing 'npm' field."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        blacklist = Blacklist.objects.filter(
            npm=npm, 
            endDate__gte=timezone.now().date()
        )
        
        if not blacklist.exists():
            return Response({
                "success": False,
                "message": f"No active blacklist found for student with NPM {npm}."
            }, status=status.HTTP_404_NOT_FOUND)
            
        count = blacklist.delete()[0]
        logger.info(f"Removed {count} blacklist entries for student with NPM {npm}.")
        return Response({
            "success": True,
            "message": f"Removed {count} blacklist entries for student with NPM {npm}."
        })
        
    except Exception as e:
        logger.error(f"Failed to remove blacklist entry: {str(e)}")
        return Response({
            "success": False,
            "message": "Failed to remove student from blacklist. Please try again."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='get',
    operation_description="Check if the current authenticated user is blacklisted",
    operation_summary="Check current user blacklist status",
    responses={
        200: openapi.Response(
            description="Blacklist check successful",
            schema=BlacklistResponseSerializer
        ),
        401: "Authentication required"
    },
    tags=['Blacklist'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_current_user_blacklist(request):
    """
    Check if the current authenticated user is blacklisted.
    Requires authentication.
    """
    user = request.user
    
    if not user.npm:
        return Response({
            "npm": None,
            "is_blacklisted": False,
            "blacklist_info": None,
            "message": "User does not have an NPM number assigned"
        })
    
    blacklist = Blacklist.get_active_blacklist(user.npm)
    response_data = BlacklistResponseSerializer.format_response(user.npm, blacklist)
    
    return Response(response_data)