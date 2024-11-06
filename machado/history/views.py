from rest_framework.response import Response
from rest_framework import viewsets, status
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from machado.history.models import History

#Swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

#Serializer
from machado.history.serializers import HistorySerializer

class AuthenticatedUserActions(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    """
    @swagger_auto_schema(
        operation_summary="Create History",
        operation_description="Create a new history record.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description'),
                'method': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Method of requisition'),
            }
        ),
        responses={
            201: openapi.Response(description="History created"),
            400: openapi.Response(description="Bad request")
        }
    )
    @action(detail=False, methods=['post'])
    def create(self, request):
        description = request.data.get('description')
        method = request.data.get('method') 

        if description is None or method is None:
            return Response(
                {"detail": "Description and method are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        history = History.objects.create(
            user=request.user,
            description=description,
            method=method
        )

        serializer = HistorySerializer(history)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    """

    @swagger_auto_schema(
        operation_summary="List History",
        operation_description="Retrieve a list of all history.",
        responses={
            200: openapi.Response(
                description="A list of records",
                schema=HistorySerializer(many=True)
            ),
            403: openapi.Response(description="Forbidden - User not authenticated"),
        }
    )
    @action(detail=False, methods=['get'])
    def listMyHistory(self, request):
        history = History.objects.filter(user=request.user).order_by('-created_at')
        serializer = HistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class AdminUserActions(viewsets.GenericViewSet):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_summary="List History",
        operation_description="Retrieve a list of all history.",
        responses={
            200: openapi.Response(
                description="A list of records",
                schema=HistorySerializer(many=True)
            ),
            403: openapi.Response(description="Forbidden - User not authenticated"),
        }
    )
    @action(detail=False, methods=['get'])
    def listAllHistory(self, request):
        history = History.objects.all().order_by('-created_at')
        serializer = HistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)