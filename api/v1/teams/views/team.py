from api.v1.teams.serializers import TeamSreializer, InviteLinkSerializer, MembershipSerializer
from apps.core.teams.models import Team, TeamInviteLink

from rest_framework import status, viewsets, response, permissions, decorators
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from http import HTTPMethod as methods

from typing import Optional, Any

User = get_user_model()

class TeamViewset(viewsets.ModelViewSet):
    serializer_class = TeamSreializer
    
    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'update' or self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] =  self.request.user
        return context
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def get_queryset(self):
        user = self.request.user
        teams = Team.objects.filter(team_in__user = user).distinct()
        return teams
    
    def retrieve(self, request, *args, **kwargs):
        primary_key = kwargs.get("pk", None)
        queryset = Team.objects.filter(team_in__user = request.user).distinct()
        team = get_object_or_404(queryset, 
                                 pk = primary_key)
        return response.Response(self.serializer_class(team, context = {"user": request.user}).data)
    
    # Request: {"token": "..."}
    @decorators.action(methods=[methods.POST], detail=False)
    def join(self, request, *args, **kwargs):
        token = request.data.get("token", None)
        if token is None:
            return response.Response(status=status.HTTP_400_BAD_REQUEST, data={"Token hasn't provided"}) # TODO: Do looks greate
        
        token_model: TeamInviteLink = get_object_or_404(TeamInviteLink.objects.all(), token=token)
        team_by_token: Team = get_object_or_404(Team.objects.all(), invite_link=token_model)
        # TODO: Что если пользователь уже добавлен в команду -> можно делать проверку на уровне пермишиннов, либо простой респонс на то что "йоу ты есть тут"
        # TODO: Что если токен невалидный, когда и как получать новый?
        team_by_token.add_member(self.request.user)
        return response.Response(
            self.serializer_class(team_by_token).data,
            status=status.HTTP_200_OK
        )
        
   
   
class InvitelinkViewset(viewsets.GenericViewSet):
    serializer_class = InviteLinkSerializer
    queryset = TeamInviteLink.objects.all()
    
    def get_object(self) -> TeamInviteLink:
        teamid = self.kwargs.get("id", None)
        # Temporary check that user is owner TODO: next need approve to moderators
        if Team.objects.get(id = teamid).owner_id != self.request.user:
            self.permission_denied(self.request, code=status.HTTP_405_METHOD_NOT_ALLOWED)
        obj = get_object_or_404(self.get_queryset(), team_id = teamid)
        return obj
    
    @decorators.action(methods=[
        methods.GET, methods.POST, methods.DELETE
    ], detail=False)
    def invite_link(self, request, **kwargs):
        if request.method == methods.GET:
            instance: TeamInviteLink = self.get_object()
            return response.Response(self.serializer_class(instance).data)
        
        if request.method == methods.POST:
            serializer = self.get_serializer(data=request.data, 
                                             context={
                                                 "team_id": self.kwargs.get("id", None)
                                                 })
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        if request.method == methods.DELETE:
            instance: TeamInviteLink = self.get_object()
            instance.delete()
            return response.Response(
                status=status.HTTP_204_NO_CONTENT
            )
        
        return response.Response(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
            
     