from types import MethodType
import pytest
from django.contrib.auth import get_user_model
from test_fixutres import *
from apps.core.teams.choices import MembershipRoleChoice
from django.db import IntegrityError

UserModel = get_user_model()

# ---- TEAM TESTS ----
def test_owner_membership(team_factory, user_factory) -> None:
    owner = user_factory()
    t: Team = team_factory(owner_id = owner)
    assert Membership.objects.count() == 1
    assert Membership.objects.last().get_role_display() == "Owner"
    
def test_team_methods(team_factory, user_factory):
    team_owner = user_factory()
    team = team_factory(owner_id = team_owner)
    
    method_expected_results: dict[str, any] = {
        '__str__': "TestTeamName",
        'get_team_name': "TestTeamName",
        'get_owner_name': "TestUsername"
    }
    for fn, ev in method_expected_results.items():
        f = getattr(team, fn)
        if type(f) is MethodType:
            result = f()
            assert result == ev
        else:
            assert False, ('[NP] That attribute doesn\'t exist or is not a method type')

def test_unique_create(team_factory, user_factory):
    not_unq_name: str = "NotUniqueTeam"
    team_owner = user_factory()
    team = team_factory(name = not_unq_name, owner_id = team_owner)
    with pytest.raises(IntegrityError):
        new_team = team_factory(name = not_unq_name, owner_id = team_owner) 