import json
import logging
from typing import Any
from userroom.services.room_service import RoomService
from channels.db import database_sync_to_async

logger = logging.getLogger('freenglish')

class RoomCommands:
    def __init__(self, consumer):
        self.consumer = consumer
        self.room_service = RoomService()

    async def handle_create_room(self, data: dict[str, Any], user):
        from userroom.serializers import UserRoomSerializer
        
        try:
            room_name = data.get('room_name')
            native_language = data.get('native_language')
            language_level = data.get('language_level', 'Beginner')
            participant_limit = data.get('participant_limit', 10)

            # Проверка наличия обязательных полей
            if not room_name or not native_language or not language_level:
                await self.consumer.send(text_data=json.dumps({'type': 'error', 'message': 'Missing required fields'}))
                return

            # Создание комнаты
            room = await self.room_service.create_room(
                room_name=room_name,
                native_language=native_language,
                language_level=language_level,
                participant_limit=participant_limit,
                creator=user,
            )

            # Получение данных сериализатора в асинхронном контексте
            room_data = await self.serialize_room_data(room)

            await self.consumer.send(text_data=json.dumps({'type': 'roomCreated', 'room': room_data}))

        except Exception as e:
            logger.error(f'An error occurred while creating a room: {e}', exc_info=True)
            await self.consumer.send(
                text_data=json.dumps(
                    {'type': 'error', 'message': 'An error occurred while creating the room. Please try again later.'}
                )
            )

    async def serialize_room_data(self, room):
        from userroom.serializers import UserRoomSerializer
        
        # Используем database_sync_to_async для сериализации
        return await database_sync_to_async(lambda: UserRoomSerializer(room).data)()
