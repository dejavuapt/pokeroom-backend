
from apps.games.state import State
from apps.games.models import LobbyGameState
from apps.games.decorators import stage_action


class PokerLobbyState(State):
    _name = "Start lobby"
    
    def in_(self) -> None:
        self._instance.result_data.update({"tasks": []})
        return
    
    def out_(self) -> list[str]:
        self._instance.completed = True
        self._instance.save()
        return self.tasks
    
    @property
    def tasks(self) -> list[str]:
        return self._instance.result_data.get("tasks")    
    
    @stage_action
    def add_task(self, name: str) -> None:
        self._instance.result_data["tasks"].append(name)
        self._instance.save()
    
    

class EndLobbyState(State):
    pass