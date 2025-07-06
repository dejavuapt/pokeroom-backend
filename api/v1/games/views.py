from apps.games.models.models import GameInstance, GameState, GameTypesChoices, GameRoleChoices, Player
from apps.games.models.poker_planning import TaskEvaluationGameState, LobbyGameState
from apps.games.core.engine import GameEngine
from api.v1.games.serializers import *

from typing import Optional
import logging
logger = logging.getLogger()

from rest_framework import viewsets, response, status, mixins, decorators
from django.shortcuts import get_object_or_404
from http import HTTPMethod

def format_msg(msg: str) -> dict[str, str]:
    return {"detail": msg}

class PokerGameViewset(viewsets.GenericViewSet,
                       mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin):
    serializer_class = GameinstanceSerializer
    def get_queryset(self):
        return GameInstance.objects.all()
    
    def create(self, request, *args, **kwargs):
        """
        Request:
            { "rule": "1,2,3,4,5,-,c,p" }
        """
        try:
            rule: str | None = request.data.get("rule", None)
            e: GameEngine = GameEngine.build(GameTypesChoices.POKER, 
                                             self.request.user,
                                             props={"rule": rule} if rule else None)
            serializer = self.get_serializer(e.game_instance)
        except Exception as exc: 
            return response.Response({"detail": str(exc)},
                                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response.Response(serializer.data,
                                 status=status.HTTP_201_CREATED)
        
    @decorators.action(methods=[HTTPMethod.POST], detail=False)
    def join(self, request, *args, **kwargs): 
        game_id: str = request.data.get("id", None)
        if game_id:
            try:
                instance: GameInstance = get_object_or_404(GameInstance.objects.all(), pk = game_id)
                new_player: Player = instance.add_player(self.request.user)
                serializer = PlayerSerializer(new_player)
                return response.Response(serializer.data,
                                         status=status.HTTP_200_OK)
            except Exception as exc:
                return response.Response(format_msg(str(exc)), 
                                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return response.Response(format_msg("`id` label not provided"),
                                 status=status.HTTP_400_BAD_REQUEST)
    

class StateViewset(viewsets.GenericViewSet,
                   mixins.ListModelMixin):
    queryset = GameInstance.objects.all()
    
    def get_object(self):
        game_id = self.kwargs.get("id", None)
        g: GameInstance = get_object_or_404(self.queryset, pk=game_id)
        return g
    
    def list(self, request, *args, **kwargs):
        g: GameInstance = self.get_object()
        current_state: str = GameEngine.resume(g).manager._current_state.name
        return response.Response({"current_state": current_state}, 
                                 status=status.HTTP_200_OK)
    
    @decorators.action(methods=[HTTPMethod.POST], detail=False)
    def forward(self, request, *args, **kwargs):
        g: GameInstance = self.get_object()
        if self._is_facilitator(self.request.user):
            GameEngine.resume(g).forward()
            return response.Response(status=status.HTTP_200_OK)
        else:
            return response.Response(format_msg("You can't step forward state."),
                                      status=status.HTTP_406_NOT_ACCEPTABLE)
        
    def _is_facilitator(self, user) -> bool:
        game_object: GameInstance = self.get_object()
        if Player.objects.filter(user = user, game = game_object).exists():
            return Player.objects.get(user = user, game = game_object).role == GameRoleChoices.FACILITATOR
        raise ValueError("Player doesn't exist.")

class PlayersViewset(viewsets.GenericViewSet,
                     mixins.ListModelMixin):
    def list(self, request, *args, **kwargs):
        game_id = self.kwargs.get("id", None)
        if game_id:
            g: GameInstance = get_object_or_404(GameInstance.objects.all(), pk=game_id)
            serializer = PlayerSerializer(g.players, many=True)
            return response.Response(serializer.data, status=status.HTTP_200_OK)
    
    @decorators.action(methods=[HTTPMethod.GET], detail=False)
    def votes(self, request, *args, **kwargs):
        game_id = self.kwargs.get("id", None)
        if game_id:
            try:
                g: GameInstance = get_object_or_404(GameInstance.objects.all(), pk =game_id)
                e: GameEngine = GameEngine.resume(g)
                s: TaskEvaluationGameState = e.manager._current_state.instance
                return response.Response(s.players_votes, status=status.HTTP_200_OK)
            except Exception as exc:
                return response.Response(format_msg(str(exc)), 
                                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class TaskEvaluationViewset(viewsets.GenericViewSet,
                            mixins.CreateModelMixin,
                            mixins.ListModelMixin,
                            mixins.RetrieveModelMixin):
    lookup_field = 'title'
    
    def get_object(self):
        game_id = self.kwargs.get("id", None)
        g: GameInstance = get_object_or_404(GameInstance.objects.all(), pk=game_id)
        return g
    
    # add_task in start lobby and task evaluation stage
    def create(self, request, *args, **kwargs):
        title: str = request.data.get('title', None)
        if title:
            g: GameInstance = self.get_object()
            if title in g.config.get("tasks"):
                return response.Response(format_msg("Can't add duplicate tasks."),
                                        status=status.HTTP_400_BAD_REQUEST)
            try:
                GameEngine.resume(g).do('add-task', 
                                       {'name': title})
                return response.Response(status=status.HTTP_201_CREATED)
            except Exception as exc:
                return response.Response(format_msg(str(exc)), 
                                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response.Response(format_msg("Not provided `title` label"),
                                 status=status.HTTP_400_BAD_REQUEST)
        
    # get all tasks of task evaluation stage
    def list(self, request, *args, **kwargs):
        try:
            g: GameInstance = self.get_object()
            # TODO: Many long request, need to split it
            rd: dict = GameEngine.resume(g).game_instance.config.get("data", None)
            return response.Response(rd, status=status.HTTP_200_OK)
        except Exception as exc:
            return response.Response(format_msg(str(exc)), 
                                     status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
    
    def retrieve(self, request, *args, **kwargs):
        title = self.kwargs.get('title', None)
        return response.Response({"detail": title}, status=status.HTTP_200_OK)
        # return super().retrieve(request, *args, **kwargs)
        
    @decorators.action(methods=[HTTPMethod.POST, HTTPMethod.GET], detail=False)
    def current(self, request, *args, **kwargs) -> response.Response:
        if request.method == HTTPMethod.POST:
            title: str = request.data.get("title", None)
            g: GameInstance = self.get_object()
            if title in g.config.get("tasks"):
                GameEngine.resume(g).do('set-current-task',
                                        {"name": title})
                return response.Response(status=status.HTTP_200_OK)
            else:
                return response.Response(status=status.HTTP_400_BAD_REQUEST)
            
        if request.method == HTTPMethod.GET:
            g: GameInstance = self.get_object()
            title: str = GameEngine.resume(g).manager._current_state.current_task
            return response.Response({"current_task": title}, status=status.HTTP_200_OK)
        
        # I guess this is no need    
        return response.Response({"detail": f"Method `{request.method}` not allowed."},
                                 status=status.HTTP_400_BAD_REQUEST)
        
    @decorators.action(methods=[HTTPMethod.POST], detail=True)
    def estimate(self, request, *args, **kwargs) -> response.Response:
        estimate: str = request.data.get('estimate', None)
        title: str = self.kwargs.get('title', None)
        g: GameInstance = self.get_object()
        if estimate and title in g.config.get("tasks"):
            GameEngine.resume(g).do('add-user-estimate',
                                    {"username": self.request.user.username,
                                     "estimate": estimate})
            return response.Response(status=status.HTTP_200_OK)
        return response.Response(status=status.HTTP_418_IM_A_TEAPOT)
    
    
    @decorators.action(methods=[HTTPMethod.POST], detail=False)
    def avg(self, request, *args, **kwargs) -> response.Response:
        try:
            g: GameInstance = self.get_object()
            e: GameEngine = GameEngine.resume(g)
            task: str = e.manager._current_state.current_task
            e.do('calculate-current-task-estimate')
            return response.Response({"total": e.manager._current_state._instance.result_data.get(task, '-')})
        except Exception as exc:
            return response.Response(format_msg(str(exc)), 
                                     status=status.HTTP_500_INTERNAL_SERVER_ERROR)