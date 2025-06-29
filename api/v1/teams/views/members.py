from api.v1.teams.serializers import TeamSreializer, MembershipSerializer
from api.v1.users.permissions import IsMembershipOwner, IsMembershipOwnerOrModerator
from apps.core.teams.choices import MembershipRoleChoice
from apps.core.teams.models import Team, Membership


from rest_framework import status, viewsets, response, permissions
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
 
User = get_user_model()
    
ROLE_MAPPING = {
    "member": 'D',
    "moderator": 'M',
    "owner": 'O'
}
    
class MembersViewset(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MembershipSerializer
    _is_need_serializer_team = False
    
    def get_serializer_class(self):
        if not self._is_need_serializer_team:
            return self.serializer_class
        else:
            return TeamSreializer
        
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] =  self.request.user
        return context
    
    def get_queryset(self):
        team_id = self.kwargs.get("id", None)
        return Membership.objects.filter(team = Team.objects.get(pk = team_id))
    
    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), user = self.request.user)
        # IDK why check not working. I'm just tired.
        # self.check_object_permissions(self.request, obj)
        if obj.role != MembershipRoleChoice.OWNER:
            self.permission_denied(self.request, code = status.HTTP_403_FORBIDDEN)
        return obj
    
    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'update':
            self.permission_classes.append(IsMembershipOwner)
        elif self.action == 'create':
            self.permission_classes.append(IsMembershipOwnerOrModerator)
        return super().get_permissions()
    

    
    def list(self, request, **kwargs):
        serializer = self.serializer_class(self.get_queryset(), many = True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request, **kwargs):
        username_to_add = request.data.get("username", None)
        if username_to_add is None:
            return response.Response({"error": "Username must be provided."}, status = status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(User, username = username_to_add)
        mm = self.get_queryset().filter(user = user)
        if mm.exists():
            return response.Response({"error": "Can't add someone who already exists in team."})
        
        membership = Team.objects.get(pk = kwargs.get("id", None)).add_member(user)
        if membership is not None:
            serializer = self.serializer_class(membership)
            return response.Response(serializer.data, status = status.HTTP_201_CREATED)
        
        return response.Response({"error": "fatal"}, status = status.HTTP_501_NOT_IMPLEMENTED)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance: Membership = self.get_object()
        is_valid, result = self._update_data_is_valid(request)
        if not is_valid:
            return response.Response({
                    "%s" % result.get("status"): "%s" % result.get("message")
                    }, status = status.HTTP_400_BAD_REQUEST)
        
        username = kwargs.get("pk", None)
        if username == request.user.username:
            return response.Response({"error": "Can't change yourself role."}, status = status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, username = username)
        user_membership = get_object_or_404(self.get_queryset(), user = user) #check if user in team's members
        
        another_user_serializer = self.get_serializer(user_membership, data = {'role': result.get("role")}, partial = partial)
        another_user_serializer.is_valid(raise_exception = True)
            
        if result.get("role") == MembershipRoleChoice.OWNER:
            current_team = Team.objects.get(pk = kwargs.get("id", None))
            
            # Temporary solved get another serializer...
            self._is_need_serializer_team = True
            team_serializer = self.get_serializer(current_team, data = {
                'owner_id': user.id
            }, partial = partial)
            team_serializer.is_valid(raise_exception = True)
            self._is_need_serializer_team = False
            
            current_user_serializer = self.get_serializer(instance, data = {
                'role': MembershipRoleChoice.DEFAULT
                }, partial = partial)
            current_user_serializer.is_valid(raise_exception = True)
            
            self.perform_update(current_user_serializer)
            self.perform_update(team_serializer)
            
        self.perform_update(another_user_serializer)
            
            
        return response.Response(another_user_serializer.data, status.HTTP_200_OK)
            
            
    def destroy(self, request, *args, **kwargs):
        instance: Membership = self.get_object()
        username = kwargs.get("pk", None)
        if username == request.user.username:
            return response.Response({"error": "You can't out of team while u r owner."},
                            status = status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, username = username)
        user_membership = get_object_or_404(self.get_queryset(), user = user)
        self.perform_destroy(user_membership)
        return response.Response(status = status.HTTP_204_NO_CONTENT)
            


    def _message_return(self, status, message):
        return {"status": status, "message": message}
    
    def _update_data_is_valid(self, request) -> tuple[bool, dict]:
        new_role = request.data.get('role', None)
        if new_role is None:
            return False, self._message_return("error", "Role must be provided.")
        if new_role not in ROLE_MAPPING:
            return False, self._message_return("error", "Invalid role provided")
        
        return True, {"role": ROLE_MAPPING.get(new_role)}
            
    def _get_team_by_user(self, pk, user) -> Team:
        queryset = Team.objects.filter(team_in__user = user).distinct()
        return get_object_or_404(queryset, pk = pk)
        