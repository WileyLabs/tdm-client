"""Common type definitions for TDM Client."""

from os import PathLike
from typing import Union

# Type alias matching standard library behavior
StrPath = Union[str, PathLike[str]]
