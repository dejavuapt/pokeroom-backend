from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.core.teams.models import Team, Membership
from apps.core.teams.choices import MembershipRoleChoice


@receiver([post_save], sender = Team)
def update_memberships_roles(sender, 
                             instance,
                             created, 
                             **kwargs):
    
    if created:
        Membership.objects.create(user = instance.owner_id, 
                                  team = instance, 
                                  role = MembershipRoleChoice.OWNER)
        return
    
    try:
        old_team = Team.objects.select_for_update().get(pk = instance.pk)
        old_owner = old_team.owner_id
        new_owner = instance.owner_id
        
        if old_owner == new_owner:
            return
         
        memb = Membership.objects.filter(user = new_owner, 
                                  team = instance
                                  ).first()
        memb.role = MembershipRoleChoice.OWNER
        Membership.objects.filter(user = old_owner, 
                                  team = instance
                                  ).update(role = MembershipRoleChoice.DEFAULT)
    except Team.DoesNotExist:
        pass