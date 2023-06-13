from __future__ import annotations
import re
from typing import TYPE_CHECKING, Protocol, Any

if TYPE_CHECKING:
    from State import State


class AccessRule(Protocol):
    def __call__(self, state: State, **kwargs) -> bool:
        ...


# Variable names and values used by rule execution,
# will be automatically filled by Items
allowed_globals: dict[str, Any] = {}


_escape: re.Pattern[str] = re.compile(r'[\'()[\]-]')


def escape_name(name: str) -> str:
    return _escape.sub('', name.replace(' ', '_'))
