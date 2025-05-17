from rest_framework import permissions
from apps.core.teams.choices import TeamMemberRoleChoice

class IsOwnerOrModerator(permissions.IsAuthenticated):
    
    def has_object_permission(self, request, view, obj):
        return request.user.member_in.filter(team_id= obj,
                                             role__in=[TeamMemberRoleChoice.OWNER, 
                                                       TeamMemberRoleChoice.MODERATOR]).exists()
    
class IsOwner(permissions.IsAuthenticated):
    
    def has_object_permission(self, request, view, obj):
        return obj.owner_id == request.user