from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets

from apps.core.teams.models import Team
from .serializers import TeamSreializer

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSreializer

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