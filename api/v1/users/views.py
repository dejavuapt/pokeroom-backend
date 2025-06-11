from typing import Any
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from api.v1.teams.serializers import TeamSreializer
from apps.core.teams.models import Team
from djoser import views

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