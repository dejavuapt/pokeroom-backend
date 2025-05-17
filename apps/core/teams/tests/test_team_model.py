import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from apps.core.teams.models import Team, TeamMember
from types import MethodType

UserModel = get_user_model()

# TODO: Дописать тесты, а лучше по юзкейсам начать думать, что юзер создает, добавляет, редактирует и т.п.
class TestTeamModel:
    pytestmark: list[pytest.MarkDecorator] = [pytest.mark.django_db]
    
    @pytest.fixture(scope='function')
    def user(self, **kwargs): 
        def _user(**kwargs):
            user = UserModel.objects.create(**kwargs)
            user.save()
            return user
        return _user
       
    @pytest.fixture(scope='function')
    def team(self, **kwargs):
        def _team(**kwargs):
            team = Team.objects.create(**kwargs) 
            team.save()
            team.create_member_by_owner()
            return team
        return _team
            
    
    @pytest.fixture(scope='function')
    def complex_data(self, user, team) -> dict:
        first_user = user(username = "test_username", password = "test_password")
        team_by_first_user: Team = team(name = "test_team_name", description="a long...", owner_id=first_user)
        member_first = user(username = "test_username_two", email = "email_one@one.one", )
        member_second = user(username = "test_username_three", email = "email_tow@two.two",)
        return {
            'owner': first_user,
            'team': team_by_first_user,
            'member_one': member_first,
            'member_two': member_second,
        }
        
    def test_team_related_model(self, complex_data: dict):
        membership = complex_data.get('owner').member_in.first()
        assert complex_data.get('team') in complex_data.get('owner').teams.all()
        assert membership.team_id == complex_data.get('team') 
        assert membership.role == 'O'
        assert membership.__str__() == 'test_username in test_team_name Owner'
       
    def test_team_methods(self, complex_data: dict):
        methods_expected_results: dict[str, any] = {
            '__str__': "test_team_name owned by test_username",
            'get_team_name': "test_team_name",
            'get_owner_name': "test_username"
        } 
        for fun_name, expected_val in methods_expected_results.items():
            f = getattr(complex_data.get('team'), fun_name)
            if type(f) is MethodType:
                result = f()
                assert result == expected_val
            else:
                assert False, ('[NOT PASSED] That attribute doesn\'t exist or is not a method type')
    
    def test_unique_create(self, complex_data: dict, team):
        try:
            new_team = team(name = str(complex_data.get('team').name), owner_id = complex_data.get('owner'))
        except IntegrityError:
            assert True
        else:
            assert False, ('[NOT PASSED] Model allowed create a team with existing name by user')
            
    def test_add_members(self, complex_data: dict):
        team: Team = complex_data.get('team').add_member(complex_data.get('member_one'))
        assert team in complex_data.get('member_one').team_set.all()
        assert 'Default' == team.team_in.last().get_role_display()