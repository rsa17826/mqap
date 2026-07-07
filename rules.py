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
from .items import HAS_LIST


def set_all_location_rules(world: World) -> None:
  for node in PROG:
    if "receive" not in node:
      continue

    room_id_base = f"{node['room']['north']}_{node['room']['east']}"

    for itemInfo in node["receive"]:
      clean_item = itemInfo.split("#")[0]

      # 1. Handle the naming difference between events and standard locations
      if clean_item.startswith(("loot:")):
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
          if tname in HAS_LIST:
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


# def set_all_location_rules(world: World) -> None:
#   """
#   Dynamically applies progression rules to locations and events.
#   """
#   for node in PROG:
#     requires = node.get("requires", [])
#     if not requires or any(not and_list for and_list in requires):
#       continue

#     # Compile the logical DNF conditions ([[]] -> OR inside AND)
#     or_rule = None
#     for and_list in requires:
#       and_rule = None
#       for req in and_list:
#         current_rule = Has(req)
#         and_rule = current_rule if and_rule is None else and_rule & current_rule
#       or_rule = and_rule if or_rule is None else or_rule | and_rule

#     if or_rule is not None:
#       room_prefix = f"{node['room']['north']}_{node['room']['east']}"
#       for item in node.get("receive", []):
#         # Format matches the event location format we defined during region setup
#         target_name = f"{room_prefix} - {item}"

#         try:
#           target = world.get_location(target_name)
#           world.set_rule(target, or_rule)
#         except Exception:
#           try:
#             target = world.get_entrance(item)
#             world.set_rule(target, or_rule)
#           except Exception:
#             pass

#         # If the target exists as a valid registered location or entrance, apply the rule
#         # if target is not None:
#         #   world.set_rule(target, or_rule)


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
