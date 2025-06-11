from typing import Any
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from api.v1.teams.permissions import IsOwner
from api.v1.teams.serializers import TeamSreializer, MembershipSerializer
from apps.core.teams.models import Team, Membership
from apps.core.teams.choices import MembershipRoleChoice
from djoser import views
from django.urls import reverse

UserModel = get_user_model()

class UserViewSet(views.UserViewSet):
    pass


class UserTeamViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamSreializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] =  self.request.user
        return context
    
    def retrieve(self, request, *args, **kwargs):
        primary_key = kwargs.get("pk", None)
        queryset = Team.objects.filter(team_in__user = request.user).distinct()
        team = get_object_or_404(queryset, 
                                 name = primary_key)
        return Response(self.serializer_class(team, context = {"user": request.user}).data)
    
    def get_queryset(self):
        user = self.request.user
        teams = Team.objects.filter(team_in__user = user).distinct()
        return teams
    
ROLE_MAPPING = {
    "member": 'D',
    "moderator": 'M'
}
    
class UserTeamMembersViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    
    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [IsAuthenticated]
        elif self.action == 'update' or self.action == 'partial_update':
            self.permission_classes = [IsAuthenticated, IsOwner]
        return super().get_permissions()
    
    def list(self, request, **kwargs):
        primary_key = kwargs.get("name", None)
        queryset = Team.objects.filter(team_in__user = request.user).distinct()
        team = get_object_or_404(queryset, name = primary_key)
        
        members = self.queryset.filter(team = team).distinct()
        serializer = self.serializer_class(members, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        primary_key = kwargs.get("name", None)
        queryset = Team.objects.filter(team_in__user = request.user).distinct()
        team = get_object_or_404(queryset, name = primary_key) 
        
        username = request.data.get('username', None)
        user = get_object_or_404(UserModel, username = username)
        new_role = request.data.get('role', None)
        
        if username is None or new_role is None:
            return Response({"error": "Username and role must be provided."}, status= status.HTTP_400_BAD_REQUEST)
        
        if new_role in ROLE_MAPPING:
            new_role = ROLE_MAPPING.get(new_role)
        else:
            return Response({"error": "Invalide role provided."}, status = status.HTTP_400_BAD_REQUEST)
        
        member = get_object_or_404(self.queryset, user = user, team = team)
        
        serializer = self.serializer_class(member, {"role": new_role}, partial = partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid operation."}, status = status.HTTP_400_BAD_REQUEST)
    
    # TODO: Queryset and team need to init in class, not in methods
        