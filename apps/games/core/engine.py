from typing import Optional, Any
from .state_manager import StateManager
from apps.games.poker_planning.task_evaluation import TasksEvaluationState
from apps.games.common.lobbies import EndLobbyState, PokerLobbyState
from apps.games.models import GameInstance, GameTypesChoices, TaskEvaluationGameState, LobbyGameState

class GameEngine:
    
    _state_manager: Optional[StateManager] = None
    # def __init__(self, game_config: dict[str,Any]):
    
    
    def bootstrap(self, game_type: GameTypesChoices) -> StateManager:
        config = self._get_config(game_type=game_type)
        
        self._game_instance = GameInstance.objects.create(
            config=config,
            type=game_type
        )
        self._game_instance.save()
        
        self._state_manager = StateManager(
            config=self._get_config(game_type=game_type), 
            instance=self._game_instance
            )
        
        return self._state_manager
        
            
    def resume(self): 
        pass
    
    def _get_config(self, game_type: GameTypesChoices) -> dict[str, Any]:
        if game_type == GameTypesChoices.POKER:
            return {
                "sequence": [
                    (PokerLobbyState(), LobbyGameState),
                    (TasksEvaluationState(), TaskEvaluationGameState)
                    ],
            }
        
        if game_type == GameTypesChoices.RETRO:
            pass
        
        raise ValueError(f"Unknown game type: {game_type}")
 