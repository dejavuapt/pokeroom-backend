
from apps.games.core.state import State
from apps.games.models import LobbyGameState
from apps.games.core.utils.decorators import stage_action
from apps.games.core.utils.types import JSONDict


    
    # def to_json(self) -> JSONDict:
    #     return {"name": self._name,
    #             "instance_id": self._instance.id }
    

class EndLobbyState(State):
    pass