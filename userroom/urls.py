from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRoomViewSet

router = DefaultRouter()
router.register(r'rooms', UserRoomViewSet, basename='room')

urlpatterns = [
    path('', include(router.urls)),
]
