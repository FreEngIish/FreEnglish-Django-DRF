import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from userroom.consumers.room_commands import RoomCommands
from userroom.services.room_service import RoomService
from userroom.services.user_service import UserService
from userroom.tasks import deactivate_room_if_empty

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
            await self.channel_layer.group_add(f'room_{self.room_id}', self.channel_name)
        else:
            await self.close()
            logger.warning(f'Tried to connect to non-existent room {self.room_id}')

    async def disconnect(self, close_code):  # noqa: ARG002
        if self.room_id and self.user:
            await self.commands.handle_leave_room(self.room_id, self.user)
            await self.channel_layer.group_discard(f'room_{self.room_id}', self.channel_name)
            room = await self.room_service.get_room(self.room_id)
            if room:
                participant_count = await self.room_service.count_participants(room)
                logger.info(f"In room {self.room_id} remaining participants: {participant_count}")

                if participant_count == 0:
                    logger.info(f"Room {self.room_id} is empty. Starting the deactivation task.")
                    deactivate_room_if_empty.apply_async((self.room_id,), countdown=900)
                    logger.info(f"The task of deactivating the room {self.room_id} added to the queue.")
        await self.channel_layer.group_discard(f'room_{self.room_id}', self.channel_name)

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

                if message_type == 'joinRoom':
                    if await self.room_exists(self.room_id):
                        await self.commands.handle_join_room(self.room_id, user=self.user)
                    else:
                        await self.send(text_data=json.dumps({
                            'type': 'error',
                            'message': 'Room does not exist.'
                        }))
                elif message_type == 'leaveRoom':
                    await self.commands.handle_leave_room(self.room_id, user=self.user)
                elif message_type == 'editRoom':
                    await self.commands.handle_edit_room(self.room_id, user=self.user, data=data)
                elif message_type == 'sdp':
                    await self.handle_sdp(data, self.room_id)
                elif message_type == 'ice_candidate':
                    await self.handle_ice_candidate(data, self.room_id)
                else:
                    await self.send(text_data=json.dumps({'type': 'error', 'message': 'Unknown message type'}))

            except json.JSONDecodeError:
                logger.error('Invalid JSON received: %s', text_data)
                await self.send(text_data=json.dumps({'type': 'error', 'message': 'Invalid JSON'}))
            except Exception as e:
                logger.error('Error processing message: %s', str(e))
                await self.send(text_data=json.dumps({'type': 'error', 'message': 'An unexpected error occurred'}))

    async def participants_list(self, event):
        participants = event['participants']
        await self.send(text_data=json.dumps({
            'type': 'participantsList',
            'participants': participants
        }))

    async def handle_sdp(self, data, room_id):
        logger.info(f"Received SDP data: {data}")

        if 'sdp' in data:
            await self.channel_layer.group_send(
                f'room_{room_id}',
                {
                    'type': 'sdp',
                    'sdp': data['sdp'],
                    'sender': self.user.username
                }
            )
        else:
            logger.error(f"SDP data missing in: {data}")
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'SDP data missing'}))

    async def sdp(self, event):
        await self.send(text_data=json.dumps({
            'type': 'sdp',
            'sdp': event['sdp'],
            'sender': event['sender']
        }))

    async def handle_ice_candidate(self, data, room_id):
        if 'candidate' in data:
            await self.channel_layer.group_send(
                f'room_{room_id}',
                {
                    'type': 'ice_candidate',
                    'candidate': data['candidate'],
                    'sender': self.user.username
                }
            )
        else:
            logger.error(f"ICE candidate data missing in: {data}")
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'ICE candidate data missing'}))

    async def ice_candidate(self, event):
        await self.send(text_data=json.dumps({
            'type': 'ice_candidate',
            'candidate': event['candidate'],
            'sender': event['sender']
        }))

    async def room_exists(self, room_id):
        return await self.room_service.get_room(room_id) is not None
