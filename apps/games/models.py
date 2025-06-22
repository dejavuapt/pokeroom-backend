from django.db import models
from django.utils.translation import gettext as _
from django.utils import timezone
from apps.core.teams.models import Team
from django.contrib.postgres.fields import ArrayField

import uuid

class GameTypesChoices(models.TextChoices):
    POKER = 'P', _("PlanningPoker")
    RETRO = 'R', _("Retrospective")

class GameInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # team = models.ForeignKey(Team, on_delete=models.CASCADE)
    config = models.JSONField(_("Config data"))
    created_at = models.DateTimeField(_("Created at"), default=timezone.now)
    type = models.CharField(_("Game type"),
                            max_length=1, 
                            choices=GameTypesChoices.choices
                            )
    
class GameState(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(GameInstance, on_delete=models.CASCADE)
    name = models.CharField(_("Stage name"), max_length=100)
    completed = models.BooleanField(_("Is completed stage"), default=False)
    result_data = models.JSONField(_("Result data"), default=dict)
    
    class Meta:
        abstract = True
    
    def update_result(self, data: dict) -> None:
        self.result_data.update(data)
        self.save()
        
        
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