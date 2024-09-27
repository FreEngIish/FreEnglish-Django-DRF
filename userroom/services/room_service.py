from channels.db import database_sync_to_async
import logging

logger = logging.getLogger('freenglish')

class RoomService:
    @database_sync_to_async
    def create_room(self, room_name, native_language, language_level, participant_limit, creator):
        from userroom.models import UserRoom, RoomMembers  # Импортируем здесь, чтобы избежать циклических импортов

        # Создаем новую комнату
        room = UserRoom(
            room_name=room_name,
            native_language=native_language,
            language_level=language_level,
            participant_limit=participant_limit,
            creator=creator,
        )
        room.save()  # Сохраняем комнату в базе данных
        room.current_participants.add(creator)  # Добавляем создателя как участника комнаты

        # Создаем запись о членах
        RoomMembers.objects.create(room=room, user=creator)  
        
        return room
