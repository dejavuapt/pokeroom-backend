from queue import Queue
from typing import TypeVar, Union, Optional, Any
import logging, importlib
import copy

from .state import State
from apps.games.models.models import GameState, GameInstance, GameInstanceStatusChoices
from apps.games.core.utils.types import JSONDict

logger = logging.getLogger(__name__)

State_T = TypeVar('State_T', bound="State")
GameState_T = TypeVar('GameState_T', bound="GameState")


# TODO: Idea: Move GameManager\Engine etc. into library. States of project should be in a project, not in a game logic.
class GameManager:
    """
    GameManager is a class to manipulate with game's states. 
    """
    _current_state: Optional[State_T] = None
    _states: list[tuple[State_T, GameState_T]] = []
    _config: Optional[JSONDict] = None
    _game_instance: Optional[GameInstance] = None
    
    def __init__(self, 
                 config: JSONDict,
                 instance: Optional[GameInstance] = None) -> None:
        self._game_instance = instance
        self._load(config)
        self.state_forward()
    
    def state_forward(self) -> Optional[State_T]:
        """
        `state_forward` method automaticly finished previous state and start next state. \n
        Initialize gamestate object from model. Get next state and excluded it from `sequence` list.
        """
        if not self._states:
            if self._current_state is not None:
                self._cancel()
            self._game_instance.status = GameInstanceStatusChoices.FINISED
            self._game_instance.save()
            return None
        
        if self._current_state is not None:
            self._cancel()
        else:
            self._game_instance.status = GameInstanceStatusChoices.STARTED
            self._game_instance.save()

        state_name, gamestate_name = self._states.pop(0) if self._states else (None, None)
        state = self._re_class("states", state_name)()
        gamestate = self._re_class("models", gamestate_name)
        logger.debug(f"Transition from {type(self._current_state).__name__} to {type(state).__name__}")
        
        self._current_state = state
        
        if gs:= gamestate.objects.filter(game=self._game_instance).first():
            self._current_state.instance = gs
        else:
            gs = gamestate.objects.create(
                game=self._game_instance,
                name=state.name,
            )
            gs.save()
            self._current_state.instance = gs
            
        self._current_state.context = self
        
        self._open()
        
        return self._current_state
    
    def handle_action(self, action: str, data: JSONDict) -> None:
        """
        Call action on a current state. Action means that method has decorator "state_action".\n
        Example: if method called like `do_something` with params (params1: str, params2: str, ...)
        then action is :str:`do-something` and data is `{"params1": Any, "params2": Any, ...}`
        """
        _avaliable_actions = self._current_state.avaliable_actions()
        if action in _avaliable_actions.keys():
            _avaliable_actions.get(action)(self._current_state, **data) 
    
    def _load(self, config: JSONDict) -> None:
        conf = copy.deepcopy(config)
        self._states = conf.pop("sequence") if conf.get("sequence", None) else None
        self._config = conf
        
    def _re_class(self, module: str, obj: str) -> Any:
        part_module: str = "%s.%s" % (self._config.get("settings").get("path"), 
                                      module)
        return getattr(importlib.import_module(part_module), obj)
    
    def _open(self) -> None:
        """
        Start current state. \n
        Call `in_` method to translate data in state from previous state.
        """
        logger.debug(f"Start state `{self._current_state.name}`, with config: {self._config}")
        self._current_state.in_(self._config.get("data", None))
    
    def _cancel(self) -> None:
        """
        Cancel current state. \n
        Call `out_` method in state and get output data to move it in another state.\n
        Update gameinstance's config
        """
        if self._current_state is not None:
            self._config.update({"data": self._current_state.out_()})
        self._update_instance_config()
        logger.debug(f"End state `{self._current_state.name}`, with config: {self._config}")
        
    def _update_instance_config(self) -> None:
        new_config: JSONDict = self._config
        new_config.update({"sequence": self._states})
        self._game_instance.update_config(new_config)
