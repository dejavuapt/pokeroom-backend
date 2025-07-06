from apps.games.models.models import GameInstance, GameState, GameTypesChoices, GameRoleChoices
from apps.games.models.poker_planning import TaskEvaluationGameState, LobbyGameState
from apps.games.core.engine import GameEngine
from api.v1.games.serializers import *

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
        poker_id = self.kwargs.get("id", None)
        return GameInstance.objects.filter(pk=poker_id)
    
    def create(self, request, *args, **kwargs):
        # TODO: add support rules {"rule": [1,2,3,4,5]}
        try:
            eng = GameEngine().bootstrap_or_resume(game_type=GameTypesChoices.POKER,
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
    def get_queryset(self):
        poker_id = self.kwargs.get("id", None)
        return GameInstance.objects.filter(pk=poker_id)
    
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
        
        if request.method == HTTPMethod.POST:
            task_label: str = request.data.get("task", None)
            gi: Optional[GameInstance] = self.get_object()
            if task_label and gi:
                GameEngine().resume_by_gi(gi).do('set-current-task', 
                                                 {"name": task_label})
                return response.Response({"detail": f"Success set current task with title {task_label}."},
                                         status=status.HTTP_200_OK)
            return response.Response({"detail": "Not provided title of task or game not started"},
                                     status=status.HTTP_400_BAD_REQUEST)
        
        if request.method == HTTPMethod.GET:
           if gi:= self.get_queryset().first():
               current_task = GameEngine().resume_by_gi(gi)._game_manager._current_state.current_task
               return response.Response({"current_task": current_task},
                                        status=status.HTTP_200_OK)
            
        return response.Response(status=status.HTTP_501_NOT_IMPLEMENTED)
            

    # 12Q345qwe
    @decorators.action(methods=[HTTPMethod.GET, HTTPMethod.POST], 
                       detail=False)
    def estimate(self, request, *args, **kwargs) -> response.Response:

        if request.method == HTTPMethod.GET:
            try: 
                if gi := self.get_object():
                    ge = GameEngine().resume_by_gi(gi).do('calculate-current-task-estimate')
                    cs = ge._game_manager._current_state._instance.current_task
                    res = ge._game_manager._current_state._instance.result_data.get(cs, '-')
                return response.Response({"current_task_estimate": res},
                                         status=status.HTTP_202_ACCEPTED)
            except Exception as exc:
                return response.Response({"detail": str(exc)},
                                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if request.method == HTTPMethod.POST:
            user_estimate: str = request.data.get("estimate", None)
            gi = self.get_queryset().first()
            if user_estimate and gi:
                current_user = self.request.user
                GameEngine().resume_by_gi(gi).do('add-user-estimate',
                                                 {"username": current_user.username, 
                                                  "estimate": user_estimate})
                return response.Response(status=status.HTTP_202_ACCEPTED)
        
        return response.Response(status=status.HTTP_501_NOT_IMPLEMENTED)
    
    