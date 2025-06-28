from channels.generic.websocket import AsyncWebsocketConsumer
import json

class TeamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if user.is_authenticated:
            await self.accept()
        else:
            await self.close()
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message', '')
        except json.JSONDecodeError:
            message = text_data

        await self.send(text_data=json.dumps({
            'message': message,
            'echo': True
        }))