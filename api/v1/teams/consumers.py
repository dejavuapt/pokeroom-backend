from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import sync_to_async, database_sync_to_async
from apps.core.teams.models import Team
import json

class TeamConsumer(AsyncWebsocketConsumer):
    async def connect(self):        
        user = self.scope['user']
        if user.is_authenticated:
            self.team_id: str = self.scope.get("url_route").get("kwargs").get("id")
            self.team_group_name: str = f"team_{self.team_id}"
            await self.channel_layer.group_add(self.team_group_name,
                                               self.channel_name)
            await self.accept()
        else:
            await self.close()
    
    async def receive(self, text_data):
        team_id = self.scope.get("url_route").get("kwargs").get('id')
        team_name = await self.get_team_name_by_id(team_id)
        
        await self.channel_layer.group_send(self.team_group_name,
                                            {'type': 'team.info', 
                                             'id': team_id,
                                             'name': team_name,})
    
    async def team_info(self, event):
        id = event.get('id')
        name = event.get('name')
        
        await self.send(text_data=json.dumps({'id': id, 'name': name}))
    
    @database_sync_to_async
    def get_team_name_by_id(self, id) -> str:
        return Team.objects.get(id = id).name