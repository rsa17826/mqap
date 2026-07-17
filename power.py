import dataclasses
from dataclasses import dataclass
from typing import override

from BaseClasses import CollectionState
from rule_builder.rules import Rule

from worlds.AutoWorld import World


@dataclass(frozen=True)
class PowerData:
  power: int = 0
  power_group: str | None = None # e.g. "weapon", "shield" — exclusive slots


import re


from ._power import POWER_TABLE as aPOWER_TABLE

# POWER_TABLE: dict[str, PowerData] = {
#   "quest:curse.9": PowerData(power=10, power_group="weapon"),
#   "Steel Sword": PowerData(power=3, power_group="weapon"),
#   "Fire Sword": PowerData(power=5, power_group="weapon"),
#   "Wooden Shield": PowerData(power=1, power_group="shield"),
#   "Steel Shield": PowerData(power=3, power_group="shield"),
#   "Ring of Power": PowerData(power=2, power_group=None), # stacks
# }
POWER_TABLE = {}
# Precompute for the rule's item_dependencies + fast lookup
POWER_GROUP_ITEMS: dict[str, list[str]] = {}
UNGROUPED_POWER_ITEMS: list[str] = []
for name, _data in aPOWER_TABLE.items():
  g = re.match(r"(\w+):(\w+)", name)
  assert g is not None
  power_group = g[1] if g[1] in ("weapon", "armor") else None
  power = int(_data[0].get("power", 0))
  if power_group == "armor":
    power *= 0.8

  _data = PowerData(power=int(power), power_group=power_group)
  POWER_TABLE[name] = _data
  if _data.power <= 0:
    continue

  if _data.power_group is None:
    UNGROUPED_POWER_ITEMS.append(name)
  else:
    POWER_GROUP_ITEMS.setdefault(_data.power_group, []).append(name)


@dataclasses.dataclass()
class HasPower(Rule[World], game="MathQuest"):
  """Checks that the player's effective power level (max-per-exclusive-group + stacking items) meets a threshold"""

  min_power: int

  @override
  def _instantiate(self, world: World) -> Rule.Resolved:
    return self.Resolved(
      min_power=self.min_power,
      player=world.player,
      caching_enabled=getattr(world, "rule_caching_enabled", False),
    )

  class Resolved(Rule.Resolved):
    min_power: int

    @override
    def _evaluate(self, state: CollectionState) -> bool:
      prog_items = state.prog_items[self.player]
      total = 0
      for name in UNGROUPED_POWER_ITEMS:
        if prog_items[name]:
          total += POWER_TABLE[name].power


      for names in POWER_GROUP_ITEMS.values():
        best = 0
        for name in names:
          if prog_items[name]:
            best = max(best, POWER_TABLE[name].power)


        total += best

      return total >= self.min_power

    @override
    def item_dependencies(self) -> dict[str, set[int]]:
      # every powered item can affect this rule's result — needed for cache invalidation
      deps: dict[str, set[int]] = {name: {id(self)} for name in UNGROUPED_POWER_ITEMS}
      for names in POWER_GROUP_ITEMS.values():
        for name in names:
          deps.setdefault(name, set()).add(id(self))


      return deps

    @override
    def __str__(self) -> str:
      return f"HasPower({self.min_power})"


