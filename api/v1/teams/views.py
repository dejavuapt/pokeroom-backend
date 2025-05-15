from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
# Create your views here.
from rest_framework.views import APIView
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets

from apps.core.teams.models import Team, TeamMember
from apps.core.teams.choices import TeamMemberRoleChoice

from http import HTTPMethod

from .serializers import TeamSreializer, MembershipSerializer

UserModel = get_user_model()


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSreializer
    
    @action(["get"], detail=True)
    def get_info(self, request, pk=None):
        from_user = request.data
        user_id = from_user.get('user_id', None)
        if user_id == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message' : "Wow! user %s It's %s" % (user_id, pk),
        })
    #6f6b0cf8-a411-4c0b-bfaa-09c7f2382f40 
    @action(methods=[HTTPMethod.GET, HTTPMethod.POST], detail=True)
    def members(self, request, pk = None):
        team = get_object_or_404(Team, pk=pk)
        if request.method == HTTPMethod.POST:
            user = get_object_or_404(UserModel, id=request.data.get('user_id'))
            current_user = request.user
            role = request.data.get('role', TeamMemberRoleChoice.DEFAULT)
            if current_user.member_in.filter(team_id=team, 
                                             role__in=[TeamMemberRoleChoice.OWNER, 
                                                       TeamMemberRoleChoice.MODERATOR]).exists():
                new_membership = TeamMember.objects.create(
                    user_id = user,
                    role = role,
                    team_id = team
                )
                serializer = MembershipSerializer(new_membership)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        if request.method == HTTPMethod.GET:
            member_ships = team.team_in.all()
            serializer = MembershipSerializer(member_ships, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_403_FORBIDDEN)
            
        
        

# class APITeam(APIView):
#     def get(self, request):
#         teams = Team.objects.all()
#         serializer: TeamSreializer = TeamSreializer(teams, many=True)
#         return Response(serializer.data)
    
#     def post(self, request):
#         serializer: TeamSreializer = TeamSreializer(data = request.data)
#         if(serializer.is_valid()):
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
# def api_team_detail(request, team_id):
#     team = Team.objects.get(id=team_id)
#     if request.method == 'PUT' or request.method == 'PATCH':
#         serializer: TeamSreializer = TeamSreializer(team, data = request.data, partial = True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     if request.method == 'DELETE':
#         team.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
    
#     serializer: TeamSreializer = TeamSreializer(team)
#     return Response(serializer.data, status=status.HTTP_200_OK)