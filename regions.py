from __future__ import annotations

from BaseClasses import Entrance, Region
from worlds.AutoWorld import World

# A region is a container for locations ("checks"), which connects to other regions via "Entrance" objects.
# Many games will model their Regions after physical in-game places, but you can also have more abstract regions.
# For a location to be in logic, its containing region must be reachable.
# The Entrances connecting regions can have rules - more on that in rules.py.
# This makes regions especially useful for traversal logic ("Can the player reach this part of the map?")

# Every location must be inside a region, and you must have at least one region.
# This is why we create regions first, and then later we create the locations (in locations.py).


def create_and_connect_regions(world: World) -> None:
  create_all_regions(world)
  connect_regions(world)


def create_all_regions(world: World) -> None:
  from .room_geometry import GEOM

  temp: set[str] = set()
  for room in GEOM:
    _id = f'{room["north"]}_{room["east"]}'
    if _id not in temp:
      temp.add(_id)
      region = Region(
        _id,
        world.player,
        world.multiworld,
      )
      world.multiworld.regions.append(region)
  # Creating a region is as simple as calling the constructor of the Region class.

  # Some regions may only exist if the player enables certain options.
  # In our case, the Hammer locks the top middle chest in its own room if the hammer option is enabled.
  # if world.options.hammer:
  #   top_middle_room = Region("Top Middle Room", world.player, world.multiworld)
  #   regions.append(top_middle_room)


def connect_regions(world: World) -> None:
  from .room_geometry import GEOM

  # We have regions now, but still need to connect them to each other.
  # But wait, we no longer have access to the region variables we created in create_all_regions()!
  # Luckily, once you've submitted your regions to multiworld.regions,
  # you can get them at any time using world.get_region(...).

  # Okay, now we can get connecting. For this, we need to create Entrances.
  # Entrances are inherently one-way, but crucially, AP assumes you can always return to the origin region.
  # One way to create an Entrance is by calling the Entrance constructor.

  for room in GEOM:
    cur = world.get_region(f'{room["north"]}_{room["east"]}')

    for _dir in ("north", "south", "east", "west"):
      # 1. Determine the exact coordinates of the adjacent room based on the direction
      target_north = room["north"]
      target_east = room["east"]
      _id = f'{room["north"]}_{room["east"]}'
      if _id in ("100_100", "300_300"):
        continue
      if _dir == "north":
        target_north += 1
      elif _dir == "south":
        target_north -= 1
      elif _dir == "east":
        target_east += 1
      elif _dir == "west":
        target_east -= 1

      target_name = f"{target_north}_{target_east}"
      # print(target_name, _dir, room)

      # 2. Iterate through the exits if they exist in this direction
      i = 0
      for _exit in room["exits"][_dir]:
        # Build a unique identifier for this entrance
        entrance_name = f"Exit from {_id} {_dir}.{i}"

        entrance = Entrance(
          world.player,
          entrance_name,
          parent=cur,
        )
        cur.exits.append(entrance)

        # 3. Securely connect to the correct calculated adjacent room
        target_region = world.get_region(target_name)
        entrance.connect(target_region)
        i += 1

  # You can then connect the Entrance to the target region.
  # overworld_to_bottom_right_room.connect(bottom_right_room)

  # An even easier way is to use the region.connect helper.
  # _ = overworld.connect(right_room, "Overworld to Right Room")
  # _ = right_room.connect(final_boss_room, "Right Room to Final Boss Room")

  # The region.connect helper even allows adding a rule immediately.
  # We'll talk more about rule creation in the set_all_rules() function in rules.py.
  # _ = overworld.connect(
  #   top_left_room,
  #   "Overworld to Top Left Room",
  #   lambda state: state.has("Key", world.player),
  # )

  # Some Entrances may only exist if the player enables certain options.
  # In our case, the Hammer locks the top middle chest in its own room if the hammer option is enabled.
  # In this case, we previously created an extra "Top Middle Room" region that we now need to connect to Overworld.
  # if world.options.hammer:
  #   top_middle_room = world.get_region("Top Middle Room")
  #   overworld.connect(top_middle_room, "Overworld to Top Middle Room")
