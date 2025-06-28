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
    
    engine = GameEngine().bootstrap_or_resume(game_type=GameTypesChoices.POKER,
                                              team=team,
                                              init_user=user1)
    instance = engine._game_instance
    assert isinstance(instance, GameInstance)
    assert GameInstance.objects.all().first() == instance
    assert ppModels.TaskEvaluationGameState.objects.all().count() == 0
    assert ppModels.LobbyGameState.objects.all().count() == 1
    # current state is lobby
    
    # prepare lobby from tasks
    for task_name in ["Task1", "Task2", "Task3"]:
        engine.do("add-task", {"name": task_name})
        
    assert type(engine._game_manager._current_state.instance) is ppModels.LobbyGameState
    assert ppModels.LobbyGameState.objects.first().result_data == {"tasks": ["Task1", "Task2", "Task3"]}
    
    engine._game_manager.state_forward()
    
    assert type(engine._game_manager._current_state.instance) is ppModels.TaskEvaluationGameState
    assert ppModels.LobbyGameState.objects.first().completed
    
    engine.do("set-current-task", {"name": "Task1"})
    
    assert ppModels.TaskEvaluationGameState.objects.first().current_task == "Task1"
    
    engine.do("add-user-estimate", {"username": "petya", "estimate": 1})
    engine.do("add-user-estimate", {"username": "vasya", "estimate": 8})
    
    ath_engine = GameEngine()
    if ath_instance := ath_engine.bootstrap_or_resume(team=team):
        assert type(ath_engine._game_manager._current_state) == type(engine._game_manager._current_state)
        ath_engine.do("add-user-estimate", {"username": "luda", "estimate": 5})
    
    
    assert ppModels.TaskEvaluationGameState.objects.first().players_votes == {"luda": 5, "vasya": 8, "petya": 1}
    
    ath_engine = GameEngine()
    if ath_instance := ath_engine.bootstrap_or_resume(team=team):
        ath_engine.do('calculate-current-task-estimate')
    
    assert ppModels.TaskEvaluationGameState.objects.first().current_task == None
    assert ppModels.TaskEvaluationGameState.objects.first().players_votes == {}
    assert ppModels.TaskEvaluationGameState.objects.first().result_data == {"Task1": 5}
    
    state = engine._game_manager.state_forward()
    print(type(state))
    assert type(engine._game_manager._current_state.instance) is ppModels.LobbyGameState
    assert ppModels.TaskEvaluationGameState.objects.first().completed
    
    # Мне лень дописывать это, буду править в рабочем порядке
    state = ath_engine._game_manager.state_forward()
    ath_engine = GameEngine()
    if ath_instance := ath_engine.bootstrap_or_resume(team=team):
        print(ath_engine._game_manager._current_state.instance.result_data)