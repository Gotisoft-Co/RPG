from __future__ import annotations
import random
from typing import List, Tuple
from .base import Character
from elements import Element
from skills import Skill
from effects import Downed, Shield, Poison
# Базовые члены пати
class Warrior(Character):
    def __init__(self,name:str):
        super().__init__(name,5,120,20,16,9,6)
        self.skills={"Бросок":Skill("Бросок",Element.PHYS,24),"Защитная стойка":Skill("Защитная стойка",Element.PHYS,0,mp_cost=5,cooldown=3)}
    def basic_attack(self,target:Character)->Tuple[int,bool,bool]:
        base=self.level+self.strength*2; is_crit=self.roll_crit(); dmg=self.apply_crit(base,is_crit); dealt=target.receive_damage(dmg,Element.PHYS); return dealt,is_crit,False
    def use_skill(self,name:str,allies:List[Character],enemies:List[Character]):
        sk=self.skills[name]
        if self.is_cd(sk.name) or not self.spend_mp(sk.mp_cost): return 0,False,False
        self.set_cd(sk.name, sk.cooldown)
        if name=="Бросок":
            target=random.choice([e for e in enemies if e.is_alive]); dmg=self.strength*3+8; is_crit=self.roll_crit(); dmg=self.apply_crit(dmg,is_crit); one=False
            if Element.PHYS in target.weaknesses: target.add_effect(Downed()); target.down=True; one=True
            dealt=target.receive_damage(dmg,Element.PHYS); return dealt,is_crit,one
        if name=="Защитная стойка": self.add_effect(Shield(0.5,2)); return 0,False,False
        return 0,False,False
class Mage(Character):
    def __init__(self,name:str):
        super().__init__(name,5,90,60,6,10,18)
        self.skills={"Агии":Skill("Агии",Element.FIRE,28,8),"Буфу":Skill("Буфу",Element.ICE,26,8),"Зио":Skill("Зио",Element.ELEC,22,8,inflict_shock=True),"Магару":Skill("Магару",Element.WIND,20,10,cooldown=1,target_all=True)}
    def basic_attack(self,target:Character)->Tuple[int,bool,bool]:
        base=self.level+self.intelligence; dealt=target.receive_damage(base,Element.PHYS); return dealt,False,False
    def use_skill(self,name:str,allies:List[Character],enemies:List[Character]):
        sk=self.skills[name]
        if self.is_cd(sk.name) or not self.spend_mp(sk.mp_cost): return 0,False,False
        self.set_cd(sk.name, sk.cooldown)
        total=0; one=False
        targets=[e for e in enemies if e.is_alive];
        if not sk.target_all: targets=[random.choice(targets)] if targets else []
        for t in targets:
            dmg=self.intelligence*2+sk.power
            if sk.element in t.weaknesses: dmg=int(dmg*1.5); t.add_effect(Downed()); t.down=True; one=True
            if sk.element in t.resists: dmg=max(0,dmg//2)
            total+=t.receive_damage(dmg,sk.element)
        return total,False,one
class Healer(Character):
    def __init__(self,name:str):
        super().__init__(name,5,95,70,7,11,17)
        self.skills={"Диa":Skill("Диa",Element.PHYS,0,8),"Патра":Skill("Патра",Element.PHYS,0,5),"Медиара":Skill("Медиара",Element.PHYS,0,16,cooldown=1)}
    def basic_attack(self,target:Character): base=self.level+self.agility; return target.receive_damage(base,Element.PHYS),False,False
    def use_skill(self,name:str,allies:List[Character],enemies:List[Character]):
        sk=self.skills[name]
        if self.is_cd(sk.name) or not self.spend_mp(sk.mp_cost): return 0,False,False
        self.set_cd(sk.name, sk.cooldown)
        if name=="Диa":
            t=min([a for a in allies if a.is_alive], key=lambda x: x.hp/x.max_hp, default=allies[0]); heal=self.intelligence*2+18; t.heal(heal); return -heal,False,False
        if name=="Патра":
            t=random.choice([a for a in allies if a.is_alive]); t.effects=[e for e in t.effects if e.__class__.__name__ not in ("Silence","Downed")]; t.down=False; return 0,False,False
        if name=="Медиара":
            heal_each=self.intelligence+15
            for a in allies:
                if a.is_alive: a.heal(heal_each)
            return -heal_each*len([a for a in allies if a.is_alive]),False,False
        return 0,False,False
class Thief(Character):
    def __init__(self,name:str):
        super().__init__(name,5,85,40,10,18,8)
        self.skills={"Гарула":Skill("Гарула",Element.WIND,22,8),"Ядовитый клинок":Skill("Ядовитый клинок",Element.PHYS,18,6),"Дымовая завеса":Skill("Дымовая завеса",Element.PHYS,0,5,cooldown=2)}
    def basic_attack(self,target:Character):
        base=self.level+self.agility; is_crit=self.roll_crit() or random.random()<0.1; dmg=self.apply_crit(base+self.strength,is_crit); return target.receive_damage(dmg,Element.PHYS),is_crit,False
    def use_skill(self,name:str,allies:List[Character],enemies:List[Character]):
        sk=self.skills[name]
        if self.is_cd(sk.name) or not self.spend_mp(sk.mp_cost): return 0,False,False
        self.set_cd(sk.name, sk.cooldown)
        if name=="Гарула":
            t=random.choice([e for e in enemies if e.is_alive]); dmg=self.agility*2+sk.power; one=False
            if Element.WIND in t.weaknesses: t.add_effect(Downed()); t.down=True; one=True; dmg=int(dmg*1.5)
            return t.receive_damage(dmg,Element.WIND),False,one
        if name=="Ядовитый клинок":
            t=random.choice([e for e in enemies if e.is_alive]); dmg=self.strength*2+sk.power
            if random.random()<0.4: t.add_effect(Poison(5,3))
            return t.receive_damage(dmg,Element.PHYS),False,False
        if name=="Дымовая завеса":
            for a in allies: a.add_effect(Shield(0.35,2))
            return 0,False,False
        return 0,False,False
# Главный герой с системой Персон
from personas import Persona
class Protagonist(Character):
    def __init__(self,name:str, personas: list[Persona]):
        super().__init__(name,5,110,60,12,12,12)
        self.personas = {p.name: p for p in personas}
        self.current_persona: Persona = personas[0]
        self.apply_persona_stats()
        self._switched_this_turn = False
    def apply_persona_stats(self):
        p=self.current_persona
        self.skills = {s.name: s for s in p.skills}
        self.weaknesses = p.weaknesses.copy(); self.resists = p.resists.copy()
    def basic_attack(self,target:Character):
        base=self.level+self.strength
        return target.receive_damage(base,Element.PHYS),False,False
    def switch_persona(self, name:str)->bool:
        if name in self.personas and not self._switched_this_turn:
            self.current_persona = self.personas[name]
            self.apply_persona_stats(); self._switched_this_turn = True
            return True
        return False
    def use_skill(self,name:str,allies:List[Character],enemies:List[Character]):
        # Простое ИИ: если можем ударить в слабость — перед ударом бесплатно сменим персону
        target = min([e for e in enemies if e.is_alive], key=lambda x: x.hp/x.max_hp)
        # авто-переключение ради слабости
        for p in self.personas.values():
            for sk in p.skills:
                if sk.element in target.weaknesses and self.mp>=sk.mp_cost and not self.is_cd(sk.name):
                    self._switched_this_turn=False
                    self.switch_persona(p.name)
                    break
        self._switched_this_turn=False  # сбросим (смена бесплатна в стиле P5)
        if name not in self.skills: return 0,False,False
        sk=self.skills[name]
        if self.is_cd(sk.name) or not self.spend_mp(sk.mp_cost): return 0,False,False
        self.set_cd(sk.name, sk.cooldown)
        total=0; one=False
        targets=[e for e in enemies if e.is_alive]
        if not sk.target_all: targets=[target]
        for t in targets:
            dmg=self.intelligence*2+sk.power
            if sk.element in t.weaknesses: t.add_effect(Downed()); t.down=True; one=True; dmg=int(dmg*1.5)
            if sk.element in t.resists: dmg=max(0,dmg//2)
            total+=t.receive_damage(dmg, sk.element)
        return total,False,one