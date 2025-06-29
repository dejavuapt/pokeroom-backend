from api.v1.teams.serializers import TeamSreializer, InviteLinkSerializer, MembershipSerializer
from apps.core.teams.models import Team, TeamInviteLink

from rest_framework import status, viewsets, response, permissions, decorators
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth import get_user_model
from http import HTTPMethod as methods

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from typing import Optional, Any
from datetime import timedelta

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
        """
        Handle operation to join into the team by token.
        
        Supported HTTP methods:
        - POST: Add the user who sent the request to the team byt token.
        
        Args:
            request (Request): The HTTP request object.
            
        Returns:
            Response: 
                - 200 Successfully joined the team. Returns the team's data.
                - 400 The token was not provided in the request.
                - 404 The token does not exist in the database.
                - 406 The token has expired.
                - 418 The user is already a member of the team.
            
        Raises:
            Http404: If the token is not found (via get_object_or_404).
        """
        token = request.data.get("token", None)
        if token is None:
            return response.Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "Token hasn't provided"})
        
        token_model: TeamInviteLink = get_object_or_404(TeamInviteLink.objects.all(), token=token)
        if not self._is_valid_invite_link(token_model):
            return response.Response(status=status.HTTP_406_NOT_ACCEPTABLE, data={"detail": "Token has expired."})
        
        team_by_token: Team = get_object_or_404(Team.objects.all(), invite_link=token_model)
        member = team_by_token.add_member(self.request.user)
        if member is None:
            return response.Response({"detail": "Can't join into the team you're on."}, status=status.HTTP_418_IM_A_TEAPOT)
        
        # channels_layer.group_send(team_id: str, { action: team_member_joined, member: member_serialize(member) })
        #joBo6Vf0neOb9WjPeNz0BA
        cl = get_channel_layer()
        # serialzed_member = MembershipSerializer(member)
        # serialzed_member.is_valid(raise_exception=True)
        # serialzed_member.save()
        async_to_sync(cl.group_send)(f"team_{str(team_by_token.id)}", 
                                                      {'type': 'member.joined',
                                                       'member': {
                                                           'name': member.user.username,
                                                           'role': member.role,
                                                       }})
        # BUG: Чето перестал проходить после добавления каналов, нужно решить это как-то
        return response.Response(
            self.serializer_class(team_by_token).data,
            status=status.HTTP_200_OK
        )
        
    @staticmethod
    def _is_valid_invite_link(token: TeamInviteLink) -> bool:
        return not (timezone.now() - token.expires_at) >= timedelta(days=1)
            
        
   
   
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
        """
        Handles operations related to team invite links.

        Supported HTTP methods:
        - GET: Retrieve the current invite link for the team.
        - POST: Create a new invite link for the team using the provided data.
        - DELETE: Delete the existing invite link.

        Parameters:
            request (Request): The HTTP request object.
            **kwargs: Additional keyword arguments, including 'id' for identifying the team.

        Returns:
            Response: 
                - 200 OK with serialized invite link data on GET.
                - 201 Created with serialized data on successful POST.
                - 204 No Content on successful DELETE.
                - 405 Method Not Allowed for unsupported methods.
        """

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
        
        return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
            
     