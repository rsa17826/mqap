from __future__ import annotations

import re
from functools import reduce

from rule_builder.rules import Has, HasAll, Rule, True_

from worlds.AutoWorld import World

from ._progression import PROG


def set_all_rules(world: World) -> None:
  """
  Main entry point to set all rules for the world.
  """
  set_all_entrance_rules(world)
  set_all_location_rules(world)
  set_completion_condition(world)


def set_all_entrance_rules(_world: World) -> None:
  """
  Set explicit rules for entrances if applicable.
  Static transitions not covered by progression nodes can be manually defined here.
  """
  pass


_ENTRANCE_RE = re.compile(r"^entrance\.[a-z]+\d+$")
from .items import ARMOR_ORDER, HAS_LIST, WEAPON_ORDER, MAGIC_ORDER
from .power import HasPower

_POWER_RE = re.compile(r"^power:(\d+)$")


def set_all_location_rules(world: World) -> None:
  for node in PROG:
    if "receive" not in node:
      continue

    room_id_base = f"{node['room']['north']}_{node['room']['east']}"

    for itemInfo in node["receive"]:
      clean_item = itemInfo.split("#")[0]

      # 1. Handle the naming difference between events and standard locations
      if clean_item.startswith(("power:")):
        continue

      if clean_item.startswith(("quest:", "flag:", "area:", "loot:")) and not (
        world.options.each_quest_is_a_check and clean_item.startswith("quest:")
      ):
        loc_name = f"{room_id_base}: root - {clean_item}"
      else:
        loc_name = f"{room_id_base} - {clean_item}"

      location = world.get_location(loc_name)

      # 2. Build and apply the rules
      requires = node.get("requires", [])

      # `requires` is a DNF: a list of OR'd alternatives, where each alternative is a list of
      # items that must ALL be held. If ANY alternative is empty, that OR-branch needs nothing
      # at all, so the whole location is unconditionally reachable and no rule should be set
      # (mirrors regions.py's _reqs_to_rule: `if any(len(option) == 0 ...): return None`).
      if any(len(_and) == 0 for _and in requires):
        continue

      allConditions: list[Rule[World]] = []
      for _and in requires:
        clean_items: list[str] = []
        for token in _and:
          name = token
          if _ENTRANCE_RE.match(name):
            name = f"{room_id_base} - {name}"

          clean_items.append(name)

        sub_rule: Rule | None = None
        for item in clean_items:
          tname = item.split("#", 1)[0]
          power_match = _POWER_RE.match(item)
          if power_match:
            temprule = HasPower(int(power_match.group(1)))
          elif world.options.progressive_magic and tname in MAGIC_ORDER:
            # With progressive_weapons on, the actual item received is the generic
            # "weapon:progressive weapons" item, not the named weapon. Reaching this
            # weapon's logic requires having collected at least this many of them.
            temprule = Has("magic:progressive magic", MAGIC_ORDER[tname])
          elif world.options.progressive_armor and tname in ARMOR_ORDER:
            # With progressive_weapons on, the actual item received is the generic
            # "weapon:progressive weapons" item, not the named weapon. Reaching this
            # weapon's logic requires having collected at least this many of them.
            temprule = Has("armor:progressive armor", ARMOR_ORDER[tname])
          elif world.options.progressive_weapons and tname in WEAPON_ORDER:
            # With progressive_weapons on, the actual item received is the generic
            # "weapon:progressive weapons" item, not the named weapon. Reaching this
            # weapon's logic requires having collected at least this many of them.
            temprule = Has("weapon:progressive weapons", WEAPON_ORDER[tname])
          elif tname in HAS_LIST:
            temprule = HAS_LIST[tname]
          else:
            temprule = Has(item)

          if sub_rule is None:
            sub_rule = temprule
          else:
            sub_rule = sub_rule & temprule # AND within a single requirement group


        assert sub_rule is not None
        allConditions.append(sub_rule)

        # allConditions.append(HasAll(*clean_items) if len(clean_items) > 1 else Has(clean_items[0]))

      if allConditions:
        # print(allConditions, "allConditions")
        # print(HAS_LIST, "HAS_LIST")
        world.set_rule(location, reduce(lambda a, s: a | s, allConditions)) # OR across alternative groups




def set_completion_condition(world: World) -> None:
  """
  Defines the ultimate victory condition for the player to clear the multiworld.
  """
  rule = True_()
  if world.options.final_boss:
    rule &= Has("flag:final boss dead")

  if world.options.all_quests_maxed:
    from .items import maxQuests

    rule &= HasAll(*(f"quest:{name}.{value}" for name, value in maxQuests.items()))

  world.set_completion_rule(rule)
