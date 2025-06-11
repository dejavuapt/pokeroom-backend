import pytest
from api.v1.users.views import UserViewSet
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
import requests

User = get_user_model()

    
@pytest.fixture()
def client():
    return APIClient()

# @pytest.fixture()
# def user_factory(db):
#     def create_user( username = "TestUsername", email = "user@example.com", password = "testpassword"):
#         return User.objects.create(username = username, email = email, password = password)
#     return create_user
@pytest.fixture()
def user_data_factory():
    def create_user_data(
            username = "TestUsername",
            email = "user@example.com",
            password = "test_password"
        ) -> dict[str, str]:
            return {
                "username": username,
                "email": email,
                "password": password
            }
    return create_user_data

@pytest.fixture()
def auth_client(db, client: APIClient, user_data_factory) -> APIClient:
    register_url = reverse("users:u-list")
    user_data = user_data_factory()
    client.post(register_url, user_data)
    
    auth_url = reverse("token:jwt-create")
    access_token = client.post(
        auth_url, { "username": user_data.get("username"), "password": user_data.get("password")  }
    ).data.get("access")
    client.credentials(HTTP_AUTHORIZATION='Bearer %s' % (access_token))
    
    return client
    
