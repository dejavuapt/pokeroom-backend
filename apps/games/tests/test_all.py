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
    engine = GameEngine()
    engine.bootstrap(GameTypesChoices.POKER) # Прямо тут игра создана уже и есть в бдшке и уже есть запись в бд по стейту
    
    for task_name in ["Task1", "Task2", "Task3"]:
        engine._state_manager.handle_action("add-task", {"name": task_name})
    
    engine._state_manager.next()
    
    # choose a new task
    engine._state_manager.handle_action("set-current-task", {"name": "Task1"})
    
    # guys estimate a task
    engine._state_manager.handle_action("add-user-estimate", {"username": "petya", "estimate": 1})
    engine._state_manager.handle_action("add-user-estimate", {"username": "vasya", "estimate": 8})
    engine._state_manager.handle_action("add-user-estimate", {"username": "luda", "estimate": 5})
    
    #BUG: Править чтобы дикт можно было не передавать
    engine._state_manager.handle_action("calculate-current-task-estimate", None)
    
    # ... and again from current task
    
    engine._state_manager.next()
    # result data is a {"Task1": 4, "Task2": 5, ...}
    
    
    
        
    
    
    
    # engine.bootstrap(game_instance) # or resume
    
    # engine._state_manager.handle_action("add-user-estimate", {"username": "test", "estimate": 10})
    
    pass