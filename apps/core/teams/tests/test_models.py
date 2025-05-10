import pytest
from django.contrib.auth import get_user_model
from apps.core.teams.models import Team
from types import FunctionType

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
        return team
    
    # do method to allow arguments?
    def test_team_methods_without_args(self, obj_team: Team, obj_user):
        methods_expected_results: dict[str,any] = {
            '__str__': "test_team_name owned by test_username", 
            'get_team_name': "test_team_name",
            'get_owner_name': "test_username"
        }
        for fun_name, expected_val in methods_expected_results:
            f = getattr(obj_team, fun_name)
            if type(f) is FunctionType:
                actual_result = f()
                assert actual_result == expected_val
            else:
                assert False, ('That attribute doesn\' exist or is not a function')
        