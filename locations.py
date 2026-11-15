from __future__ import annotations

import re
from .lib import print

from BaseClasses import ItemClassification, Location
from rule_builder.rules import False_, True_

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
        itemName = f"{thing['room']['north']}_{thing['room']['east']} - {itemInfo}"
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
  # created = 0
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


    # created += 1

  # print("regular:", created)


def create_events(world: World) -> None:
  # events = 0
  from ._progression import PROG
  from .items import AREA_MAP
  from .regions import get_area_power_rule, AREA_POWER_REQS, _reqs_to_rule, expand_area_requirements

  # print(AREA_POWER_REQS)
  newRoomLocations = set()
  for thing in PROG:
    for itemInfo in thing["receive"]:
      if itemInfo.startswith(("quest:", "flag:", "area:", "loot:", "static:")):
        if (False and world.options.each_quest_is_an_item) and itemInfo.startswith("quest:"):
          continue

        event_name = itemInfo.split("#", 1)[0]
        roomPos = f"{thing['room']['north']}_{thing['room']['east']}"
        room_id = f"{roomPos}: root"

        region = world.get_region(room_id)
        new_requires = []
        finalRule = True_()
        if roomPos != "-1_-1":
          newRule = get_area_power_rule(world, roomPos)

          if newRule is not None:
            finalRule &= newRule


        newRequires = expand_area_requirements(thing["requires"])
        # if roomPos == "9_22":
        #   print(newRequires)

        aa = _reqs_to_rule(world, newRequires)
        assert aa is not None, [thing["requires"], newRequires]
        assert finalRule is not None, [thing["requires"], newRequires]
        finalRule &= aa

        # print("\n\n", area, _and, AREA_POWER_REQS[area], thing["requires"], powerReqs, newAnd)
        # raise "ASd"

        _ = region.add_event(
          location_name=f"{room_id} - {event_name}",
          item_name=event_name,
          location_type=MathQuestLocation,
          item_type=items.MathQuestItem,
          rule=finalRule,
        )
        if room_id not in newRoomLocations and roomPos in AREA_MAP:
          newRoomLocations.add(room_id)
          roomRule = True_()
          if roomPos != "-1_-1":
            powerRule = get_area_power_rule(world, roomPos)
            if powerRule is not None:
              roomRule &= powerRule


          _ = region.add_event(
            location_name=f"{room_id} - new room",
            item_name="flag:room with mobs",
            location_type=MathQuestLocation,
            item_type=items.MathQuestItem,
            rule=roomRule,
          )





          # events += 1

  # print("events:", events)

  # print("newRoomLocations", len(newRoomLocations), newRoomLocations)
