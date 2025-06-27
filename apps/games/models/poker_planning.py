from apps.games.models.models import GameState
from django.db import models
from django.utils.translation import gettext as _
from django.contrib.postgres.fields import ArrayField


class TaskEvaluationGameState(GameState):
    tasks = ArrayField(models.CharField(), default=list, blank=True)
    current_task = models.CharField(_("Current task"), null=True, blank=True)
    players_votes = models.JSONField(_("Players votes"), default=dict)
    
    def init_tasks(self, tasks: list[str] = None):
        self.tasks = tasks
        self.save()
    
    def is_all_voted(self, players_names: list[str]):
        return set(self.players_votes.keys()) >= set(players_names)
    
    def submit_vote(self, username: str, value: int):
        self.players_votes.update({username: value})
        self.save()
    
    def reveal_results(self):
        self.completed = True
        self.reset()
        return self.result_data
    
    def reset(self):
        self.current_task = None
        self.players_votes = {}
        self.save()
        
        
class LobbyGameState(GameState):
    pass