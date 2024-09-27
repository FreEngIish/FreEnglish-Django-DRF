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
                    added = await self.room_service.add_participant(room, user)
                    if added:
                        await self.consumer.send(text_data=json.dumps({
                            'type': 'success',
                            'message': f'You have successfully joined the room "{room.room_name}".'
                        }))
                        logger.info(f'Participant {user.email} added to RoomMembers for room {room.room_name}')
                    else:
                        await self.consumer.send(text_data=json.dumps({
                            'type': 'info',
                            'message': f'You are already a participant in the room "{room.room_name}".'
                        }))
                        logger.warning(f'Participant {user.email} already in RoomMembers for room {room.room_name}')
                else:
                    await self.consumer.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'Room is full.'
                    }))
            else:
                await self.consumer.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Room does not exist.'
                }))
        except Exception as e:
            logger.error(f'An error occurred while joining the room: {e}', exc_info=True)
            await self.consumer.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Could not join room.'
            }))

    async def handle_leave_room(self, room_id, user):
        try:
            room = await self.room_service.get_room(room_id)
            if room:
                removed = await self.room_service.remove_participant(room, user)
                if removed:
                    await self.consumer.send(text_data=json.dumps({
                        'type': 'success',
                        'message': f'You have left the room "{room.room_name}".'
                    }))
                    logger.info(f'Participant {user.email} removed from RoomMembers for room {room.room_name}')
                else:
                    await self.consumer.send(text_data=json.dumps({
                        'type': 'info',
                        'message': f'You were not a participant in the room "{room.room_name}".'
                    }))
                    logger.warning(f'Participant {user.email} not found in RoomMembers for room {room.room_name}')
            else:
                await self.consumer.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Room does not exist.'
                }))
        except Exception as e:
            logger.error(f'An error occurred while leaving the room: {e}', exc_info=True)
            await self.consumer.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Could not leave room.'
            }))

    async def handle_edit_room(self, room_id, user, data):
        try:
            room = await self.room_service.get_room(room_id)
            if room:
                creator = await database_sync_to_async(lambda: room.creator)()
                if creator.id == user.id:
                    room_name = data.get('room_name')
                    native_language = data.get('native_language')
                    language_level = data.get('language_level')
                    participant_limit = data.get('participant_limit')

                    updated_room = await self.room_service.update_room(
                        room,
                        room_name=room_name,
                        native_language=native_language,
                        language_level=language_level,
                        participant_limit=participant_limit
                    )

                    await self.consumer.send(text_data=json.dumps({
                        'type': 'success',
                        'message': 'Room updated successfully.'
                    }))
                    logger.info(f'Room {room.room_name} updated by {user.email}')
                else:
                    await self.consumer.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'You do not have permission to edit this room.'
                    }))
            else:
                await self.consumer.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Room does not exist.'
                }))
        except Exception as e:
            logger.error(f'An error occurred while editing the room: {e}', exc_info=True)
            await self.consumer.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Could not edit room.'
            }))
