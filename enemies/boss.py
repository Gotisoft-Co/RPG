import random
from typing import List, Tuple, Optional
from characters.base import Character
from elements import Element
from skills import Skill
from effects import Shield, Downed
class BossStrategy:
    def decide(self, boss:"Boss", allies:List[Character], enemies:List[Character])->Tuple[str, Optional[Character]]: ...
class AggressiveStrategy(BossStrategy):
    def decide(self,boss,allies,enemies):
        target=min([e for e in enemies if e.is_alive], key=lambda x: x.hp/x.max_hp)
        return ("Огненный шторм" if boss.mp>=12 else "Удар"), target
class DefensiveStrategy(BossStrategy):
    def decide(self,boss,allies,enemies):
        if boss.mp>=10 and not any(type(e).__name__=="Shield" for e in boss.effects): return ("Железная кожа", None)
        target=max([e for e in enemies if e.is_alive], key=lambda x: x.strength)
        return ("Ледяной шип" if boss.mp>=8 else "Удар"), target
class DesperateStrategy(BossStrategy):
    def decide(self,boss,allies,enemies):
        if boss.mp>=14: return ("Гроза", None)
        return ("Удар", random.choice([e for e in enemies if e.is_alive]))
class Boss(Character):
    def __init__(self,name:str):
        super().__init__(name,7,300,80,18,12,16)
        self.skills={
            "Удар":Skill("Удар",Element.PHYS,26),
            "Огненный шторм":Skill("Огненный шторм",Element.FIRE,30,12,cooldown=1,target_all=True),
            "Ледяной шип":Skill("Ледяной шип",Element.ICE,34,8),
            "Гроза":Skill("Гроза",Element.ELEC,28,14,target_all=True),
            "Железная кожа":Skill("Железная кожа",Element.PHYS,0,10,cooldown=2),
        }
        self.weaknesses=[Element.WIND]; self.resists=[Element.FIRE]
        self.strategy: BossStrategy = AggressiveStrategy()
    def basic_attack(self,target:Character):
        base=self.level+self.strength*2; is_crit=self.roll_crit(); dmg=self.apply_crit(base,is_crit); return target.receive_damage(dmg,Element.PHYS),is_crit,False
    def pick_strategy(self):
        hp_pct=self.hp/self.max_hp
        self.strategy = AggressiveStrategy() if hp_pct>0.66 else (DefensiveStrategy() if hp_pct>0.33 else DesperateStrategy())
    def use_skill(self,name:str,allies:List[Character],enemies:List[Character]):
        sk=self.skills[name]
        if self.is_cd(sk.name) or not self.spend_mp(sk.mp_cost): return 0,False,False
        self.set_cd(sk.name, sk.cooldown)
        if name=="Железная кожа": self.add_effect(Shield(0.5,2)); return 0,False,False
        total=0; targets=[e for e in enemies if e.is_alive]
        if not sk.target_all: targets=[random.choice(targets)] if targets else []
        for t in targets:
            dmg=self.strength*2+sk.power
            if sk.element in t.weaknesses: dmg=int(dmg*1.5); t.add_effect(Downed()); t.down=True
            if sk.element in t.resists: dmg=max(0,dmg//2)
            total+=t.receive_damage(dmg, sk.element)
        return total,False,False