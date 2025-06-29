from apps.games.models.models import GameInstance, GameState, GameTypesChoices, GameRoleChoices
from apps.games.models.poker_planning import TaskEvaluationGameState, LobbyGameState
from apps.games.core.engine import GameEngine
from api.v1.games.serializers import *

from apps.core.teams.models import Team

from typing import Optional
import logging
logger = logging.getLogger()

from rest_framework import viewsets, response, status, mixins, decorators
from django.shortcuts import get_object_or_404
from http import HTTPMethod

class PokerGameViewset(viewsets.GenericViewSet,
                       mixins.ListModelMixin,
                       mixins.CreateModelMixin):
    serializer_class = GameinstanceSerializer
    # POST poker means create it
    def get_queryset(self):
        team_id = self.kwargs.get("id", None)
        return GameInstance.objects.filter(team = Team.objects.get(pk = team_id))
    
    def create(self, request, *args, **kwargs):
        # TODO: add support rules {"rule": [1,2,3,4,5]}
        t: Team = get_object_or_404(Team.objects.all(), id = self.kwargs.get("id", None))
        logger.warning(f"{type(t.owner_id)}, {type(self.request.user)}")
        if t.owner_id != self.request.user:
            self.permission_denied(self.request, 
                                   code=status.HTTP_403_FORBIDDEN)
        try:
            eng = GameEngine().bootstrap_or_resume(team=t,
                                                game_type=GameTypesChoices.POKER,
                                                init_user=self.request.user)
            serializer = self.get_serializer(eng._game_instance)
        except Exception as exc: 
            return response.Response({"detail": str(exc)},
                                      status=status.HTTP_400_BAD_REQUEST)
        return response.Response(serializer.data,
                                 status=status.HTTP_201_CREATED)
    
    # GET - get current game
    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return response.Response(serializer.data, 
                                 status=status.HTTP_200_OK)
    
class PokergameDoViewset(viewsets.GenericViewSet):
    """
    get_current_state
    GET state
    join connect to game who in a team
    GET POST players
    
    lobby
    POST add_task if user is facilitator
    # add_more_tasks -- parser
    
    poker state
    GET POST current_task
    
    POST estimate -- add user estimate
    GET estimate -- get current task estimate if user role is facilitator
    
    get_current_task
    set_current_task if user role is facilitator
    add_user_estimate acces to players
    calculate_current_task_estimate if user role is facilitator
    update_task if user role is facilitator
    
    close_game
    """
    
    def get_queryset(self):
        team_id = self.kwargs.get("id", None)
        return GameInstance.objects.filter(team = Team.objects.get(pk = team_id))
    
    def get_object(self):
        game_object = self.get_queryset().first()
        if game_object and game_object.players.get(user=self.request.user).role != GameRoleChoices.FACILITATOR:
            self.permission_denied(self.request, 
                                   code=status.HTTP_405_METHOD_NOT_ALLOWED)
        return game_object
        
    
    @decorators.action(methods=[HTTPMethod.GET, HTTPMethod.POST],
                       detail=False)
    def state(self, request, *args, **kwargs) -> response.Response:
        if request.method == HTTPMethod.GET:
            gi = self.get_queryset().first()
            if gi is not None:
                state_name = GameEngine().resume_by_gi(gi)._game_manager._current_state.name
                return response.Response({"current_state": state_name},
                                         status=status.HTTP_200_OK)
        
        if request.method == HTTPMethod.POST:
            gi = self.get_object()
            if gi is not None:
                gm = GameEngine().resume_by_gi(gi)._game_manager
                prev_state_name: str = gm._current_state.name
                gm.state_forward()
                new_state_name: str = gm._current_state.name
                return response.Response({"detail": f"Completed transfer from {prev_state_name} to {new_state_name} state."},
                                         status=status.HTTP_200_OK)
                
        return response.Response({"detail": "something wrong"}, 
                                 status=status.HTTP_501_NOT_IMPLEMENTED)
                
    
    @decorators.action(methods=[HTTPMethod.GET, HTTPMethod.POST], 
                       detail=False)
    def players(self, request, *args, **kwargs) -> response.Response:
        if request.method == HTTPMethod.GET:
            gi = self.get_queryset().first()
            if gi:
                return response.Response(PlayerSerializer(gi.players, many=True).data,
                                         status=status.HTTP_200_OK)
        
        if request.method == HTTPMethod.POST:
            return response.Response(status=status.HTTP_501_NOT_IMPLEMENTED)
        
        return response.Response({"detail": "something wrong"}, 
                                 status=status.HTTP_501_NOT_IMPLEMENTED)
     
    @decorators.action(methods=[HTTPMethod.POST], 
                       detail=False)
    def add_task(self, request, *args, **kwargs) -> response.Response:
        task_name: str = request.data.get("title", None)
        gi: Optional[GameInstance] = self.get_object()
        if task_name and gi:
            try:
                GameEngine().resume_by_gi(gi).do('add-task', 
                                                 {"name": task_name})
                return response.Response({"detail": f"Success add a task with title {task_name}."},
                                         status=status.HTTP_201_CREATED)
            except Exception as exc:
                return response.Response({"detail": str(exc)},
                                         status=status.HTTP_400_BAD_REQUEST)
            
        return response.Response({"detail": "Not provided titile of task or game not started"},
                                 status=status.HTTP_400_BAD_REQUEST)
        
        
    @decorators.action(methods=[HTTPMethod.GET, HTTPMethod.POST], 
                       detail=False)
    def current_task(self, request, *args, **kwargs) -> response.Response:
        pass
    
    @decorators.action(methods=[HTTPMethod.GET, HTTPMethod.POST], 
                       detail=False)
    def estimate(self, request, *args, **kwargs) -> response.Response:
        pass
    
    