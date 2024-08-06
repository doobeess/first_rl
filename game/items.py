"""Item-based verb behavior."""

from __future__ import annotations

import attrs
from tcod.ecs import Entity  # noqa: TCH002

from game.action import ActionResult, Impossible, Success
from game.components import Name, Position, VisibleTiles
from game.effect import Effect
from game.messages import add_message
from game.spell import Spell
from game.tags import IsActor, IsIn


@attrs.define
class Potion:
    """Drinkable potion."""

    def on_apply(self, actor: Entity, item: Entity) -> ActionResult:
        """Consume the item and apply its effect."""
        add_message(actor.registry, f"""You consume the {item.components.get(Name, "?")}!""")
        if Effect in item.components:
            item.components[Effect].affect(actor)
        item.clear()
        return Success()


@attrs.define
class RandomTargetScroll:
    """One use scroll targeting the nearest enemy."""

    maximum_range: int

    def on_apply(self, actor: Entity, item: Entity) -> ActionResult:
        """Cast items spell at nearest target in range."""
        actor_pos = actor.components[Position]
        possible_targets = actor.registry.Q.all_of(
            components=[Position], tags=[IsActor], relations=[(IsIn, actor_pos.map)]
        ).get_entities() - {actor}

        visible_map = actor_pos.map.components[VisibleTiles]
        visible_targets = [entity for entity in possible_targets if visible_map[entity.components[Position].ij]]
        if not visible_targets:
            return Impossible("No target visible.")

        target = min(visible_targets, key=lambda entity: actor_pos.distance_squared(entity.components[Position]))
        if actor_pos.distance_squared(target.components[Position]) > self.maximum_range**2:
            return Impossible("No target in range.")

        result = item.components[Spell].cast_at_entity(actor, item, target)
        if result:
            item.clear()
        return result
