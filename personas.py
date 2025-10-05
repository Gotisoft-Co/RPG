from dataclasses import dataclass, field
from typing import List
from elements import Element
from skills import Skill
@dataclass
class Persona:
    name: str
    skills: List[Skill] = field(default_factory=list)
    weaknesses: List[Element] = field(default_factory=list)
    resists: List[Element] = field(default_factory=list)
# Набор стартовых персон ГГ
AGATHION = Persona(
    name="Агатион",
    skills=[Skill("Зио", Element.ELEC, 22, 8, inflict_shock=True), Skill("Буфу", Element.ICE, 18, 6)],
    weaknesses=[Element.WIND],
    resists=[Element.ELEC]
)
PIXIE = Persona(
    name="Пикси",
    skills=[Skill("Диa", Element.PHYS, 0, 8), Skill("Гару", Element.WIND, 20, 6)],
    weaknesses=[Element.ICE],
    resists=[Element.WIND]
)
JACK_FROST = Persona(
    name="Джек Фрост",
    skills=[Skill("Буфу", Element.ICE, 26, 8), Skill("Мабуфу", Element.ICE, 18, 10, target_all=True)],
    weaknesses=[Element.FIRE],
    resists=[Element.ICE]
)
STARTER_PERSONAS = [AGATHION, PIXIE, JACK_FROST]