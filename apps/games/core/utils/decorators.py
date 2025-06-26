from typing import Optional
from functools import wraps

def stage_action(func, **kwargs):
    @wraps(func)
    def decorator(*args, **kwargs): 
        return func(*args, **kwargs)
    
    decorator.is_action = True
    decorator.action_name = decorator.__name__.replace('_', '-').lower()
    decorator.kwargs = kwargs
    return decorator