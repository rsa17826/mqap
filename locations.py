from __future__ import annotations

import re

from BaseClasses import ItemClassification, Location

from worlds.AutoWorld import World

from . import items
from ._progression import PROG

# Every location must have a unique integer ID associated with it.
# We will have a lookup from location name to ID here that, in world.py, we will import and bind to the world class.
# Even if a location doesn't exist on specific options, it must be present in this lookup.

LOCATION_NAME_TO_ID: dict[str, int] = {}
# from .room_geometry import GEOM

_id_counter = 1
for thing in PROG:
  if "receive" in thing:
    for itemInfo in thing["receive"]:
      if itemInfo.startswith(
        (
          "item:",
          "weapon:",
          "armor:",
          "food:",
          "skill:",
          "magic:",
          "permit:",
          "misc:",
        )
      ):
        # itemName = itemInfo.split("#")[0]
        itemName = f"{thing['room']['north']}_{thing['room']['east']} - {itemInfo.split('#')[0]}"
        if itemName not in LOCATION_NAME_TO_ID:
          LOCATION_NAME_TO_ID[itemName] = _id_counter
          _id_counter += 1

# temp: set[str] = set()
# i = 0
# for room in GEOM:
#   _id = f'{room["north"]}_{room["east"]}'
#   if _id not in temp:
#     temp.add(_id)
#     LOCATION_NAME_TO_ID[_id] = i
#     i += 1


# Each Location instance must correctly report the "game" it belongs to.
# To make this simple, it is common practice to subclass the basic Location class and override the "game" field.
class MathQuestLocation(Location):
  game: str = "MathQuest"


# Let's make one more helper method before we begin actually creating locations.
# Later on in the code, we'll want specific subsections of LOCATION_NAME_TO_ID.
# To reduce the chance of copy-paste errors writing something like {"Chest": LOCATION_NAME_TO_ID["Chest"]},
# let's make a helper method that takes a list of location names and returns them as a dict with their IDs.
# Note: There is a minor typing quirk here. Some functions want location addresses to be an "int | None",
# so while our function here only ever returns dict[str, int], we annotate it as dict[str, int | None].
def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
  return {location_name: LOCATION_NAME_TO_ID[location_name] for location_name in location_names}


def create_all_locations(world: World) -> None:
  create_regular_locations(world)
  create_events(world)


def create_regular_locations(world: World) -> None:
  for itemName, location_id in LOCATION_NAME_TO_ID.items():
    room_id = itemName.split(" - ", 1)[0]
    region = world.get_region(room_id)
    location = MathQuestLocation(
      world.player,
      itemName,
      location_id,
      region,
    )
    region.locations.append(location)


def create_events(world: World) -> None:
  from ._progression import PROG

  for thing in PROG:
    if "receive" not in thing:
      continue
    for itemInfo in thing["receive"]:
      if itemInfo.startswith(("quest:", "flag:", "area:")):
        event_name = itemInfo.split("#")[0]
        room_id = f"{thing['room']['north']}_{thing['room']['east']}"

        region = world.get_region(room_id)

        _ = region.add_event(
          location_name=f"{room_id} - {event_name}",
          item_name=event_name,
          location_type=MathQuestLocation,
          item_type=items.MathQuestItem,
        )


# def create_events(world: World) -> None:
#   from ._progression import PROG

#   for thing in PROG:
#     if "receive" in thing:
#       for itemInfo in thing["receive"]:
#         # Identify non-physical items like quests
#         if itemInfo.startswith(("quest:", "flag:", "location.")):
#           event_name = itemInfo.split("#")[0]
#           room_id = f"{thing['room']['north']}_{thing['room']['east']}"

#           # Get the room region where this event happens
#           region = world.get_region(room_id)

#           # Create an Event Location and lock the Event Item to it automatically
#           _ = region.add_event(
#             location_name=f"{room_id} - {event_name}",
#             item_name=event_name,
#             location_type=MathQuestLocation,
#             item_type=items.MathQuestItem,
#           )

# Sometimes, the player may perform in-game actions that allow them to progress which are not related to Items.
# In our case, the player must press a button in the top left room to open the final boss door.
# AP has something for this purpose: "Event locations" and "Event items".
# An event location is no different than a regular location, except it has the address "None".
# It is treated during generation like any other location, but then it is discarded.
# This location cannot be "sent" and its item cannot be "received", but the item can be used in logic rules.
# Since we are creating more locations and adding them to regions, we need to grab those regions again first.
# top_left_room = world.get_region("Top Left Room")
# final_boss_room = world.get_region("Final Boss Room")

# # One way to create an event is simply to use one of the normal methods of creating a location.
# button_in_top_left_room = MathQuestLocation(
#   world.player, "Top Left Room Button", None, top_left_room
# )
# top_left_room.locations.append(button_in_top_left_room)

# We then need to put an event item onto the location.
# An event item is an item whose code is "None" (same as the event location's address),
# and whose classification is "progression". Item creation will be discussed more in items.py.
# Note: Usually, items are created in world.create_items(), which for us happens in items.py.
# However, when the location of an item is known ahead of time (as is the case with an event location/item pair),
# it is common practice to create the item when creating the location.
# Since locations also have to be finalized after world.create_regions(), which runs before world.create_items(),
# we'll create both the event location and the event item in our locations.py code.
# button_item = items.MathQuestItem(
#   "Top Left Room Button Pressed",
#   ItemClassification.progression,
#   None,
#   world.player,
# )
# button_in_top_left_room.place_locked_item(button_item)

# # A way simpler way to do create an event location/item pair is by using the region.create_event helper.
# # Luckily, we have another event we want to create: The Victory event.
# # We will use this event to track whether the player can win the game.
# # The Victory event is a completely optional abstraction - This will be discussed more in set_rules().
# _ = final_boss_room.add_event(
#   "Final Boss Defeated",
#   "Victory",
#   location_type=MathQuestLocation,
#   item_type=items.MathQuestItem,
# )

# If you create all your regions and locations line-by-line like this,
# the length of your create_regions might get out of hand.
# Many worlds use more data-driven approaches using dataclasses or NamedTuples.
# However, it is worth understanding how the actual creation of regions and locations works,
# That way, we're not just mindlessly copy-pasting! :)
