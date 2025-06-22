import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from apps.game.models import GameInstance, GameTypesChoices, TaskEvaluationGameState
from apps.game.poker_planning.task_evaluation import TasksEvaluationState
from apps.core.teams.models import Team
from apps.game.engine import GameEngine


UserModel = get_user_model()




@pytest.fixture
def team_factory(db):
    def create_team(name):
        t = Team.objects.create(name=name)
        t.save()
        return t
    return create_team

def test_create_game(team_factory):
    # team = team_factory("TestTeam")
    
    # Create game in team
    game_instance = GameInstance.objects.create(
        # team=team,
        config={},
        type=GameTypesChoices.POKER
    )
    engine = GameEngine()
    engine.bootstrap(game_instance) # or resume ofcs
    
    
    
    pass