import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

from userroom.consumers.room_commands import RoomCommands
from userroom.services.room_service import RoomService
from userroom.services.user_service import UserService


logger = logging.getLogger('freenglish')

class RoomConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.commands = RoomCommands(self)
        self.user_service = UserService()
        self.room_service = RoomService()
        self.room_id = None

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs'].get('room_id')

        if await self.room_exists(self.room_id):
            await self.accept()
        else:
            await self.close()
            logger.warning(f'Tried to connect to non-existent room {self.room_id}')

    async def disconnect(self, close_code):  # noqa: ARG002
        if self.room_id and self.user:
            await self.commands.handle_leave_room(self.room_id, self.user)

    async def receive(self, text_data=None, bytes_data=None):
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
                elif message_type == 'getAllRooms':
                    await self.handle_get_all_rooms()  # Получить все комнаты
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
            rooms_data = [await self.room_service.serialize_room_data(room) for room in rooms]
            await self.send(text_data=json.dumps({'type': 'allRooms', 'rooms': rooms_data}))
        except Exception as e:
            logger.error(f'An error occurred while fetching all rooms: {e}', exc_info=True)
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Could not retrieve rooms.'}))
