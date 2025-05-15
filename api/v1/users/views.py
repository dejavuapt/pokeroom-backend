from django.shortcuts import render

# Create your views here.
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from api.v1.teams.serializers import TeamSreializer
from djoser import views

UserModel = get_user_model()

class UserViewSet(views.UserViewSet):
    
    @action(["get"], detail=False)
    def teams(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
