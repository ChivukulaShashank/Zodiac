# TODO: Implement
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Workspace:
    name:str
    path:Path
    config:dict
    resources:dict = field(default_factory= dict)