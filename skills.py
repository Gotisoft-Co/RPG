from dataclasses import dataclass
from elements import Element
@dataclass
class Skill:
    name: str
    element: Element
    power: int
    mp_cost: int = 0
    cooldown: int = 0
    target_all: bool = False
    inflict_silence: bool = False
    inflict_shock: bool = False
    description: str = ""