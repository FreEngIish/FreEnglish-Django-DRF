# WebRTC WebSocket API

----

## SDP exchange

### Example of sending SDP via WebSocket:
  - `URL WebSocket`: `ws://example.com/ws/rooms/{room_id}/`
  - `Message type`: `sdp`
  - `Description`: Send SDP offer or answer so that participants can set connection parameters (audio, video, etc.).
#### Example of message structure (JSON):
```json
{
  "type": "sdp",
  "sdp": {
    "type": "offer",  // или "answer"
    "sdp": "v=0\r\no=- 4611739839264850505 2 IN IP4 127.0.0.1\r\ns=-\r..."
  }
}
```
#### Response from the server:
When another member of the room receives SDP, the server will send a reply message with the type `sdp`.
```json
{
  "type": "sdp",
  "sdp": {
    "type": "answer",
    "sdp": "v=0\r\no=- 4611739839264850505 2 IN IP4 127.0.0.1\r\ns=-\r..."
  },
  "sender": "username_of_other_participant"
}
```
### Exchange of ICE candidates
ICE candidates are required to establish a connection between WebRTC participants, even if they are behind NAT or firewalls. ICE candidates are also generated on the WebRTC client side and transmitted via WebSocket to the server.
#### An example of sending an ICE candidate via WebSocket:
  - `URL WebSocket`: `ws://example.com/ws/rooms/{room_id}/`
  - `Message type`: `ice_candidate`
  - `Description`: Send ICE candidates to provide a direct connection between participants.
#### Example of message structure (JSON):
```json
{
  "type": "ice_candidate",
  "candidate": {
    "candidate": "candidate:842163049 1 udp 1677729535 192.168.1.10 54121 typ srflx raddr 192.168.1.10 rport 54121 generation 0 ufrag 1zdr network-id 1",
    "sdpMid": "audio",
    "sdpMLineIndex": 0
  }
}
```
#### Response from the server:
When another participant receives an ICE candidate, the server will send a message with type `ice_candidate`
```json
{
  "type": "ice_candidate",
  "candidate": {
    "candidate": "candidate:842163049 1 udp 1677729535 192.168.1.10 54121 typ srflx raddr 192.168.1.10 rport 54121 generation 0 ufrag 1zdr network-id 1",
    "sdpMid": "audio",
    "sdpMLineIndex": 0
  },
  "sender": "username_of_other_participant"
}
```

#### Example of a common process (SDP + ICE candidates):
1. One participant generates an **SDP offer** and sends it via WebSocket.
2. Another participant receives this offer, generates an **SDP answer**, and sends it via WebSocket.
3. Both participants start exchanging **ICE candidates** by sending them to each other through the server.