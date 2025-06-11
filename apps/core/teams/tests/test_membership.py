from types import MethodType
import pytest
from django.contrib.auth import get_user_model
from test_fixutres import *
from apps.core.teams.choices import MembershipRoleChoice
from django.db import IntegrityError

UserModel = get_user_model()


# ---- MEMBERSHIP TEST ---- 
    
def test_add_member(team_factory, user_factory):
    owner = user_factory()
    t: Team = team_factory(owner_id = owner) 
    
    member = user_factory(username = "ImTheMember", email = "member@example.com")
    t.add_member(member)
    assert t.members.count() == 2
    assert Membership.objects.last().role == "D"
    
    moderator = user_factory(username = "ImTheModerator", email = "moderator@example.com")
    t.add_member(moderator, MembershipRoleChoice.MODERATOR)
    assert t.members.count() == 3
    assert Membership.objects.last().role == "M"
    
    t.add_member(moderator, MembershipRoleChoice.OWNER)
    assert t.members.count() == 3
    assert Membership.objects.last().role == "M" 
    
def test_change_owner(team_factory, user_factory):
    owner = user_factory()
    t: Team = team_factory(owner_id = owner)
    new_owner = user_factory(username = "NewOwner", email = "owner@example.com")
    
    # owner do
    Team.objects.filter(pk = t.pk).update(owner_id = new_owner)
    with pytest.raises(ValueError):
        t.set_new_owner(new_owner)
    assert Membership.objects.count() == 1
    assert Membership.objects.get(user = owner).role == 'O'
    
    t.add_member(new_owner)
    t.set_new_owner(new_owner)
    assert Membership.objects.count() == 2
    assert Membership.objects.get(user = new_owner, team = t).role == 'O', ("[NP] Member not owned team.")
    assert Membership.objects.get(user = owner, team = t).role == 'D', ("[NP] Old owner hasn't stay a member.")
    
    
    
    