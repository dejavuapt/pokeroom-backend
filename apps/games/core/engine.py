from typing import Optional, Any, Union, Final
from apps.games.models.models import GameInstance, GameTypesChoices, GameInstanceStatusChoices
from apps.games.core.game_manager import GameManager
from apps.games.core.utils.types import JSONDict
from apps.core.teams.models import Team

from django.contrib.auth import get_user_model, models

ErrorDict = dict[str, str]
NoneError = tuple[None, str]

User = get_user_model()

class GameEngine:
    _games_path: Final[str] = "apps.games"
    TYPES_MAPPING: Final[dict[str, str]] = {
        GameTypesChoices.POKER: "poker_planning",
        GameTypesChoices.RETRO: "retrospective"
    }
    
    _game_manager: Optional[GameManager] = None
    _game_instance: Optional[GameInstance] = None
    
    def bootstrap_or_resume(self, 
                            team: Union[Team, str],
                            game_type: Optional[GameTypesChoices] = None,
                            init_user: Optional[Union[models.AbstractUser, str]] = None
                  ) -> Union['GameEngine', NoneError]:
        if isinstance(team, str):
            try:
                team = Team.objects.get(pk = team)
            except Team.DoesNotExist as ex:
                return None, str(ex)
        
        if game_type is None or init_user is None:
            try:
                gi = GameInstance.objects.get(team = team)
                if gi.status != GameInstanceStatusChoices.CLOSED:
                    self._game_instance = gi
                    self._game_manager = GameManager(config=gi.config,
                                                     instance=gi)
                    return gi
                return None, "Game is closed"
            except GameInstance.DoesNotExist as ex:
                return None, str(ex)
        
        if isinstance(init_user, str):
            try:
                init_user = User.objects.get(pk = init_user)
            except User.DoesNotExist as ex:
                return None, str(ex)

        if GameInstance.objects.filter(team=team).exists():
            raise ValueError("Game already started")

        self._game_instance = GameInstance.objects.create(team=team,
                                                          host_by=init_user,
                                                          config=self._get_config(game_type=game_type),
                                                          type=game_type,
                                                          status=GameInstanceStatusChoices.STARTED)
        self._game_instance.save()
        
        self._game_manager = GameManager(config=self._get_config(game_type=game_type), 
                                         instance=self._game_instance)
        
        return self
    
    def resume_by_gi(self, instance: GameInstance) -> 'GameEngine':
        self._game_instance = instance
        self._game_manager = GameManager(config=self._game_instance.config,
                                         instance=self._game_instance)
        return self
    
    def do(self, action: str, data: Optional[JSONDict] = None) -> Optional[Union['GameEngine', NoneError]]:
        if self._game_manager.handle_action(action, data if data else {}):
            return self
        raise ValueError("That method doesn't exist.")
    
    def _get_config(self, game_type: GameTypesChoices) -> dict[str, Any]:
        if game_type == GameTypesChoices.POKER:
            return {
                "settings": {
                    "path": self._games_path,
                    "game": self.TYPES_MAPPING.get(game_type)
                },
                "sequence": [
                    ('PokerLobbyState', 'LobbyGameState'),
                    ('TasksEvaluationState', 'TaskEvaluationGameState'),
                    ('PokerLobbyEndState', 'LobbyGameState')
                    ],
                "rule": ['1', '2', '3', '5', '8', 'c', 'l']
            }
        
        if game_type == GameTypesChoices.RETRO:
            pass
        
        raise ValueError(f"Unknown game type: {game_type}")
