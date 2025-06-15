from typing import Any
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from api.v1.users.permissions import IsMembershipOwner, IsMembershipOwnerOrModerator
from api.v1.users.serializers import UserSerializer
from api.v1.teams.serializers import TeamSreializer, MembershipSerializer
from apps.core.teams.models import Team, Membership
from apps.core.teams.choices import MembershipRoleChoice
from djoser import views
from django.urls import reverse

import logging
logger = logging.getLogger('api')

UserModel = get_user_model()

class PokeroomUserViewSet(views.UserViewSet):
    serializer_class = UserSerializer
    
    def create(self, request, *args, **kwargs):
        logger.debug(f"{request.data}")
        return super().create(request, *args, **kwargs)


class UserTeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSreializer
    
    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            self.permission_classes = [IsAuthenticated]
        elif self.action == 'update' or self.action == 'create':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] =  self.request.user
        return context
    
    def get_queryset(self):
        user = self.request.user
        teams = Team.objects.filter(team_in__user = user).distinct()
        return teams
    
    def retrieve(self, request, *args, **kwargs):
        primary_key = kwargs.get("pk", None)
        queryset = Team.objects.filter(team_in__user = request.user).distinct()
        team = get_object_or_404(queryset, 
                                 pk = primary_key)
        return Response(self.serializer_class(team, context = {"user": request.user}).data)
    
    
    
ROLE_MAPPING = {
    "member": 'D',
    "moderator": 'M',
    "owner": 'O'
}
    
class UserTeamMembersViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MembershipSerializer
    serializer_team = False
    # --- PUBLIC ---
    
    ## --- CLASS METHODS ---
    
    def get_serializer_class(self):
        if not self.serializer_team:
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
            self.permission_classes = [IsAuthenticated]
        elif self.action == 'update':
            self.permission_classes.append(IsMembershipOwner)
        elif self.action == 'create':
            self.permission_classes.append(IsMembershipOwnerOrModerator)
        return super().get_permissions()
    
    ## --- HTTP METHODS ----
    
    def list(self, request, **kwargs):
        serializer = self.serializer_class(self.get_queryset(), many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request, **kwargs):
        username_to_add = request.data.get("username", None)
        if username_to_add is None:
            return Response({"error": "Username must be provided."}, status = status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(UserModel, username = username_to_add)
        mm = self.get_queryset().filter(user = user)
        if mm.exists():
            return Response({"error": "Can't add someone who already exists in team."})
        
        membership = Team.objects.get(pk = kwargs.get("id", None)).add_member(user)
        if membership is not None:
            serializer = self.serializer_class(membership)
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        
        return Response({"error": "fatal"}, status = status.HTTP_501_NOT_IMPLEMENTED)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance: Membership = self.get_object()
        is_valid, result = self._update_data_is_valid(request)
        if not is_valid:
            return Response({
                    "%s" % result.get("status"): "%s" % result.get("message")
                    }, status = status.HTTP_400_BAD_REQUEST)
        
        username = kwargs.get("pk", None)
        if username == request.user.username:
            return Response({"error": "Can't change yourself role."}, status = status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(UserModel, username = username)
        user_membership = get_object_or_404(self.get_queryset(), user = user) #check if user in team's members
        
        another_user_serializer = self.get_serializer(user_membership, data = {'role': result.get("role")}, partial = partial)
        another_user_serializer.is_valid(raise_exception = True)
            
        if result.get("role") == MembershipRoleChoice.OWNER:
            current_team = Team.objects.get(pk = kwargs.get("id", None))
            
            # Temporary solved get another serializer...
            self.serializer_team = True
            team_serializer = self.get_serializer(current_team, data = {
                'owner_id': user.id
            }, partial = partial)
            team_serializer.is_valid(raise_exception = True)
            self.serializer_team = False
            
            current_user_serializer = self.get_serializer(instance, data = {
                'role': MembershipRoleChoice.DEFAULT
                }, partial = partial)
            current_user_serializer.is_valid(raise_exception = True)
            
            self.perform_update(current_user_serializer)
            self.perform_update(team_serializer)
            
        self.perform_update(another_user_serializer)
            
            
        return Response(another_user_serializer.data, status.HTTP_200_OK)
            
            
    def destroy(self, request, *args, **kwargs):
        instance: Membership = self.get_object()
        username = kwargs.get("pk", None)
        if username == request.user.username:
            return Response({"error": "You can't out of team while u r owner."},
                            status = status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(UserModel, username = username)
        user_membership = get_object_or_404(self.get_queryset(), user = user)
        self.perform_destroy(user_membership)
        return Response(status = status.HTTP_204_NO_CONTENT)
            

    # --- PRIVATE ---

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
        