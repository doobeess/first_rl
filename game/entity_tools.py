"""Generic entity functions."""

from __future__ import annotations

from tcod.ecs import Entity  # noqa: TCH002

from game.components import Count, Name, Enchantment
from game.tags import EquippedBy


def get_name(entity: Entity) -> str:
    """Return the name of a generic entity."""
    return entity.components.get(Name, "???")


def get_desc(entity: Entity) -> str:
    """Return a description of an entity."""
    name = ""
    try:
        if entity.components[Enchantment] != 0:
            name += f"{'+' if entity.components[Enchantment] > 0 else ''}{entity.components[Enchantment]} "
    except KeyError:
        pass
    name += get_name(entity)
    if entity.components.get(Count, 1) != 1:
        name = f"{entity.components[Count]}x {name}"
    if EquippedBy in entity.relation_tag:
        name += " (E)"
    return name
