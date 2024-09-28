import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

from userroom.services.room_service import RoomService
from userroom.services.user_service import UserService


logger = logging.getLogger('freenglish')

class MainConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_service = UserService()
        self.room_service = RoomService()
        self.user = None

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        data = text_data_json.get('data', {})

        if message_type == 'createRoom':
            token = text_data_json.get('token')
            if token:
                self.user = await self.user_service.get_user_from_token(token)
                if not self.user:
                    await self.send(text_data=json.dumps({'type': 'error', 'message': 'Invalid token.'}))
                    return
            await self.handle_create_room(data)

    async def handle_create_room(self, data):
        try:
            room_name = data.get('room_name')
            native_language = data.get('native_language')
            language_level = data.get('language_level', 'Beginner')
            participant_limit = data.get('participant_limit', 10)

            if not room_name or not native_language or not language_level:
                await self.send(text_data=json.dumps({'type': 'error', 'message': 'Missing required fields'}))
                return

            room = await self.room_service.create_room(
                room_name=room_name,
                native_language=native_language,
                language_level=language_level,
                participant_limit=participant_limit,
                creator=self.user,
            )

            room_data = await self.room_service.serialize_room_data(room)
            await self.send(text_data=json.dumps({'type': 'roomCreated', 'room': room_data}))

        except Exception as e:
            logger.error(f'Error creating room: {e}')
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'An error occurred while creating the room.'}))  # noqa: E501
