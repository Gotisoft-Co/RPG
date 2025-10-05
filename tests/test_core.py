import random
import pytest

from characters.party import Warrior, Mage, Healer, Thief
from enemies.mob import Mob
from elements import Element

def test_basic_attack_damage():
    w = Warrior("Воин")
    m = Mob("Пикси")
    hp0 = m.hp
    dmg, *_ = w.basic_attack(m)
    assert m.hp == hp0 - dmg
    assert dmg > 0

def test_heal_increases_hp():
    h = Healer("Хилер")
    w = Warrior("Воин")
    w.hp -= 30
    assert w.hp < w.max_hp
    # Диa лечит одного:
    total, _, _ = h.use_skill("Диa", [w, h], [Mob("Слизень")])
    assert w.hp <= w.max_hp
    assert total < 0  # отрицательное — суммарное «восстановление»

def test_weakness_triggers_one_more():
    m = Mage("Маг")
    e = Mob("Враг")
    # насильно сделаем врага слабым к огню
    e.weaknesses = [Element.FIRE]
    total, crit, one_more = m.use_skill("Агии", [m], [e])
    assert one_more is True

def test_seed_reproducibility():
    random.seed(123)
    a = [random.randint(1, 100) for _ in range(5)]
    random.seed(123)
    b = [random.randint(1, 100) for _ in range(5)]
    assert a == b