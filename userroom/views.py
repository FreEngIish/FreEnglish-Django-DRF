from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserRoom
from .serializers import UserRoomSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UserRoomListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rooms = UserRoom.objects.all()
        serializer = UserRoomSerializer(rooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserRoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRoomDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a room by ID",
        responses={200: UserRoomSerializer, 404: 'Not Found'}
    )
    def get(self, request, pk):
        room = get_object_or_404(UserRoom, pk=pk)
        serializer = UserRoomSerializer(room)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update a room by ID",
        request_body=UserRoomSerializer,
        responses={200: UserRoomSerializer, 400: 'Bad Request'}
    )
    def put(self, request, pk):
        room = get_object_or_404(UserRoom, pk=pk)
        serializer = UserRoomSerializer(room, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a room by ID",
        responses={204: 'No Content', 404: 'Not Found'}
    )
    def delete(self, request, pk):
        room = get_object_or_404(UserRoom, pk=pk)
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
