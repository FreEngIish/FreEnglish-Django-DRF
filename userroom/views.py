from rest_framework import viewsets
from .models import UserRoom
from .serializers import UserRoomSerializer
from rest_framework.permissions import IsAuthenticated


class UserRoomViewSet(viewsets.ModelViewSet):
    queryset = UserRoom.objects.all()
    serializer_class = UserRoomSerializer
    permission_classes = [IsAuthenticated]
