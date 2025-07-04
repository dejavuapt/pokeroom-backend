import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from typing import Optional
from django.urls import reverse

User = get_user_model()

#TODO: Move Client and fixtures to conftest of all api's tests
class Client(APIClient):
    
    _user: Optional[User] = None # type: ignore
    _refresh_token: Optional[str] = None
    _access_token: Optional[str] = None
    
    @property
    def user(self) -> User:
        return self._user
    
    @property
    def refresh_token(self) -> str:
        return self._refresh_token
    
    @property
    def access_token(self) -> str:
        return self._access_token
    
    def auth(self, active_user: User) -> 'Client': # type: ignore
        self.logout()
        refresh_token = RefreshToken.for_user(active_user)
        
        self._refresh_token = str(refresh_token)
        self._access_token = str(refresh_token.access_token)
        
        self.credentials(HTTP_AUTHORIZATION='Bearer %s' % (self._access_token))
        self._user = active_user
        return self

        
@pytest.fixture
def authorized_user(user: User) -> Client:
    return Client().auth(user)

@pytest.fixture
def unauthorized_user() -> Client:
    return Client()

# ------ UP MOVED 
from apps.core.teams.models import Team

def test_create_game(authorized_user: Client, 
                     unauthorized_user: Client, 
                     team: Team) -> None:
    url: str = reverse("teams:poker-game-list", args=(str(team.id)))
    
    resp = authorized_user.get(url)
    assert resp.status_code == 200
    assert resp.data == []
    
    resp = authorized_user.post(url)
    
    assert resp.status_code == 200
    # assert resp.data == {
    #     "host_by": "...",
    #     "type": "P",
    #     "status": "O",
    #     "config": {},
    #     "created_at": ""
    # }