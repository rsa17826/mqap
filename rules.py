from __future__ import annotations

from rule_builder.rules import Has, HasAll
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


import re

_ENTRANCE_RE = re.compile(r"^entrance\.[a-z]+\d+$")


def set_all_location_rules(world: World) -> None:
  for node in PROG:
    if "receive" not in node:
      continue

    room_id = f"{node['room']['north']}_{node['room']['east']}"

    for itemInfo in node["receive"]:
      if not itemInfo.startswith(("item:", "weapon:", "armor:", "food:", "skill:", "magic:", "permit:", "misc:")):
        continue

      loc_name = f"{room_id} - {itemInfo.split('#')[0]}"
      location = world.get_location(loc_name)

      or_conditions = []
      for and_clause in node.get("requires", []):
        if not and_clause:
          continue
        clean_items = []
        for token in and_clause:
          name = token.split("#")[0]
          if _ENTRANCE_RE.match(name):
            name = f"{room_id} {name}" # qualify to this node's own room
          clean_items.append(name)
        or_conditions.append(HasAll(*clean_items) if len(clean_items) > 1 else Has(clean_items[0]))

      if or_conditions:
        final_rule = or_conditions[0]
        for condition in or_conditions[1:]:
          final_rule = final_rule | condition
        world.set_rule(location, final_rule)


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
  world.set_completion_rule(Has("flag:final boss dead"))
