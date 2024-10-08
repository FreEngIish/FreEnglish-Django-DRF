# RoomCommands Class Documentation WebSocket.

## Overview

The `RoomCommands` class handles WebSocket commands for managing rooms. It allows users to create, join, leave, and edit rooms, and communicates with the `RoomService` to manage these operations.

## Table of Contents

- [Class: RoomCommands](#class-roomcommands)
  - [Method: `handle_create_room`](#method-handle_create_room)
  - [Method: `handle_filter_rooms`](#method-handle_filter_rooms) 
  - [Method: `handle_search_rooms`](#method-handle_search_rooms)  
  - [Method: `handle_join_room`](#method-handle_join_room)
  - [Method: `handle_leave_room`](#method-handle_leave_room)
  - [Method: `handle_edit_room`](#method-handle_edit_room)

---
# Commands for /ws/main/

## Class: RoomCommands

## Method: `handle_create_room`

### Parameters:
- `data`: A dictionary containing the following fields:
  - `room_name` (required): The name of the room.
  - `native_language` (required): The native language of the room.
  - `language_level` (optional): The language level (default: `'Beginner'`).
  - `participant_limit` (optional): The maximum number of participants (default: `10`).
- `user`: The user creating the room.

### Logic:
- Validates that the required fields are provided.
- Calls the `RoomService` to create a new room.
- Sends a success message with the room data, or an error message if something goes wrong.

### WebSocket Message:
```json
{
  "token": "JWT_Token",
  "type": "createRoom",
  "data": {
    "room_name": "English Practice",
    "native_language": "English",
    "language_level": "Intermediate",
    "participant_limit": 10,
    "description": "description"
  }
}
```

---

## Method: `handle_filter_rooms`

### Parameters:
- `language_level` (optional): The desired language level for filtering.
- `min_participants` (optional): The minimum number of participants in the room.
- `max_participants` (optional): The maximum number of participants in the room.

### Logic:
- Filters the list of rooms based on the provided criteria (`language_level`, `min_participants`, and `max_participants`).
- Calls the `RoomService` to fetch the filtered list of rooms.
- Sends the filtered list of rooms back to the client.

### WebSocket Message:
```json
{
  "type": "filterRooms",
  "data": {
    "language_level": "Intermediate",
    "min_participants": 0,
    "max_participants": 10
  }
}
```

---

## Method: `handle_search_rooms`

### Parameters:
- `search_query`: A string containing the name or part of the name of the room to search.

### Logic:
- Calls the `RoomService` to retrieve rooms that match the search query.
- Sends the filtered list of rooms back to the client, or sends an error message if something goes wrong.

### WebSocket Message:
```json
{
  "token": "JWT_Token",
  "type": "searchRoom",
  "data": {
    "query": "English"
  }
}
```

### Response Message:
```json
{
  "type": "searchResults",
  "rooms": [
    {
      "room_id": 1,
      "room_name": "English Practice",
      "native_language": "English",
      "language_level": "Beginner",
      "participant_limit": 10,
      "description": "Basic English practice"
    },
    ...
  ]
}
```

# Commands for /ws/rooms/<id_room>/

---

## Method: `handle_join_room`
### Parameters:
- `room_id:` The ID of the room the user wants to join.
- `user:` The user who is joining the room.

### Logic:
  - Retrieves the room from the `RoomService`.
  - Checks if the room exists and if it has space for more participants.
  - Adds the user to the room and sends a success message, or sends an error message if the room is full or doesn't exist.

### WebSocket Message:
```json
{
    "token": "JWT_Token",
  "type": "joinRoom"
}
```

## Method: `handle_leave_room`
### Parameters:
- `room_id:` The ID of the room the user wants to leave.
- `user:` The user leaving the room.
### Logic:
- Retrieves the room from the `RoomService`.
- `Removes` the user from the room and sends a success message, or sends an error message if the user wasn't a participant.
### WebSocket Message:
```json
{
    "token": "JWT_Token",
  "type": "leaveRoom"
}
```
## Method: `handle_edit_room`
### Parameters:
- `room_id`: The ID of the room to edit.
- `user`: The user making the request (must be the room creator).
- `data`: A dictionary with the updated room details (e.g., room_name, native_language, language_level, participant_limit).
- ### Logic:
- Verifies that the user is the creator of the room.
- Updates the room details using the provided data, or sends an error message if the user doesn't have permission.
### WebSocket Message:
```json
{
  "token": "JWT_Token",
  "type": "editRoom",
  "room_id": "47eb28c571ed40dea4b59b3e422f1bb2",
  "data": {
    "room_name": "Advanced English",
    "native_language": "English",
    "language_level": "Advanced",
    "participant_limit": 5,
    "description": "description"
  }
}
```
