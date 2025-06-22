from typing import Optional

def stage_action(action_name: Optional[str] = None, **kwargs):
    def decorator(func): 
        func.is_action = True
        func.action_name = action_name if action_name else func.__name__.replace('_', '-').capitalize()
        func.kwargs = kwargs
    return decorator