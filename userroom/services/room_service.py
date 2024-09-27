from channels.db import database_sync_to_async


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
        RoomMembers.objects.create(room=room, user=creator)
        return room