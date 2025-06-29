from django.db import models
from django.utils.translation import gettext as _
from django.utils import timezone
from apps.core.teams.models import Team
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model
from apps.games.core.utils.types import JSONDict

User = get_user_model()

import uuid

class GameTypesChoices(models.TextChoices):
    POKER = 'P', _("PlanningPoker")
    RETRO = 'R', _("Retrospective")
    
class GameInstanceStatusChoices(models.TextChoices):
    OPEN = 'O', _("Opened")
    STARTED = 'S', _("Started")
    FINISED = 'F', _("Finisehd")
    CLOSED = 'C', _("Closed")
    
class GameRoleChoices(models.TextChoices):
    FACILITATOR = 'F', _("Facilitator")
    PLAYER = 'P', _("Player")

class GameInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="game")
    host_by = models.ForeignKey(User,
                                verbose_name=_("Hoted by"),
                                on_delete=models.CASCADE,
                                related_name='hosted_games')
    type = models.CharField(_("Game type"),
                            max_length=1, 
                            choices=GameTypesChoices.choices)
    status = models.CharField(_("Game status"), 
                              max_length=1,
                              choices=GameInstanceStatusChoices.choices,
                              default=GameInstanceStatusChoices.OPEN)
    config = models.JSONField(_("Config data"), default=dict)
    created_at = models.DateTimeField(_("Created at"), default=timezone.now)
    
    def save(self, **kwargs):
        created: bool = self._state.adding
        super().save(**kwargs)
        if created:
            faci = Player.objects.create(game=self,
                                         user=self.host_by,
                                         role=GameRoleChoices.FACILITATOR)
            faci.save()
    
    def set_facilitator(self, user) -> None:
        if self.players.filter(user = user).exists():
            self.players.filter(role = GameRoleChoices.FACILITATOR).update(role = GameRoleChoices.PLAYER)
            self.players.filter(user = user).update(role = GameRoleChoices.FACILITATOR)
    
    def update_config(self, new_config: JSONDict) -> None:
        self.config = new_config
        self.save()
            
    
class Player(models.Model):
    user = models.ForeignKey(User, 
                             on_delete=models.CASCADE, 
                             verbose_name=_("Player"), 
                             related_name="games")
    game = models.ForeignKey(GameInstance, 
                             on_delete=models.CASCADE, 
                             verbose_name=_("Game"), 
                             related_name="players")
    role = models.CharField(_("Player role"), 
                            max_length=1, 
                            choices=GameRoleChoices.choices, 
                            default=GameRoleChoices.PLAYER)
    
    class Meta:
        verbose_name = _("Player")
        verbose_name_plural = _("Players")
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'game',],
                name="unique_game_players",
                violation_error_message= _("Unique player in that game already exist")
            )
        ]
    
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