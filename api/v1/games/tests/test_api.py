from __future__ import annotations
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
    
    def auth(self, active_user: User) -> Client:
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
