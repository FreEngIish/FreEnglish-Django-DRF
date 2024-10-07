import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

from userroom.consumers.main_commands import MainCommands
from userroom.services.room_service import RoomService
from userroom.services.user_service import UserService


logger = logging.getLogger('freenglish')

class MainConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.commands = MainCommands(self)
        self.user_service = UserService()
        self.room_service = RoomService()
        self.room_id = None

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add('rooms_group', self.channel_name)

        await self.handle_get_all_rooms()

    async def disconnect(self, close_code):  # noqa: ARG002
        await self.channel_layer.group_discard('rooms_group', self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):  # noqa: ARG002
        if text_data is not None:
            try:
                text_data_json = json.loads(text_data)
                token = text_data_json.get('token')
                if token:
                    self.user = await self.user_service.get_user_from_token(token)
                    if not self.user:
                        await self.send(text_data=json.dumps({'type': 'error', 'message': 'Invalid token.'}))
                        return

                message_type = text_data_json.get('type')
                data = text_data_json.get('data', {})

                if message_type == 'createRoom':
                    await self.commands.handle_create_room(data, user=self.user)
                else:
                    await self.send(text_data=json.dumps({'type': 'error', 'message': 'Unknown message type'}))

            except json.JSONDecodeError:
                logger.error('Invalid JSON received: %s', text_data)
                await self.send(text_data=json.dumps({'type': 'error', 'message': 'Invalid JSON'}))
            except Exception as e:
                logger.error('Error processing message: %s', str(e))
                await self.send(text_data=json.dumps({'type': 'error', 'message': 'An unexpected error occurred'}))

    async def room_created(self, event):
        room_data = event['room']
        await self.send(text_data=json.dumps({'type': 'roomCreated', 'room': room_data}))

    async def handle_get_all_rooms(self):
        try:
            rooms = await self.room_service.get_all_rooms()
            rooms_data = await self.room_service.serialize_rooms_data(rooms)

            await self.send(text_data=json.dumps({'type': 'allRooms', 'rooms': rooms_data}))
        except Exception as e:
            logger.error(f'An error occurred while fetching all rooms: {e}', exc_info=True)
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Could not retrieve rooms.'}))
    async def get_all_rooms(self, event):  # noqa: ARG002
        await self.handle_get_all_rooms()
