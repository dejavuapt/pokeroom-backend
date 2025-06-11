# import pytest
# from apps.core.teams.models import Team, Membership
# from api.v1.teams.views import TeamViewSet
# from api.v1.users.views import UserViewSet
# from django.contrib.auth import get_user_model
# from django.contrib.auth.models import AbstractUser
# from rest_framework.test import APIClient as Client
# from django.urls import reverse
# # from rest_framework.request import Request
# import requests

# User = get_user_model()


# class TestTeamViewset():
    
#     @pytest.fixture(scope='function')
#     def client(self):
#         return Client()
    
#     @pytest.fixture(scope='function')
#     def auth_client(self, client: Client) -> Client:
#         register_url = UserViewSet.reverse_action("u-list") # Ощущение, что это не правильный роут
#         user_data = {
#             "username": "test_user",
#             "email": "test_user@gmail.cos",
#             "password": "test_password1"
#         }
#         client.post(register_url, user_data)
        
#         auth_url = reverse("token:jwt-create")
#         access_token = client.post(
#             auth_url, { "username": user_data.get("username"), "password": user_data.get("password")  }
#         ).data.get("access")
#         client.credentials(HTTP_AUTHORIZATION='Bearer %s' % (access_token))
        
#         return client
    
    
    
#     # POST /api/v1/t/
#     def test_create_team(self, auth_client: Client):
#         data_to_create = {
#             "name": "test_team-name",
#         }
#         request = auth_client.post(reverse("teams:t-create"), data_to_create)
#         teams = Team.objects.filter(name = data_to_create.get("name"))
#         assert teams.exists()
#         assert teams.first().owner_id == request.user
#         assert teams.first().description == None
        
    
    