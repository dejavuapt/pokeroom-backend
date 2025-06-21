from api.v1.teams.serializers import TeamSreializer
from apps.core.teams.models import Team

from rest_framework import status, viewsets, response, permissions
from django.shortcuts import get_object_or_404

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
   
   
class TokenViewset(viewsets.GenericViewSet):
    pass 