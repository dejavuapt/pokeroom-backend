from apps.game.state import State
from typing import Optional, Union
from apps.game.decorators import stage_action


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
        self._instance.submit_vote(username, estimate)
    
    @stage_action
    def calculate_current_task_estimate(self) -> None:
        if not len(self._instance.players_votes) == 0:
            calculated_estimate: int = sum(self._instance.players_votes.value()) / len(self._instance.players_votes)
            self.update_task(self._instance.current_task, calculated_estimate)
            self._instance.reset()
            return

        raise NotImplementedError()
        
    @stage_action
    def update_task(self, task: str, estimate: Union[str, int]) -> None:
        self._instance.update_result({task: estimate})
        


