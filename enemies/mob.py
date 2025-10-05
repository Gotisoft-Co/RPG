import random
from characters.base import Character
from elements import Element
from skills import Skill
class Mob(Character):
    def __init__(self,name:str,level:int=4):
        super().__init__(name,level,70,20,10,10,8)
        self.skills={"Когти":Skill("Когти",Element.PHYS,18),"Пламя":Skill("Пламя",Element.FIRE,16,6)}
        elems=[Element.FIRE,Element.ICE,Element.ELEC,Element.WIND,Element.PHYS]; random.shuffle(elems)
        self.weaknesses=elems[:1]; self.resists=elems[1:3]
    def basic_attack(self,target:Character):
        base=self.level+self.strength; return target.receive_damage(base,Element.PHYS),False,False
    def use_skill(self,name,allies,enemies):
        sk=self.skills[name]
        if self.is_cd(sk.name) or not self.spend_mp(sk.mp_cost): return 0,False,False
        self.set_cd(sk.name, sk.cooldown)
        t=random.choice([e for e in enemies if e.is_alive])
        dmg=self.strength+sk.power
        if sk.element in t.weaknesses: t.add_effect(__import__('effects').effects.Downed()); t.down=True; dmg=int(dmg*1.5)
        return t.receive_damage(dmg, sk.element),False,False