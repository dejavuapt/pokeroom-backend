import inspect

from abc import abstractmethod, ABC
from typing import Optional, Any
from apps.games.models.models import GameState
from apps.games.core.utils.types import JSONDict


class State(ABC):
    
    @property
    def instance(self) -> Optional[GameState]:
        return self._instance
    
    @instance.setter
    def instance(self, instance: Optional[GameState] = None) -> None:
        self._instance = instance
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, state_name: str) -> None:
        self._name = state_name
    
    @property
    def context(self) -> 'StateManager':
        return self._context

    @context.setter
    def context(self, context: 'StateManager') -> None:
        self._context = context

    @abstractmethod
    def in_(self, context: Optional[dict[str, str]] = None) -> None:
        pass
    
    @abstractmethod
    def out_(self) -> Optional[dict[str,str]]:
        pass
    
    def to_json(self) -> JSONDict:
        return {"name": self._name,
                "instance": self._instance}    
    
    def from_json(self, name, game_state, context):
        self._name = name
        self._instance = game_state,
        self._context = context
        
    @classmethod
    def avaliable_actions(cls) -> dict[str, Any]:
        return { getattr(method, 'action_name', 'n'): method 
                for name, method in inspect.getmembers(cls, predicate=inspect.isfunction) if getattr(method, 'is_action', False)}
    
