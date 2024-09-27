from django.urls import re_path

from userroom.consumers.room_comsumer import RoomConsumer


websocket_urlpatterns = [
    re_path(r'^ws/rooms/$', RoomConsumer.as_asgi()),
]