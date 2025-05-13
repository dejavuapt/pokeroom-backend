import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from apps.core.teams.models import Team, TeamMember
from types import MethodType

UserModel = get_user_model()

# TODO: Дописать тесты, а лучше по юзкейсам начать думать, что юзер создает, добавляет, редактирует и т.п.
class TestTeamModel:
    pytestmark: list[pytest.MarkDecorator] = [pytest.mark.django_db]

    # TODO: Разобраться с фикстурами, потому что я всё ещё не понимаю че за бред со скоупом в pytest
    @pytest.fixture(scope='function')
    def obj_user(self) -> any:
        test_user =  UserModel(
            username = "test_username",
            password = "test_password"
        )
        test_user.save()
        return test_user
    
    @pytest.fixture(scope='function')
    def obj_team(self, obj_user) -> Team:
        team = Team.objects.create(
            name = "test_team_name",
            description = "test_some long description to get information about this test team",
            owner_id = obj_user,
        )
        team.save()
        team.create_member_by_owner();
        return team
        
    def test_team_related_model(self, obj_team: Team, obj_user):
        assert obj_team in obj_user.teams.all()
        user_membership: TeamMember = obj_user.member_in.first()
        assert user_membership.team_id == obj_team
        assert user_membership.role == 'O'
        assert user_membership.__str__() == 'test_username in test_team_name Owner'
        
    
    # do method to allow arguments?
    def test_team_methods_without_args(self, obj_team: Team, obj_user):
        methods_expected_results: dict[str,any] = {
            '__str__': "test_team_name owned by test_username", 
            'get_team_name': "test_team_name",
            'get_owner_name': "test_username"
        }
        for fun_name, expected_val in methods_expected_results.items():
            f = getattr(obj_team, fun_name)
            if type(f) is MethodType:
                actual_result = f()
                assert actual_result == expected_val
            else:
                assert False, ('That attribute doesn\' exist or is not a function')
        
    def test_create_team(self, obj_team: Team, obj_user):
        try:
            team_with_existed_name = Team.objects.create(
                name = "test_team_name",
                owner_id = obj_user
            )
            team_with_existed_name.save()
        except IntegrityError:
            assert True
        # except:
        #     assert False, ('Some another exception')
        else:
            assert False, ('Can create object with existing name.')
