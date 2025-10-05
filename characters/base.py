from __future__ import annotations
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
from descriptors import BoundedStat
from elements import Element
from skills import Skill
from effects import Effect, Shield, Silence, Downed
class Human(ABC):
    hp = BoundedStat("hp",0,"max_hp"); mp = BoundedStat("mp",0,"max_mp")
    strength = BoundedStat("strength",1); agility = BoundedStat("agility",1); intelligence = BoundedStat("intelligence",1)
    def __init__(self,name:str,level:int,max_hp:int,max_mp:int,strength:int,agility:int,intelligence:int):
        self.name=name; self.level=level; self.max_hp=max_hp; self.max_mp=max_mp
        self.hp=max_hp; self.mp=max_mp; self.strength=strength; self.agility=agility; self.intelligence=intelligence
        self.effects: List[Effect]=[]; self._shield_ratio=0.0
    @property
    def is_alive(self)->bool: return self.hp>0
    def __str__(self): return f"{self.name} Lv{self.level} HP {self.hp}/{self.max_hp} MP {self.mp}/{self.max_mp}"
class CritMixin:
    crit_chance=0.05; crit_mult=1.5
    def roll_crit(self)->bool: return random.random()<self.crit_chance
    def apply_crit(self, dmg:int, is_crit:bool)->int: return int(dmg*self.crit_mult) if is_crit else dmg
class Character(Human, CritMixin, ABC):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        self.skills: Dict[str, Skill]={}; self._cooldowns: Dict[str,int]={}; self.inventory=[]
        self.weaknesses: List[Element]=[]; self.resists: List[Element]=[]; self.down=False; self.last_element=Element.PHYS
    @abstractmethod
    def basic_attack(self, target:"Character")->Tuple[int,bool,bool]: ...
    @abstractmethod
    def use_skill(self, name: str, allies: List[Character], enemies: List[Character]) -> Tuple[int, bool, bool]:
        def can_cast(self) -> bool:
            from effects import Silence
            return not any(isinstance(e, Silence) for e in self.effects)
    def add_effect(self, eff: Effect): eff.on_apply(self); self.effects.append(eff)
    def tick_effects_start(self):
        for e in list(self.effects): e.on_turn_start(self)
    def tick_effects_end(self):
        for e in list(self.effects): e.on_turn_end(self);
        for e in list(self.effects):
            if e.expired: e.on_expire(self); self.effects.remove(e)
    def receive_damage(self, amount:int, element:Element|None)->int:
        if element is None: element = Element.PHYS
        if self._shield_ratio>0: amount=max(0,int(amount*(1-self._shield_ratio)))
        if element in self.resists: amount=max(0, amount//2)
        if element in self.weaknesses: amount=int(amount*1.5)
        self.hp -= amount; self.last_element=element
        if self.hp<=0: self.down=False
        return amount
    def heal(self, amount:int): self.hp += amount
    def spend_mp(self, cost:int)->bool:
        if self.mp>=cost: self.mp-=cost; return True
        return False
    def reduce_cooldowns(self):
        for k in list(self._cooldowns.keys()): self._cooldowns[k]=max(0,self._cooldowns[k]-1)
    def is_cd(self,name:str)->bool: return self._cooldowns.get(name,0)>0
    def set_cd(self,name:str,cd:int):
        if cd>0: self._cooldowns[name]=cd