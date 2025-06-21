import uuid
from django.db import models
from django.utils.translation import gettext as _
from django.utils import timezone
from django.contrib.auth import get_user_model

from .interfaces.invite_link import InviteLinkInterface
from .choices import MembershipRoleChoice

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
        through='Membership',
        through_fields=("team", "user"),
        verbose_name=_("Members")
    )
    
    class Meta:
        verbose_name = _("Team")
        verbose_name_plural = _("Teams")
        # you can use unique_together for now but keep in mind unique_together may be deprecated in the future as stated in Django docs.
        # unique_together = [['owned_by', 'name']]
        constraints = [
            models.UniqueConstraint(
                fields=['owner_id', 'name',], #teams.Team: (models.E012) 'constraints' refers to the nonexistent field 'Lower(F(name))'. BUG
                name="unique_lower_name_by_user",
                violation_error_message=_("That team with name is already exist.")
            ),
        ]

    def save(self, **kwargs):
        created: bool = self._state.adding
        super().save(**kwargs)
        if created:
            self._crt_ownership()
        
    def __str__(self):
        return self.name
    
    def _crt_ownership(self) -> None:
        Membership.objects.create(user = self.owner_id,
                                  team = self,
                                  role = MembershipRoleChoice.OWNER).save()
    
    def set_new_owner(self, new_owner):
        if not isinstance(new_owner, UserModel):
            raise ValueError("New owner must be a User.")
        
        self.owner_id = new_owner
        self.save()
            

    def add_member(self, user, role = MembershipRoleChoice.DEFAULT) -> 'Membership':
        if role is not MembershipRoleChoice.OWNER:
            tm = Membership.objects.create(team = self, user = user, role = role)
            tm.save()
            return tm
        return None
        
    def get_team_name(self) -> str:
        return getattr(self, 'name')
    
    # In case it's should work, bt idk | need to test that
    def get_owner_name(self) -> str:
        owner_attr: models.ForeignKey['AbstractUser'] = getattr(self, 'owner_id') # type: ignore
        return owner_attr.__str__()
    
    
class Membership(models.Model):
    
    user = models.ForeignKey(
        UserModel, 
        on_delete=models.CASCADE, 
        verbose_name=_("Member"), 
        related_name="member_in"
    )
    team = models.ForeignKey(
        Team, 
        on_delete=models.CASCADE, 
        verbose_name=_("Team"), 
        related_name="team_in"
    )
    role = models.CharField(_("Role"), 
                            max_length=1, 
                            choices=MembershipRoleChoice.choices, 
                            default=MembershipRoleChoice.DEFAULT
    )
    invited_at = models.DateTimeField(_("Invited date"), default=timezone.now)
    
    class Meta:
        verbose_name = _("Membership")
        verbose_name_plural = _("Memberships")
        constraints = [
            models.UniqueConstraint(
                fields=['team', 'user',],
                name="unique_membership",
                violation_error_message= _("Membership with that user and team is already exist.")
            )
        ]

    def __str__(self):
        return f"{self.user.get_username()} in {self.team.get_team_name()} is {self.get_role_display()}"

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