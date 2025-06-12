import pytest
from django.contrib.auth import get_user_model
from apps.core.teams.models import Team, Membership
from apps.core.teams.choices import MembershipRoleChoice

UserModel = get_user_model()


@pytest.fixture()
def user_factory(db):
    def create_user(
        username = "TestUsername",
        password = "testpassword",
        email = "user@example.com",
        **kwrags
    ):
        return UserModel.objects.create(username = username, 
                                        password = password, 
                                        email = email, 
                                        **kwrags)
    return create_user

@pytest.fixture()
def team_factory(db):
    def create_team(
        name = "TestTeamName",
        description = "Some Description",
        **kwargs
    ):
        return Team.objects.create(name = name, description = description, **kwargs)
    return create_team

@pytest.fixture()
def membership_factory(db ):
    def create_membership(
        user,
        team,
        role = MembershipRoleChoice.DEFAULT.value
    ):
        return Membership.objects.create(user = user, team = team, role = role)
    return create_membership