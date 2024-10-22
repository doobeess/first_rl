"""Combat logic."""

from __future__ import annotations

import logging
import math
from random import Random

import tcod.ecs  # noqa: TCH002

from game.components import (
    AI,
    HP,
    XP,
    Defense,
    DefenseBonus,
    Graphic,
    MaxHP,
    Name,
    Power,
    PowerBonus,
    Enchantment,
    RewardXP,
    Evasion
)
from game.messages import add_message
from game.tags import Affecting, IsAlive, IsBlocking, IsPlayer

logger = logging.getLogger(__name__)

def get_accuracy(entity: tcod.ecs.Entity) -> float:
    return 1-entity.components[Evasion]


def get_attack(actor: tcod.ecs.Entity) -> int:
    """Get an entities attack power."""
    rng = actor.world[None].components[Random]
    attack_power_range = actor.components.get(Power, (0,0))
    attack_power = rng.randint(attack_power_range[0], attack_power_range[1])

    for e in actor.registry.Q.all_of(components=[PowerBonus], relations=[(Affecting, actor)]):
        try:
            eb = math.ceil(attack_power_range[0]/5)*e.components[Enchantment]
        except KeyError:
            eb = 0
        bonus = rng.randint(e.components[PowerBonus][0]+eb, e.components[PowerBonus][1]+eb)
        attack_power += bonus
    return attack_power


def get_defense(actor: tcod.ecs.Entity) -> int:
    """Get an entities defense power."""
    defense_power = actor.components.get(Defense, 0)
    for e in actor.registry.Q.all_of(components=[DefenseBonus], relations=[(Affecting, actor)]):
        defense_power += e.components[DefenseBonus]
    return defense_power


def melee_damage(attacker: tcod.ecs.Entity, target: tcod.ecs.Entity):
    """Get melee damage for attacking target."""
    rng = attacker.world[None].components[Random]
    damage = max(0, get_attack(attacker) - get_defense(target))
    hit = rng.random() <= get_accuracy(target)
    if hit:
        return damage
    else:
        return None



def apply_damage(entity: tcod.ecs.Entity, damage: int, blame: tcod.ecs.Entity):
    """Deal damage to an entity."""
    entity.components[HP] -= damage
    if entity.components[HP] <= 0:
        die(entity, blame)


def die(entity: tcod.ecs.Entity, blame: tcod.ecs.Entity | None) -> None:
    """Kill an entity."""
    is_player = IsPlayer in entity.tags
    add_message(
        entity.registry,
        text="You died!" if is_player else f"{entity.components[Name]} is dead!",
        fg="player_die" if is_player else "enemy_die",
    )
    if blame:
        blame.components.setdefault(XP, 0)
        blame.components[XP] += entity.components.get(RewardXP, 0)
        add_message(
            entity.registry, f"{blame.components[Name]} gains {entity.components.get(RewardXP, 0)} experience points."
        )

    entity.components[Graphic] = Graphic(ord("%"), (191, 0, 0))
    entity.components[Name] = f"remains of {entity.components[Name]}"
    entity.components.pop(AI, None)
    entity.tags.discard(IsBlocking)
    entity.tags.discard(IsAlive)


def heal(entity: tcod.ecs.Entity, amount: int) -> int:
    """Recover the HP of `entity` by `amount`. Return the actual amount restored."""
    if not (entity.components.keys() >= {HP, MaxHP}):
        logger.info("%r has no HP/MaxHP component", entity)
        return 0
    old_hp = entity.components[HP]
    new_hp = min(old_hp + amount, entity.components[MaxHP])
    entity.components[HP] = min(entity.components[HP] + amount, entity.components[MaxHP])
    return new_hp - old_hp
