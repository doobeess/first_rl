"""World initialization."""

from __future__ import annotations

from random import Random

import tcod.ecs

import game.actor_tools
import game.procgen
from game.components import (
    HP,
    MaxHP,
    Nutrition,
    MaxNutrition,
    Defense,
    DefenseBonus,
    EquipSlot,
    Graphic,
    Name,
    Position,
    Power,
    PowerBonus,
    RewardXP,
    SpawnWeight,
    Evasion,
    Enchantment,
)
from game.effect import Effect
from game.effects import Healing, AddNutrition
from game.item import ApplyAction
from game.item_tools import equip_item
from game.items import Potion, Food, RandomTargetScroll, TargetScroll
from game.map_tools import get_map
from game.messages import MessageLog, add_message
from game.spell import EntitySpell, PositionSpell
from game.spells import Fireball, LightningBolt
from game.tags import IsActor, IsIn, IsItem, NotStackable, IsPlayer


def new_world() -> tcod.ecs.Registry:
    """Return a new world."""
    world = tcod.ecs.Registry()
    world[None].components[Random] = Random()
    world[None].components[MessageLog] = MessageLog()

    init_creatures(world)
    init_items(world)

    map_ = get_map(world, game.procgen.Tombs(1))

    (start,) = world.Q.all_of(tags=["UpStairs"], relations=[(IsIn, map_)])

    player = game.actor_tools.spawn_actor(world["player"], start.components[Position])
    player.tags.add(IsPlayer)
    equip_item(player, world["dagger"].instantiate())
    equip_item(player, world["leather_armor"].instantiate())

    game.actor_tools.update_fov(player)

    add_message(world, "Hello and welcome, adventurer, to yet another dungeon!", "welcome_text")
    return world


def init_new_creature(
    world: tcod.ecs.Registry,
    name: str,
    ch: int,
    fg: tuple[int, int, int],
    hp: int,
    power: tuple[int,int],
    defense: int,
    evasion: float,
    xp: int,
    spawn_weight: tuple[tuple[int, int], ...] = (),
) -> None:
    """Setup a new creature type."""
    race = world[name]
    race.tags.add(IsActor)
    race.components[Name] = name
    race.components[Graphic] = Graphic(ch, fg)
    race.components[HP] = race.components[MaxHP] = hp
    race.components[Power] = power
    race.components[Defense] = defense
    race.components[Evasion] = evasion
    race.components[RewardXP] = xp
    if name == "player":
        race.components[Nutrition] = race.components[MaxNutrition] = 500
    if spawn_weight:
        race.components[SpawnWeight] = spawn_weight


def init_creatures(world: tcod.ecs.Registry) -> None:
    """Initialize monster database."""
    init_new_creature(world, name="player", ch=ord("@"), fg=(255, 255, 255), hp=100, power=(5,7), defense=1, evasion=.3, xp=0)
    init_new_creature(
        world,
        name="orc",
        ch=ord("o"),
        fg=(63, 127, 63),
        hp=30,
        power=(5,10),
        defense=0,
        evasion=.3,
        xp=35,
        spawn_weight=((1, 100),)
    )
    init_new_creature(
        world,
        name="troll",
        ch=ord("T"),
        fg=(0, 127, 0),
        hp=50,
        power=(20,30),
        defense=1,
        evasion=.1,
        xp=100,
        spawn_weight=((3, 15), (5, 30), (7, 60)),
    )
    init_new_creature(
        world,
        name="bat",
        ch=ord("B"),
        fg=(30,30,30),
        hp=15,
        power=(3,10),
        defense=0,
        evasion=.7,
        xp=1,
        spawn_weight=((1,100),)
    )



def init_items(world: tcod.ecs.Registry) -> None:
    """Initialize item database."""
    entity = world["food_ration"]
    entity.tags.add(IsItem)
    entity.components[Name] = "food ration"
    entity.components[Graphic] = Graphic(ord(":"), (115, 76, 31))
    entity.components[Effect] = AddNutrition(300)
    entity.components[ApplyAction] = Food()
    entity.components[SpawnWeight] = ((1,10),)

    entity = world["health_potion"]
    entity.tags.add(IsItem)
    entity.components[Name] = "Health Potion"
    entity.components[Graphic] = Graphic(ord("!"), (127, 0, 255))
    entity.components[Effect] = Healing(15)
    entity.components[ApplyAction] = Potion()
    entity.components[SpawnWeight] = ((1, 35),)

    entity = world["lightning_scroll"]
    entity.tags.add(IsItem)
    entity.components[Name] = "Lightning Scroll"
    entity.components[Graphic] = Graphic(ord("~"), (255, 255, 0))
    entity.components[ApplyAction] = RandomTargetScroll(maximum_range=5)
    entity.components[EntitySpell] = LightningBolt(damage=20)
    entity.components[SpawnWeight] = ((3, 25),)

    entity = world["fireball_scroll"]
    entity.tags.add(IsItem)
    entity.components[Name] = "Fireball Scroll"
    entity.components[Graphic] = Graphic(ord("~"), (255, 0, 0))
    entity.components[ApplyAction] = TargetScroll()
    entity.components[PositionSpell] = Fireball(damage=12, radius=3)
    entity.components[SpawnWeight] = ((6, 25),)

    entity = world["dagger"]
    entity.tags.add(IsItem)
    entity.components[Name] = "Dagger"
    entity.components[Graphic] = Graphic(ord("/"), (0, 191, 255))
    entity.components[PowerBonus] = (5,20)
    entity.components[SpawnWeight] = ((2,5),)
    entity.components[EquipSlot] = "weapon"
    entity.tags.add(NotStackable)

    entity = world["sword"]
    entity.tags.add(IsItem)
    entity.components[Name] = "Sword"
    entity.components[Graphic] = Graphic(ord("/"), (0, 191, 255))
    entity.components[PowerBonus] = (10,30)
    entity.components[SpawnWeight] = ((4, 5),)
    entity.components[EquipSlot] = "weapon"
    entity.tags.add(NotStackable)

    entity = world["leather_armor"]
    entity.tags.add(IsItem)
    entity.components[Name] = "Leather Armor"
    entity.components[Graphic] = Graphic(ord("["), (139, 69, 19))
    entity.components[DefenseBonus] = 5
    entity.components[EquipSlot] = "armor"
    entity.components[SpawnWeight] = ((2, 5),)
    entity.tags.add(NotStackable)

    entity = world["chain_mail"]
    entity.tags.add(IsItem)
    entity.components[Name] = "Chain Mail"
    entity.components[Graphic] = Graphic(ord("["), (139, 69, 19))
    entity.components[DefenseBonus] = 10
    entity.components[SpawnWeight] = ((6, 15),)
    entity.components[EquipSlot] = "armor"
    entity.tags.add(NotStackable)
