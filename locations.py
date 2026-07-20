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
          "craft:",
          "quest:",
        )
      ):
        # itemName = itemInfo.split("#")[0]
        itemName = f"{thing['room']['north']}_{thing['room']['east']} - {itemInfo.split('#')[0]}"
        if itemName not in LOCATION_NAME_TO_ID:
          LOCATION_NAME_TO_ID[itemName] = _id_counter
          _id_counter += 1





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
  # return
  for locationName, location_id in LOCATION_NAME_TO_ID.items():
    item_part = locationName.split(" - ")[-1]
    if item_part.startswith("quest:") and not world.options.each_quest_is_a_check:
      continue

    room_id = locationName.split(" - ", 1)[0]

    # item_part = locationName.split(" - ")[-1]
    # if item_part.startswith("quest:") and not world.options.each_quest_is_a_check:
    #   continue
    room_id = locationName.split(" - ", 1)[0]
    region = world.get_region(f"{room_id}: root")
    location = MathQuestLocation(
      world.player,
      locationName,
      location_id,
      region,
    )
    region.locations.append(location)


def create_events(world: World) -> None:
  from ._progression import PROG
  from .items import AREA_MAP
  from .regions import _reqs_to_rule

  newRoomLocations = set()
  for thing in PROG:
    for itemInfo in thing["receive"]:
      if itemInfo.startswith(("quest:", "flag:", "area:", "loot:")):
        if world.options.each_quest_is_a_check and itemInfo.startswith("quest:"):
          continue

        event_name = itemInfo.split("#")[0]
        room_id = f"{thing['room']['north']}_{thing['room']['east']}: root"

        region = world.get_region(room_id)

        _ = region.add_event(
          location_name=f"{room_id} - {event_name}",
          item_name=event_name,
          location_type=MathQuestLocation,
          item_type=items.MathQuestItem,
        )
        if room_id not in newRoomLocations and f"{thing['room']['north']}_{thing['room']['east']}" in AREA_MAP:
          area = AREA_MAP[f"{n}_{e}"]
          powerRule = None
          if not world.options.no_power_reqs and area in AREA_POWER_REQS:
            powerRule = _reqs_to_rule(world, AREA_POWER_REQS[area])

          # TODO add the rule to the event !!!
          newRoomLocations.add(room_id)
          _ = region.add_event(
            location_name=f"{room_id} - new room",
            item_name="flag:room with mobs",
            location_type=MathQuestLocation,
            item_type=items.MathQuestItem,
          )




  print("newRoomLocations", len(newRoomLocations), newRoomLocations)
