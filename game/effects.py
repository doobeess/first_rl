"""A collection of effects."""

from __future__ import annotations

import attrs
from tcod.ecs import Entity  # noqa: TCH002

from game.combat import heal
from game.components import Name, Nutrition, MaxNutrition
from game.messages import add_message


@attrs.define
class Healing:
    """Healing effect."""

    amount: int

    def affect(self, entity: Entity) -> None:
        """Heal the target."""
        if amount := heal(entity, self.amount):
            add_message(
                entity.registry, f"""{entity.components.get(Name, "?")} recovers {amount} HP.""", fg="health_recovered"
            )

@attrs.define
class AddNutrition:
    """Nutrition effect."""

    amount: int

    def affect(self, entity: Entity) -> None:
        entity.components[Nutrition] = min(entity.components[Nutrition]+self.amount, entity.components[MaxNutrition])
