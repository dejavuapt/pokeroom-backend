import pytest
from apps.core.teams.models import Team, Membership
from apps.core.teams.tests.test_fixutres import team_factory, user_factory
from api.v1.teams.views import TeamViewSet
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient as Client
from rest_framework import status
from django.urls import reverse
import requests
from conftest import *
import os, json


User = get_user_model()

def temp_write_to_file(result):
    file_path = os.path.join(os.path.dirname(__file__), 'output.json')
    with open(file_path, 'w') as json_file:
        json.dump(result, json_file, indent=4)

# GET /u/teams/ & /u/teams/{name}/
def test_user_teams(auth_client: Client, user_data_factory) -> None:
    team_name:str = "TestTeamName"
    user_data: dict = user_data_factory()
    Team.objects.create(
        name = team_name, 
        owner_id = User.objects.filter(username = user_data.get("username")).first()
    )
     
    url: str = reverse("users:user-teams-list")
    resp = auth_client.get(path = url)
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data) == 1
    
    url: str = reverse("users:user-teams-list") + team_name + "/"
    resp = auth_client.get(path = url)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data.get("data").get("name") == team_name


# View members by team 
# GET OPTIONS /u/teams/{name}/members/
def test_view_team_members(auth_client, user_data_factory, team_factory, user_factory) -> None:
    user_data: dict = user_data_factory()
    user = User.objects.filter(username = user_data.get("username")).first()
    
    team_name: str = "TestTeamName"
    team: Team = team_factory(name = team_name, owner_id = user)
    
    another_user = user_factory(username = "AnotherUser", email = "another@example.com")
    team.add_member(another_user)
    
    url: str = reverse("users:team-members-list", kwargs={"name": team_name})
    resp = auth_client.get(path = url)
    assert resp.status_code == status.HTTP_200_OK


# Add member only for moderator or owner
    
    
    # # POST /api/v1/t/
    # def test_create_team(self, auth_client: Client):
    #     data_to_create = {
    #         "name": "test_team-name",
    #     }
    #     request = auth_client.post(reverse("teams:t-create"), data_to_create)
    #     teams = Team.objects.filter(name = data_to_create.get("name"))
    #     assert teams.exists()
    #     assert teams.first().owner_id == request.user
    #     assert teams.first().description == None
        
    
    