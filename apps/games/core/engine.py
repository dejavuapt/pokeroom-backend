from typing import Optional, Any, Union
from apps.games.models.models import GameInstance, GameTypesChoices
from apps.games.core.game_manager import GameManager
from apps.core.teams.models import Team

from django.contrib.auth import get_user_model, models

ErrorDict = dict[str, str]
NoneError = tuple[None, str]

User = get_user_model()

class GameEngine:
    _games_path: str = "apps.games"
    TYPES_MAPPING = {
        GameTypesChoices.POKER: "poker_planning",
        GameTypesChoices.RETRO: "retrospective"
    }
    
    
    _state_manager: Optional[GameManager] = None
    # def __init__(self, game_config: dict[str,Any]):
    
    
    def bootstrap(self, 
                  game_type: GameTypesChoices,
                  team: Union[Team, str],
                  init_user: Union[models.AbstractUser, str]
                  ) -> Union[GameInstance, NoneError]:
        if isinstance(team, str):
            try:
                team = Team.objects.get(pk = team)
            except Team.DoesNotExist as ex:
                return None, str(ex)
                
        if isinstance(init_user, str):
            try:
                init_user = User.objects.get(pk = init_user)
            except User.DoesNotExist as ex:
                return None, str(ex)
            
        config = self._get_config(game_type=game_type)
        
        self._game_instance = GameInstance.objects.create(team=team,
                                                          host_by=init_user,
                                                          config=config,
                                                          type=game_type)
        self._game_instance.save()
        
        self._state_manager = GameManager(config=self._get_config(game_type=game_type), 
                                          instance=self._game_instance)
        
        return self._game_instance
        
    def resume(self, 
               team: Union[Team, str]
               ) -> Optional[Union[GameInstance, NoneError]]:
        if isinstance(team, str):
            try:
                team = Team.objects.get(pk = team)
            except Team.DoesNotExist as ex:
                return None, str(ex)
            
        # i thk it doesn't work
        if gi := GameInstance.objects.filter(team = team).first():
            self._game_instance = gi
            self._state_manager = GameManager(
                config=gi.config,
                instance=self._game_instance
            )
        else:
            return None
            
        return gi
    
    # TODO: Надо упростить. Для каждой игры делать свою подпапку, настраивать конфиг приложения и в конфиг инстанса
    # нужно добавлять общий путь, который в менеджере будет брать данные
    def _get_config(self, game_type: GameTypesChoices) -> dict[str, Any]:
        if game_type == GameTypesChoices.POKER:
            return {
                "settings": {
                    "path": self._games_path,
                    "game": self.TYPES_MAPPING.get(game_type)
                },
                "sequence": [
                    ('PokerLobbyState', 'LobbyGameState'),
                    ('TasksEvaluationState', 'TaskEvaluationGameState')
                    ],
                "rule": ['1', '2', '3', '5', '8', 'c', 'l']
            }
        
        if game_type == GameTypesChoices.RETRO:
            pass
        
        raise ValueError(f"Unknown game type: {game_type}")
