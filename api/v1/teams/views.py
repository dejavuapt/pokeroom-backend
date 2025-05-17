from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
# Create your views here.
from rest_framework.views import APIView
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework import viewsets

from .permissions import CurrentUserIsModeratorOrOwnerOrAdmin, CurrentUserIsOwnerOrAdmin
from apps.core.teams.models import Team, TeamMember
from apps.core.teams.choices import TeamMemberRoleChoice

from http import HTTPMethod

from .serializers import TeamSreializer, MembershipSerializer

UserModel = get_user_model()


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSreializer
    
    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = {'user': self.request.user}
        return super().get_serializer(*args, **kwargs)
    
    def get_permissions(self):
        if self.action == "members":
            self.permission_classes = CurrentUserIsModeratorOrOwnerOrAdmin
        elif self.action == "destroy":
            self.permission_classes = CurrentUserIsOwnerOrAdmin
        return super().get_permissions()
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # paginate skip
        current_user = request.user
        user_teams = Team.objects.filter(
            Q(team_in__user_id=current_user) | Q(owner_id=current_user)
        ).distinct()
        if user_teams.exists():
            queryset = queryset.filter(id__in=user_teams.values_list('id', flat=True))
        else: 
            queryset = queryset.none()
        
        serializer = self.get_serializer(queryset, many = True)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status = status.HTTP_204_NO_CONTENT)
        
        # return Response(
        #     data = {"message": "You haven't permissions."},
        #     status=status.HTTP_403_FORBIDDEN
        # )
    # TODO: Переработать пост запрос, т.к. у Пользователей не будет поиск по пользователям
    # поэтому добавление нового пользователя в команду нужно делать через внешний запрос 
    @action(methods=[HTTPMethod.GET, HTTPMethod.POST], detail=True)
    def members(self, request, pk = None):
        team = get_object_or_404(Team, pk=pk)
        if request.method == HTTPMethod.POST:
            user = get_object_or_404(UserModel, id=request.data.get('user_id'))
            role = request.data.get('role', TeamMemberRoleChoice.DEFAULT)
            new_membership = TeamMember.objects.create(
                user_id = user,
                role = role,
                team_id = team
            )
            serializer = MembershipSerializer(new_membership)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == HTTPMethod.GET:
            member_ships = team.team_in.all()
            serializer = MembershipSerializer(member_ships, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(
            data = {"message": "You haven't permissions."},
            status=status.HTTP_403_FORBIDDEN
        )
            