from rest_framework import permissions
from apps.core.teams.choices import MembershipRoleChoice

# TODO: Need to rewrite for membership
# class IsOwnerOrModeratorMembership(permissions.IsAuthenticated):
    
#     def has_object_permission(self, request, view, obj):
#         return request.user.member_in.filter(team_id= obj,
#                                              role__in=[MembershipRoleChoice.OWNER, 
#                                                        MembershipRoleChoice.MODERATOR]).exists()
import logging
logger = logging.getLogger('api')

class IsMembershipOwner(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        logger.warning(obj)
        return obj.user == request.user and obj.role == MembershipRoleChoice.OWNER
    
class IsMembershipOwnerOrModerator(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user and obj.role in [MembershipRoleChoice.OWNER, MembershipRoleChoice.MODERATOR]