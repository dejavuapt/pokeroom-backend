import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from apps.core.teams.models import Team, TeamInviteLink
from types import MethodType
from datetime import datetime, timedelta, timezone
import secrets

UserModel = get_user_model()

class TestTeamInviteLinkModel:
    pytestmark: list[pytest.MarkDecorator] = [pytest.mark.django_db]
    
    @pytest.fixture(scope='function')
    def obj_team(self) -> Team:
        test_user =  UserModel(username = "test_username",password = "test_password")
        test_user.save()
        team = Team.objects.create(
            name = "test_team_name",
            description = "test_some long description to get information about this test team",
            owner_id = test_user,
        )
        team.save()
        return team
    
    # idk, it's look like that test doen't need
    def test_is_valid_token(self, obj_team: Team) -> None:
        team_invite_link = TeamInviteLink.objects.create(
            team_id = obj_team
        )
        current_time: datetime = datetime.now(tz=timezone.utc)
        assert current_time < obj_team.invite_link.created_at + timedelta(days=1)

    

