import json
import logging
from typing import Any

from userroom.services.room_service import RoomService


logger = logging.getLogger('freenglish')

class MainCommands:
    def __init__(self, consumer):
        self.consumer = consumer
        self.room_service = RoomService()

    async def handle_create_room(self, data: dict[str, Any], user):
        try:
            room_name = data.get('room_name')
            native_language = data.get('native_language')
            language_level = data.get('language_level', 'Beginner')
            participant_limit = data.get('participant_limit', 10)

            if not room_name or not native_language or not language_level:
                await self.consumer.send(text_data=json.dumps({'type': 'error', 'message': 'Missing required fields'}))
                return

            room = await self.room_service.create_room(
                room_name=room_name,
                native_language=native_language,
                language_level=language_level,
                participant_limit=participant_limit,
                creator=user,
            )

            room_data = await self.room_service.serialize_room_data(room)
            self.consumer.room_id = room_data['room_id']

            # Отправка информации о новой комнате всем подключенным клиентам
            await self.consumer.channel_layer.group_send(
                'rooms_group',  # Название группы для всех комнат
                {
                    'type': 'room_created',  # Тип события
                    'room': room_data,
                }
            )

            # await self.consumer.send(text_data=json.dumps({'type': 'roomCreated', 'room': room_data}))

        except Exception as e:
            logger.error(f'An error occurred while creating a room: {e}', exc_info=True)
            await self.consumer.send(
                text_data=json.dumps(
                    {'type': 'error', 'message': 'An error occurred while creating the room. Please try again later.'}
                )
            )
