from apps.games.core.state import State
from typing import Optional, Union, Any
from apps.games.core.utils.decorators import stage_action
import copy

class TasksEvaluationState(State):
    _name = "Task Evaluation"
        
    def in_(self, tasks: Optional[list[str]] = None) -> None:
        if tasks is None:
            raise NotImplementedError()    
        self._instance.init_tasks(tasks)
    
    def out_(self) -> dict[str, Union[str, int]]:
        return self._instance.reveal_results() 
                
    @property
    def current_task(self) -> str:
        return self._instance.current_task
    
    # TODO: Need check that task exist in a tasks
    @stage_action
    def set_current_task(self, name: str) -> None:
        self._instance.current_task = name
        self._instance.save()

    @stage_action
    def add_user_estimate(self, username: str, estimate: int) -> None:
        if isinstance(estimate, str): 
            try:
                estimate = int(estimate)
            except:
                estimate = 0
        self._instance.submit_vote(username, estimate)
    
    @stage_action
    def calculate_current_task_estimate(self) -> None:
        if not len(self._instance.players_votes) == 0:
            calculated_estimate: int = round(sum(self._instance.players_votes.values()) / len(self._instance.players_votes))
            self.update_task(self._instance.current_task, calculated_estimate)
            self._instance.reset()
            return

        raise NotImplementedError()
        
    @stage_action
    def update_task(self, task: str, estimate: Union[str, int]) -> None:
        self._instance.update_result({task: estimate})
        
        
class PokerLobbyState(State):
    _name = "Start lobby"
    
    def in_(self, context: Optional[Any] = None) -> None:
        self._instance.update_result({"tasks": []})
        return
    
    def out_(self) -> list[str]:
        self._instance.completed = True
        self._instance.save()
        return self.tasks
    
    @property
    def tasks(self) -> list[str]:
        return self._instance.result_data.get("tasks")    
    
    @stage_action
    def add_task(self, name: str) -> None:
        tasks: list = copy.deepcopy(self._instance.result_data.get("tasks"))
        tasks.append(name)
        self._instance.update_result({"tasks": tasks})

class PokerLobbyEndState(State):
    _name = "End lobby"
    
    def in_(self, past_result = None):
        self._instance.update_result({"solved_tasks": past_result})
        return
    
    def out_(self):
        self._instance.completed = True
        self._instance.save()
        return self.solved_tasks
    
    @property
    def solved_tasks(self) -> dict[str, Union[str, int]]:
        return self._instance.result_data.get("solved_tasks", None)
    
