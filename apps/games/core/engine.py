from typing import Optional, Any, Union
from .state_manager import StateManager
# from apps.games.poker_planning.task_evaluation import TasksEvaluationState
# from apps.games.common.lobbies import EndLobbyState, PokerLobbyState
from apps.games.models import GameInstance, GameTypesChoices, TaskEvaluationGameState, LobbyGameState

from apps.core.teams.models import Team

from django.contrib.auth import get_user_model, models

ErrorDict = dict[str, str]

User = get_user_model()

class GameEngine:
    
    _state_manager: Optional[StateManager] = None
    # def __init__(self, game_config: dict[str,Any]):
    
    
    def bootstrap(self, 
                  game_type: GameTypesChoices,
                  team: Union[Team, str],
                  init_user: Union[models.AbstractUser, str]
                  ) -> Union[GameInstance, ErrorDict]:
        if isinstance(team, str):
            try:
                team = Team.objects.get(pk = team)
            except Team.DoesNotExist as exc:
                return {"message": str(exc)}
                
        if isinstance(init_user, str):
            try:
                init_user = User.objects.get(pk = init_user)
            except User.DoesNotExist as exc:
                return {"message": str (exc)}
            
        config = self._get_config(game_type=game_type)
        
        self._game_instance = GameInstance.objects.create(
            team=team,
            host_by=init_user,
            config=config,
            type=game_type
        )
        self._game_instance.save()
        
        self._state_manager = StateManager(
            config=self._get_config(game_type=game_type), 
            instance=self._game_instance
            )
        
        return self._game_instance
        
    def resume(self):
        pass
    
    # TODO: Надо упростить. Для каждой игры делать свою подпапку, настраивать конфиг приложения и в конфиг инстанса
    # нужно добавлять общий путь, который в менеджере будет брать данные
    def _get_config(self, game_type: GameTypesChoices) -> dict[str, Any]:
        if game_type == GameTypesChoices.POKER:
            return {
                "sequence": [
                    ('apps.games.poker_planning.task_evaluation.PokerLobbyState', 
                     'apps.games.models.LobbyGameState'),
                    ('apps.games.poker_planning.task_evaluation.TasksEvaluationState', 
                     'apps.games.models.TaskEvaluationGameState')
                    ],
                "rule": ['1', '2', '3', '5', '8', 'c', 'l']
            }
        
        if game_type == GameTypesChoices.RETRO:
            pass
        
        raise ValueError(f"Unknown game type: {game_type}")
 