from __future__ import annotations
from typing import Optional, Any, Union, Final
from apps.games.models.models import GameInstance, GameTypesChoices, GameInstanceStatusChoices
from apps.games.core.game_manager import GameManager
from apps.games.core.utils.types import JSONDict

from django.contrib.auth import get_user_model, models


User = get_user_model()

class GameEngine:
    _games_path: Final[str] = "apps.games"
    TYPES_MAPPING: Final[dict[str, str]] = {
        GameTypesChoices.POKER: "poker_planning",
        GameTypesChoices.RETRO: "retrospective"
    }
    
    _manager: Optional[GameManager] = None
    _instance: Optional[GameInstance] = None        
    
    @property
    def game_instance(self) -> Optional[GameInstance]:
        return self._instance
    
    @property
    def manager(self) -> Optional[GameManager]:
        return self._manager
    
    @classmethod
    def build(cls, 
              game_type: Optional[GameTypesChoices] = None,
              init_user: Optional[Union[models.AbstractUser, str]] = None,
              *,
              props: Optional[JSONDict] = None) -> GameEngine:
        """
        Build method allows to create a GameInstance and GameManager. 
        """
        if isinstance(init_user, str):
            try:
                init_user = User.objects.get(pk = init_user)
            except User.DoesNotExist as ex:
                return None, str(ex)
            
        slf: GameEngine = cls()

        config: JSONDict = slf._setup_config(game_type, props)
        slf._instance = slf._init_instance(init_user, config, game_type)
        slf._manager = slf._init_manager(config)
        
        return slf
    
    @classmethod
    def resume(cls, instance: GameInstance) -> GameEngine:
        slf: GameEngine = cls()
        slf._instance = instance
        slf._manager = GameManager(config=slf._instance.config, instance=slf._instance)
        return slf
    
    def do(self, action: str, data: Optional[JSONDict] = None) -> GameEngine:
        if self._manager.handle_action(action, data if data else {}):
            return self
        raise ValueError(f"Method {action} doesn't exist.")
    
    def forward(self) -> GameEngine:
        ## TODO: Need to check if that was last method to close instance, and you cannot resume game that finished
        self._manager.state_forward()
        return self
    
    def _init_instance(self, host: models.AbstractUser, 
                            config: JSONDict, game_type: GameTypesChoices) -> GameInstance:
        gi = GameInstance.objects.create(host_by=host, 
                                         config=config, 
                                         type=game_type, 
                                         status=GameInstanceStatusChoices.STARTED)
        gi.save()
        return gi
    
    def _init_manager(self, config: JSONDict) -> GameManager:
        gm: GameManager = GameManager(config, self._instance)
        return gm
    
    def _setup_config(self, game_type: GameTypesChoices, 
                      props: JSONDict | None = None) -> JSONDict:
        if game_type == GameTypesChoices.POKER:
            config: JSONDict = {
                "settings": {
                    "path": self._games_path,
                    "game": self.TYPES_MAPPING.get(game_type)
                },
                "sequence": [
                    ('PokerLobbyState', 'LobbyGameState'),
                    ('TasksEvaluationState', 'TaskEvaluationGameState'),
                    ('PokerLobbyEndState', 'LobbyGameState')
                    ],
                "rule": '1,2,3,4,5,6,7,-'
            }
            if props:
                config.update(props)
            return config
        
        
        raise ValueError(f"Unknown game type: {game_type}")
