import pytest
from apps.core.teams.models import Team, Membership
from apps.core.teams.tests.test_fixutres import team_factory, user_factory
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
        
        
@pytest.fixture
def complex(db, user_data_factory, team_factory, user_factory):
    user_data: dict = user_data_factory()
    user = User.objects.filter(username = user_data.get("username")).first()
    
    team_name: str = "TestTeamName"
    team: Team = team_factory(name = team_name, owner_id = user)
    
    another_user = user_factory(username = "AnotherUser", email = "another@example.com")
    return {
        "user": user,
        "user_team": team,
        "another_user": another_user    
    } 

# GET /u/teams/ & /u/teams/{name}/
def test_user_teams(auth_client: Client, complex) -> None:
    team = complex.get("user_team")
    
    main_url:str = reverse("teams:user-teams-list")
     
    url: str = main_url
    resp = auth_client.get(path = url)
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data) == 1
    
    url = main_url + str(team.id) + "/"
    resp = auth_client.get(path = url)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data.get("data").get("name") == team.name
    
    resp = auth_client.post(path = main_url, data = {
        'name': "NewTestTeam",
    })
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data.get("owner") == str(complex.get("user").id)
    
    with pytest.raises(ValueError):
        resp = auth_client.post(path = main_url, data = {
            'name': "TeamForAnotherUser",
            'owner_id': str(complex.get("another_user").id)
        })
    
    new_team = Team.objects.get(name = "NewTestTeam")
    url = main_url + str(new_team.id) + "/"
    resp = auth_client.patch(path = url, data = {
        'name': "NOWtestteam", 'description': "Wow! It's desc!!!"
    })
    assert resp.status_code == status.HTTP_200_OK
    
    resp = auth_client.get(path = url)
    assert resp.data.get("data").get("name") == "NOWtestteam" \
        and resp.data.get("data").get("description") == "Wow! It's desc!!!"
        
    resp = auth_client.delete(path = url)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert Membership.objects.all().count() == 1
    
    
    
    
# TODO: Convert to atomics test
# GET OPTIONS /u/teams/{name}/members/
# PUT PATCH DELETE /u/teams/{name}/members/{user_id} - change role and get owner to another user
def test_view_team_members(auth_client, complex) -> None:
    user = complex.get("user")
    team = complex.get("user_team") 
    another_user = complex.get("another_user")
    
    main_url: str = reverse("teams:team-members-list", kwargs={"id": str(team.id)})

    resp = auth_client.post(path = main_url, data = {"username": another_user.username}, format = 'json')
    assert resp.status_code == status.HTTP_201_CREATED
     
    resp = auth_client.get(path = main_url)
    assert resp.status_code == status.HTTP_200_OK
    
    url: str = main_url + '%s/' % another_user.username
    resp = auth_client.patch(path= url, data= {"role": "moderator"})
    assert resp.status_code == status.HTTP_200_OK
    assert Membership.objects.filter(team = team, user = another_user).first().role == 'M'
    
    resp = auth_client.delete(path = url)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert Team.objects.filter(id = team.id).first().members.count() == 1
    resp = auth_client.post(path = main_url, data = {"username": another_user.username}, format = 'json')
    
    url = main_url + '%s/' % user.username
    resp = auth_client.patch(path = url, data = {"role": "moderator"})
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    resp = auth_client.delete(path = url)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    
    url = main_url + '%s/' % another_user.username
    resp = auth_client.patch(path = url, data = {"role": "owner"})
    assert resp.status_code == status.HTTP_200_OK
    assert Membership.objects.filter(team = team, user = another_user).first().role == 'O'
    assert Membership.objects.filter(team = team, user = user).first().role == 'D'
    assert Team.objects.filter(owner_id = another_user).first().name == team.name
    assert Team.objects.filter(owner_id = user).count() == 0
    
    resp = auth_client.patch(path = url, data = {"role": "moderator"})
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    
    resp = auth_client.delete(path = url)
    assert resp.status_code == status.HTTP_403_FORBIDDEN

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
        
    
    