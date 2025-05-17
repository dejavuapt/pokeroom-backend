from rest_framework import permissions
from apps.core.teams.choices import TeamMemberRoleChoice

class CurrentUserIsModeratorOrOwnerOrAdmin(permissions.IsAuthenticated):
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        user_is_owner_or_moderator = user.member_in.filter(team_id= obj, 
                                                           role__in=[TeamMemberRoleChoice.OWNER, 
                                                                     TeamMemberRoleChoice.MODERATOR]).exists()
        return user.is_staff or user_is_owner_or_moderator
    
class CurrentUserIsOwnerOrAdmin(permissions.IsAuthenticated):
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        user_is_owner = obj.owner_id == user
        return user_is_owner or user.is_staff