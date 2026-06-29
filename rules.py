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


def set_all_location_rules(world: World) -> None:
  for node in PROG:
    if "receive" not in node:
      continue

    for itemInfo in node["receive"]:
      # Match the exact location string format from locations.py
      if not itemInfo.startswith(("item:", "weapon:", "armor:", "food:", "skill:", "magic:", "permit:", "misc:")):
        continue

      loc_name = f"{node['room']['north']}_{node['room']['east']} - {itemInfo.split('#')[0]}"

      location = world.get_location(loc_name)

      # Build the Archipelago rule dynamically from the nested list
      # Inner lists represent "AND" conditions, outer blocks represent "OR" paths
      or_conditions: list[HasAll[World]] = []
      for and_clause in node.get("requires", []):
        if not and_clause: # It's [[]], meaning it's un-locked/free from the start
          continue

        # Strip item ID counts like #1 or #999 to match actual clean pool item names
        clean_items = [item.split("#")[0] for item in and_clause]
        or_conditions.append(HasAll(*clean_items))

      # If there are actual constraints, chain them together with OR (|) operators
      if len(or_conditions):
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
