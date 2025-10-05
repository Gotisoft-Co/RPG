import random
from utils import ascii_header, draw_corridor
from enemies import Mob
from battle import Battle
def random_mob_pack(n:int):
    names=["Теневой слизень","Маска-гном","Летучая гарпия","Темный пикси"]
    return [Mob(random.choice(names)) for _ in range(n)]

def corridor_run(party, battles:int=3)->bool:
    ascii_header("Коридор к боссу"); pos=0; boss_at=battles
    for i in range(battles):
        draw_corridor(pos,boss_at,boss_at)
        pack=random_mob_pack(random.randint(2,3))
        if not Battle(party, pack, name=f"Стычка {i+1}").run(): return False
        pos+=1
    draw_corridor(pos,boss_at,boss_at); return True