from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.games.models.models import GameInstance, GameState, Player, GameRoleChoices, GameInstanceStatusChoices, GameTypesChoices
from apps.games.models.poker_planning import TaskEvaluationGameState, LobbyGameState

User = get_user_model()

class PlayerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Player
        fields = ('user', 'role')
        
    def to_representation(self, instance):
        repr: dict = super().to_representation(instance)
        _id = repr.pop('user')
        return {
            "username": User.objects.get(pk=_id).username,
            "role": str(GameRoleChoices(repr.get('role')).label)
        }
        
class GameinstanceSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    
    class Meta:
        model = GameInstance
        fields = ('id', 'host_by', 'type', 'status', 'config', 'players','created_at')
        extra_kwargs = {'id': {'read_only': True},
                        'host_by': {'read_only': True},
                        'type': {'read_only': True}}
    
    def to_representation(self, instance):
        repr: dict = super().to_representation(instance)
        t_s = {"type": str(GameTypesChoices(repr.get('type')).label), 
               "status": str(GameInstanceStatusChoices(repr.get('status')).label),
               "host_by": str(User.objects.get(pk=repr.get("host_by")).username)}
        repr.update(t_s)
        return repr
        

        
class TaskevaluationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TaskEvaluationGameState
        fields = ('game', 'name', 'completed', 'result_data',
                  'tasks', 'current_task', 'players_votes')
        
class LobbySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = LobbyGameState
        fields = ('game', 'name', 'completed', 'result_data')