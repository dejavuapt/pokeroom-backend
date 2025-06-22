from abc import abstractmethod, ABC
from .state_manager import StateManager
from typing import Optional, Any
from apps.games.models import GameState

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
    def context(self) -> StateManager:
        return self._context

    @context.setter
    def context(self, context: StateManager) -> None:
        self._context = context

    @abstractmethod
    def in_(self, context: Optional[dict[str, str]] = None) -> None:
        pass
    
    @abstractmethod
    def out_(self) -> Optional[dict[str,str]]:
        pass
    
    def avaliable_actions(self) -> dict[str, Any]:
        return {getattr(method, 'action_name'): method for _, method in self.__class__.__dict__.items() if getattr(method, 'is_action', False)}
    
