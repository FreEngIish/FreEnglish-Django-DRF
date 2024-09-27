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
            language_level = data.get('language_level', 'Beginner')  # Установка уровня по умолчанию
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

            room_data = await self.serialize_room_data(room)
            await self.consumer.send(text_data=json.dumps({'type': 'roomCreated', 'room': room_data}))

        except Exception as e:
            logger.error(f'An error occurred while creating a room: {e}', exc_info=True)
            await self.consumer.send(
                text_data=json.dumps(
                    {'type': 'error', 'message': 'An error occurred while creating the room. Please try again later.'}
                )
            )

    async def handle_join_room(self, room_id, user):
        try:
            room = await self.room_service.get_room(room_id)
            if room:
                current_count = await self.room_service.count_participants(room)
                if current_count < room.participant_limit:
                    await self.room_service.add_participant(room, user)
                    await self.consumer.send(text_data=json.dumps({'type': 'roomJoined', 'room_id': room_id}))
                else:
                    await self.consumer.send(text_data=json.dumps({'type': 'error', 'message': 'Room is full.'}))
            else:
                await self.consumer.send(text_data=json.dumps({'type': 'error', 'message': 'Room does not exist.'}))
        except Exception as e:
            logger.error(f'An error occurred while joining the room: {e}', exc_info=True)
            await self.consumer.send(text_data=json.dumps({'type': 'error', 'message': 'Could not join room.'}))

    async def handle_leave_room(self, room_id, user):
        try:
            room = await self.room_service.get_room(room_id)
            if room:
                await self.room_service.remove_participant(room, user)
                await self.consumer.send(text_data=json.dumps({'type': 'roomLeft', 'room_id': room_id}))
            else:
                await self.consumer.send(text_data=json.dumps({'type': 'error', 'message': 'Room does not exist.'}))
        except Exception as e:
            logger.error(f'An error occurred while leaving the room: {e}', exc_info=True)
            await self.consumer.send(text_data=json.dumps({'type': 'error', 'message': 'Could not leave room.'}))

    async def serialize_room_data(self, room):
        from userroom.serializers import UserRoomSerializer
        
        return await database_sync_to_async(lambda: UserRoomSerializer(room).data)()
