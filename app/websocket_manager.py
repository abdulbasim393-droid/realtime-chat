from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[
        int,
        list[WebSocket]
        ] = {}

    async def connect(
    self,
    conversation_id: int,
    websocket: WebSocket
    ):
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        
        self.active_connections[conversation_id].append(websocket)

    def disconnect(self, conversation_id: int, websocket: WebSocket):
        self.active_connections[conversation_id].remove(websocket)

        if not self.active_connections[conversation_id]:
            del self.active_connections[conversation_id]

    async def send_personal_message(
        self,
        message: str,
        websocket: WebSocket
    ):
        await websocket.send_text(message)

    async def broadcast(self, conversation_id: int, message):
        dead_connections = []
        print("Connections:", len(self.active_connections.get(conversation_id, [])))

        for connection in self.active_connections.get(conversation_id, []):
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)
                print("Sending to:", connection.client)
        for connection in dead_connections:
            self.disconnect(conversation_id, connection)


manager = ConnectionManager()