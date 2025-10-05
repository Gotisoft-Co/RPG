from dataclasses import dataclass
@dataclass
class Item:
    name: str; description: str
    def use(self, user, target)->str: return "Ничего не произошло."
class Potion(Item):
    def __init__(self): super().__init__("Зелье", "Восстанавливает 40 HP")
    def use(self, user, target): target.heal(40); return f"{user.name} даёт {target.name} зелье (+40 HP)."
class Ether(Item):
    def __init__(self): super().__init__("Эфир", "Восстанавливает 20 MP")
    def use(self, user, target): target.mp += 20; return f"{user.name} даёт {target.name} эфир (+20 MP)."