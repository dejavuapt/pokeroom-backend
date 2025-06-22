from typing import Optional, Any
from .state_manager import StateManager
from .poker_planning.task_evaluation import TasksEvaluationState
from apps.game.common.lobbies import StartLobbyState, EndLobbyState
from apps.game.models import GameInstance, GameTypesChoices, TaskEvaluationGameState

class GameEngine:
    
    _state_manager: Optional[StateManager] = None
    _game_instance: Optional[GameInstance] = None
    # def __init__(self, game_config: dict[str,Any]):
    
    def bootstrap(self, game_instance: GameInstance) -> None:
        self._game_instance = game_instance
        
        game_type = game_instance.type
        self._state_manager = StateManager(config=self._get_config(game_type=game_type))
        
        if game_instance.config:
            self._state_manager.load(game_instance.config)
    
    def _get_config(self, game_type: GameTypesChoices) -> dict[str, Any]:
        if game_type == GameTypesChoices.POKER:
            return {
                "sequence": [
                    (StartLobbyState, None),
                    (TasksEvaluationState, TaskEvaluationGameState)
                    (EndLobbyState, None)
                    ],
            }
        
        if game_type == GameTypesChoices.RETRO:
            pass
        
        raise ValueError(f"Unknown game type: {game_type}")
 