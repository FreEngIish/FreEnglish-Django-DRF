from django.urls import path
from .views import UserRoomListCreateAPIView, UserRoomDetailAPIView

urlpatterns = [
    path('rooms/', UserRoomListCreateAPIView.as_view(), name='room-list-create'),
    path('rooms/<int:pk>/', UserRoomDetailAPIView.as_view(), name='room-detail'),
]
