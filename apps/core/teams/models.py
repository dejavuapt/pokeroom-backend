from django.db import models
from django.utils.translation import gettext as _
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid
import secrets
from datetime import timedelta, datetime
from pokeroom_backend import constants
from .choices import TeamMemberRoleChoice

UserModel = get_user_model()

class Team(models.Model):
    
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name"),max_length=50,)
    description = models.TextField(
        _("Description"),
        max_length=200,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(_("Created at"),default=timezone.now)
    owner_id = models.ForeignKey(
        UserModel,
        verbose_name=_("Team owner"),
        on_delete=models.CASCADE, # Maybe in future do different logic, when user delete a Team, if moderators exists at delete time, then owner stay a some moderator from current team
        related_name='teams'
    )
    members = models.ManyToManyField(
        UserModel,
        through='TeamMember',
        through_fields=("team_id", "user_id"),
        verbose_name=_("Members")
    )
    
    class Meta:
        verbose_name = _("Team")
        verbose_name_plural = _("Teams")
        # you can use unique_together for now but keep in mind unique_together may be deprecated in the future as stated in Django docs.
        # unique_together = [['owned_by', 'name']]
        constraints = [
            models.UniqueConstraint(
                # fields or expressions
                fields=['owner_id', 'name',], #teams.Team: (models.E012) 'constraints' refers to the nonexistent field 'Lower(F(name))'. BUG
                name="unique_lower_name_by_user",
                violation_error_message=_("That team with name is already exist.")
            ),
        ]

    def __str__(self):
        return "%s by %s" % (self.get_team_name(), ) 
    
    
    def get_team_name(self) -> str:
        return getattr(self, 'name')
    
    # In case it's should work, bt idk | need to test that
    def get_owner_name(self) -> str:
        owner_attr: models.ForeignKey['AbstractUser'] = getattr(self, 'owner_id') # type: ignore
        return owner_attr.__str__()
    
    
class TeamMember(models.Model):
    
    user_id = models.ForeignKey(
        UserModel, 
        on_delete=models.CASCADE, 
        verbose_name=_("Member"), 
        related_name="member_in"
    )
    team_id = models.ForeignKey(
        Team, 
        on_delete=models.CASCADE, 
        verbose_name=_("Team"), 
        related_name="team_in"
    )
    role = models.CharField(_("Role"), max_length=1, choices=TeamMemberRoleChoice)
    invited_at = models.DateTimeField(_("Invited date"), default=timezone.now)




# TODO: Move this method to upper. Because room need this interface too
# TODO: Write a logic to check all models with invitelinkinterface to drop a links that expires
# Abstract InviteLink Model
class InviteLinkInterface(models.Model):
    """ 
        Abstract model for storing invite links. \n
        Based on 16 bytes and default expires at 1 day (24h) from created (added in db) \n
        That class haven't `is_expires` field. If you need to check it: do attribute in your class or create logic.
    """
    # Lambda doesn't work in migrations:
    # Mb in future add factory of tokens
    _token_nbytes: int = constants.TOKEN_NBYTES     
    
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    token = models.CharField(
        _("Token"),
        max_length = 100,
        default = "%s" % (secrets.token_urlsafe(_token_nbytes)),
        editable=False
    )
    created_at = models.DateTimeField(
        _("Token created date"),
        default = timezone.now,
        editable=False
    )
    expires_at = models.DateTimeField(
        _("Token expires date"),
        default = timezone.now() + timedelta(days=1),
        editable=False
    )
    
    class Meta:
        abstract = True
        
    def __str__(self):
        return '%s expires at %s' % (self.get_token(), self.get_expires_date())
    
    def get_token(self) -> str:
        return getattr(self, 'token')
    
    def get_expires_date(self) -> datetime:
        return getattr(self, 'expires_at')    
    
    
    
    
    
class TeamInviteLink(InviteLinkInterface):
    
    team_id = models.OneToOneField(
        Team,
        on_delete=models.CASCADE,
        verbose_name=_("Team"),
        related_name="invite_link"
    )
    
    class Meta:
        verbose_name = _("Team invitelink")
        verbose_name_plural = _("Team invitelinks")