from channels.db import database_sync_to_async
import logging

logger = logging.getLogger('freenglish')

class RoomService:
    @database_sync_to_async
    def create_room(self, room_name, native_language, language_level, participant_limit, creator):
        from userroom.models import UserRoom, RoomMembers

        room = UserRoom(
            room_name=room_name,
            native_language=native_language,
            language_level=language_level,
            participant_limit=participant_limit,
            creator=creator,
        )
        room.save()  # Синхронный вызов, так что он должен быть здесь
        room.current_participants.add(creator)  # Добавляем создателя как участника
        RoomMembers.objects.create(room=room, user=creator)  # Синхронный вызов
        return room

    @database_sync_to_async
    def get_room(self, room_id):
        from userroom.models import UserRoom
        return UserRoom.objects.filter(room_id=room_id).first()  # Здесь также синхронный вызов

    @database_sync_to_async
    def add_participant(self, room, user):
        room.current_participants.add(user)
        from userroom.models import RoomMembers
        RoomMembers.objects.get_or_create(room=room, user=user)

    @database_sync_to_async
    def remove_participant(self, room, user):
        room.current_participants.remove(user)

    @database_sync_to_async
    def count_participants(self, room):
        return room.current_participants.count()  # Синхронный вызов
