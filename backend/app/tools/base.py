from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel
from sqlalchemy.orm import Session


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    is_side_effecting: bool
    input_model: type[BaseModel]
    run: Callable[[Session, BaseModel], dict[str, Any]]
