from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.games.models.models import GameInstance, GameState, Player, GameRoleChoices
from apps.games.models.poker_planning import TaskEvaluationGameState, LobbyGameState

User = get_user_model()

class GameinstanceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = GameInstance
        fields = ('host_by', 'type', 'status', 'config', 'created_at')
        extra_kwargs = {'host_by': {'read_only': True},
                        'type': {'read_only': True}}

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
        
class TaskevaluationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TaskEvaluationGameState
        fields = ('game', 'name', 'completed', 'result_data',
                  'tasks', 'current_task', 'players_votes')
        
class LobbySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = LobbyGameState
        fields = ('game', 'name', 'completed', 'result_data')