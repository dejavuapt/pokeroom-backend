import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from apps.games.models import poker_planning as ppModels
from apps.games.models.models import GameInstance, GameTypesChoices 
from apps.core.teams.models import Team
from apps.games.core.engine import GameEngine


User = get_user_model()

@pytest.fixture
def team_factory(db):
    def create_team(name, user):
        t = Team.objects.create(name=name, owner_id=user)
        t.save()
        return t
    return create_team

@pytest.fixture
def user_factory(db):
    def create_user(username, password):
        u = User.objects.create(username=username, password=password)
        u.save()
        return u
    return create_user
        

def test_game_pipline(team_factory, user_factory):
    user1 = user_factory("test", "test_password")
    team = team_factory("test_team", user1)
    
    engine = GameEngine()
    instance = engine.bootstrap(game_type=GameTypesChoices.POKER,
                                team=team,
                                init_user=user1)
    assert isinstance(instance, GameInstance)
    assert GameInstance.objects.all().first() == instance
    assert ppModels.TaskEvaluationGameState.objects.all().count() == 0
    assert ppModels.LobbyGameState.objects.all().count() == 1
    # current state is lobby
    
    # prepare lobby from tasks
    for task_name in ["Task1", "Task2", "Task3"]:
        engine._state_manager.handle_action("add-task", {"name": task_name})
        
    assert type(engine._state_manager._current_state.instance) is ppModels.LobbyGameState
    assert ppModels.LobbyGameState.objects.first().result_data == {"tasks": ["Task1", "Task2", "Task3"]}
    
    engine._state_manager.state_forward()
    
    assert type(engine._state_manager._current_state.instance) is ppModels.TaskEvaluationGameState
    assert ppModels.LobbyGameState.objects.first().completed
    
    engine._state_manager.handle_action("set-current-task", {"name": "Task1"})
    
    assert ppModels.TaskEvaluationGameState.objects.first().current_task == "Task1"
    
    engine._state_manager.handle_action("add-user-estimate", {"username": "petya", "estimate": 1})
    engine._state_manager.handle_action("add-user-estimate", {"username": "vasya", "estimate": 8})
    engine._state_manager.handle_action("add-user-estimate", {"username": "luda", "estimate": 5})
    
    assert ppModels.TaskEvaluationGameState.objects.first().players_votes == {"luda": 5, "vasya": 8, "petya": 1}
    
    engine._state_manager.handle_action('calculate-current-task-estimate', {})
    
    assert ppModels.TaskEvaluationGameState.objects.first().current_task == None
    assert ppModels.TaskEvaluationGameState.objects.first().players_votes == {}
    assert ppModels.TaskEvaluationGameState.objects.first().result_data == {"Task1": 5}
    
    
    # # --- disconnect
    # another_client = GameEngine()
    # same_instance = another_client.resume(team=team)
    # if same_instance:
    #     assert type(another_client._state_manager._current_state) == TasksEvaluationState
    