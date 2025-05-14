from django.shortcuts import render

# Create your views here.
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from api.v1.users.serializers import UserSerializer

UserModel = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer 