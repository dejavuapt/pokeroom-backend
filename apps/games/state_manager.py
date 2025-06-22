from queue import Queue
from typing import TypeVar, Union, Optional, Any
import logging

from .state import State
from apps.games.models import GameState, GameInstance

logger = logging.getLogger(__name__)

State_T = TypeVar('State_T', bound="State")
GameState_T = TypeVar('GameState_T', bound="GameState")

class StateManager:    
    _current_state: Optional[State_T] = None
    _states: list[tuple[State_T, GameState_T]] = []
    _config: Optional[dict[str, Any]] = None
    _game_instance: Optional[GameInstance] = None
    
    def __init__(self, 
                 config: dict[str, Any], 
                 instance: Optional[GameInstance] = None) -> None:
        self._game_instance = instance
        self.load(config)
        
    def load(self, config: dict[str, Any]) -> None:
        self._states = config.pop("sequence") if config.get("sequence", None) else None
        self.next()
        self._config = config
    
    def get_current_config(self) -> dict[str, Any]:
        return {
            "sequence": self._states,
            "data": self._current_state.instance.result_data
        }
    
    def next(self) -> Optional[State_T]:
        if self._current_state is not None:
            self.finish_state()
        
        state, gamestate = self._states.pop(0) if self._states else (None, None)
        
        logger.debug(f"Transition from {type(self._current_state).__name__} to {type(state).__name__}")
        
        gs = gamestate.objects.create(
            game=self._game_instance,
            name=state.name,
        )
        gs.save()
        
        self._current_state = state
        self._current_state.instance = gs
        self._current_state.context = self
        
        self.start_state()
        
        return self._current_state
    
    def start_state(self) -> None:
        logger.debug(f"Start state `{self._current_state.name}`, with config: {self._config}")
        self._current_state.in_(self._config.get("data", None))
        
    #action like "add-user-estimate"
    def handle_action(self, action: str, data: dict[str,Any]) -> None:
        _avaliable_actions = self._available_current_actions()
        if action in _avaliable_actions.keys():
            _avaliable_actions.get(action)(self._current_state)(*data) # Оень запутано, нужно проверять
    
    def finish_state(self) -> None:
        if self._current_state is not None:
            self._config.update({"data": self._current_state.out_})
            
        logger.debug(f"End state `{self._current_state.name}`, with config: {self._config}")
        
        
    def _available_current_actions(self) -> dict[str, Any]:
        return self._current_state.avaliable_actions()
        # logger.debug(f"Avaliable actions in that stage: {self._available_actions}")
