from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from apps.core.teams.models import Team
from apps.core.rooms.choices import *
from django.utils import timezone
import uuid

UserModel = get_user_model()



class Room(models.Model):
    
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    status = models.CharField(_("Room's stats"), max_length=1, choices=RoomStatuses.choices)
    team_id = models.ForeignKey(
        Team,
        verbose_name=_("Team's room"),
        on_delete=models.CASCADE,
        related_name='rooms'
    )
    created_by = models.ForeignKey(
        UserModel,
        verbose_name=_("Created by"),
        on_delete=models.CASCADE,
        related_name='created_rooms'
    )
    created_at = models.DateTimeField(
        _("Created at"),
        default=timezone.now,
        editable=False
    )
    started_at = models.DateTimeField(_("Started at"), null=True, blank=True,)
    finished_at = models.DateTimeField(_("Finished at"), null=True, blank=True,)
    target_game = models.CharField(_("Target game strategy"), max_length=1, choices=Strategies.choices)
    # target_game_id = models.ForeignKey() # TODO: Нужно как-то с этим проработать
    video_call_link = models.CharField(_("Video call link"), max_length=200, null=True, blank=True,)
    
    class Meta:
        verbose_name = _("Room")
        verbose_name_plural = _("Rooms")
    

class RoomsMembers(models.Model):
    room_id = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        verbose_name=_("Room"),
        related_name='room_members'
    )
    user_id = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        related_name='member_rooms'
    )
    guest_token = models.CharField(_("Guest token"), max_length=200, null=True, blank=True, )
    role = models.CharField(_("Role"), max_length=1, choices=RoomMembersRole.choices)