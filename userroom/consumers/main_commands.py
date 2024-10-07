import json
import logging
from typing import Any

from userroom.services.room_service import RoomService
from userroom.tasks import deactivate_empty_room_after_creation


logger = logging.getLogger('freenglish')


class MainCommands:
    def __init__(self, consumer):
        self.consumer = consumer
        self.room_service = RoomService()

    async def handle_create_room(self, data: dict[str, Any], user):
        try:
            user_rooms_count = await self.room_service.count_user_rooms(user)
            if user_rooms_count >= 3:
                await self.consumer.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'You can only create up to 3 rooms.'
                }))
                return

            room_name = data.get('room_name')
            native_language = data.get('native_language')
            language_level = data.get('language_level', 'Beginner')
            participant_limit = data.get('participant_limit', 10)
            description = data.get('description', '')

            if not room_name or not native_language or not language_level:
                await self.consumer.send(text_data=json.dumps({'type': 'error', 'message': 'Missing required fields'}))
                return

            room = await self.room_service.create_room(
                room_name=room_name,
                native_language=native_language,
                language_level=language_level,
                participant_limit=participant_limit,
                creator=user,
                description=description,
            )

            deactivate_empty_room_after_creation.apply_async((room.room_id,), countdown=900)

            await self.consumer.channel_layer.group_send(
                'rooms_group',
                {
                    'type': 'get_all_rooms',
                }
            )

        except Exception as e:
            logger.error(f'An error occurred while creating a room: {e}', exc_info=True)
            await self.consumer.send(
                text_data=json.dumps(
                    {'type': 'error', 'message': 'An error occurred while creating the room. Please try again later.'}
                )
            )
