import pytest
from django.contrib.auth import get_user_model
from apps.core.teams import models as t_models
from apps.core.rooms import models as r_models

UserModel = get_user_model()


class TestRoomModel:
    pytestmark: list[pytest.MarkDecorator] = [pytest.mark.django_db]
    
    ## FIXTURES
    
    # TODO: maybe i can create scope to test session???
    @pytest.fixture(scope='function')
    def obj_user(self):
        pass
    
    @pytest.fixture(scope='function')
    def obj_team(self):
        pass
    
    @pytest.fixture(scope='function')
    def obj_room(self):
        pass
    
    ## TEST CASES
    
    @pytest.mark.skip
    def test_create_room(self):
        """
        Test create room, add members - only in team, invite guesets.
        """
        pass
    
    @pytest.mark.skip
    def test_choose_poker_game(self):
        """
        Test means when choose a target game it automate create game_session \n
        and get a based values
        """
        pass
    
    @pytest.mark.skip
    def test_closed_room_after_24hour(self):
        """
        Test check functionallity when room auto closed after 24h
        """
        pass
    
    @pytest.mark.skip
    def test_change_host_and_operators_with_room(self):
        """
        Test change hosts, manipulations like: change stage, closed the room, etc.
        """
        pass