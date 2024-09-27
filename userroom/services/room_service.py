import logging

from channels.db import database_sync_to_async


logger = logging.getLogger('freenglish')

class RoomService:
    @database_sync_to_async
    def create_room(self, room_name, native_language, language_level, participant_limit, creator):
        from userroom.models import RoomMembers, UserRoom

        room = UserRoom(
            room_name=room_name,
            native_language=native_language,
            language_level=language_level,
            participant_limit=participant_limit,
            creator=creator,
        )
        room.save()
        room.current_participants.add(creator)
        RoomMembers.objects.create(room=room, user=creator)
        return room

    @database_sync_to_async
    def get_room(self, room_id):
        from userroom.models import UserRoom
        return UserRoom.objects.filter(room_id=room_id).first()

    @database_sync_to_async
    def add_participant(self, room, user):
        from userroom.models import RoomMembers
        if not room.current_participants.filter(id=user.id).exists():
            room.current_participants.add(user)
            RoomMembers.objects.create(room=room, user=user)
            return True
        return False

    @database_sync_to_async
    def remove_participant(self, room, user):
        from userroom.models import RoomMembers

        if room.current_participants.filter(id=user.id).exists():
            room.current_participants.remove(user)

            RoomMembers.objects.filter(room=room, user=user).delete()
            return True
        return False

    @database_sync_to_async
    def count_participants(self, room):
        return room.current_participants.count()
