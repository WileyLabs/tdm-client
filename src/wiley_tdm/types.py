"""Common type definitions for TDM Client."""

# Standard library imports
from os import PathLike
from typing import Union

# Type alias matching standard library behavior
StrPath = Union[str, PathLike[str]]
