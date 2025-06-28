from apps.games.core.state import State
from typing import Any
from apps.games.core.utils.types import JSONDict

def state_encoder(obj: Any) -> JSONDict:
    if isinstance(obj, State):
        return obj.to_json()
    raise TypeError(f'Object of type {type(obj)} is not JSON serializable')
        