from __future__ import annotations

from BaseClasses import Entrance, Region
from rule_builder.rules import Has, HasAll, Rule

from worlds.AutoWorld import World

from . import items, locations
from ._room_geometry import ExitBase


def create_and_connect_regions(world: World) -> None:
  create_all_regions(world)


def _reqs_to_rule(reqs: list[list[str]]) -> Rule | None:
  # reqs is an OR of AND-lists, same shape as the "requires" field elsewhere.
  # An empty inner list ([]) means "no requirement" -> this node is unconditional.
  if any(len(option) == 0 for option in reqs):
    return None
  rule: Rule | None = None
  for option in reqs:
    sub_rule: Rule = HasAll(*option) if len(option) > 1 else Has(option[0])
    rule = sub_rule if rule is None else (rule | sub_rule)
  return rule


connections = {}


def create_all_regions(world: World) -> None:
  from ._room_geometry import GEOM

  createRegion(20, 20, world, GEOM)

  def createRegion(north: int, east: int):
    def connect(x: str, y: str):
      entrance = Entrance(world.player, x, parent=world.get_region(x))
      world.get_region(x).exits.append(entrance)
      entrance.connect(world.get_region(y))

    for room in GEOM:
      if room["north"] == north and room["east"] == east:
        roomId = f"{room['north']}_{room['east']}"
        if "areas" not in room:
          continue
        for i, areaSection in enumerate(room["areas"]):
          for connectedAreas in areaSection["areas"]:
            for area in connectedAreas:
              print(area, "areaSection", areaSection)
              side = area["side"]
              sideIdx = area["idx"]
              entranceId = f"{roomId}: {side} {sideIdx}"
              connections[entranceId] = Region(entranceId, world.player, world.multiworld)
              print(entranceId)
        newRegion = createRegion(north + 1, east)
        if newRegion is not None:
          connect(region, newRegion)
        newRegion = createRegion(north, east + 1)
        if newRegion is not None:
          connect(region, newRegion)
        newRegion = createRegion(north - 1, east)
        if newRegion is not None:
          connect(region, newRegion)
        newRegion = createRegion(north, east - 1)
        if newRegion is not None:
          connect(region, newRegion)
        break

  # if roomId in seen:
  #   continue
  # seen.add(roomId)

  # region = Region(roomId, world.player, world.multiworld)
  # world.multiworld.regions.append(region)

  # if "areas" not in room:
  #   continue

  # # One sub-region per exit slot referenced anywhere in "areas".
  # slot_ids: set[str] = set()
  # for area_node in room["areas"]:
  #   for group in area_node["areas"]:
  #     for slot in group:
  #       slot_ids.add(_slot_id(slot["side"], slot["idx"]))

  # for slot_id in slot_ids:
  #   slot_region = Region(f"{roomId}#{slot_id}", world.player, world.multiworld)
  #   world.multiworld.regions.append(slot_region)


def connect_doors(world: World) -> None:
  return
  from ._exits import EXITS

  # Doors (stairs, drains, warp rings, etc.) are point-to-point teleports that
  # aren't part of the directional grid or the "areas" slot system. Like
  # locations, we don't know which sub-area a trigger object sits behind, so
  # they connect from/to each room's base region, same place locations live.
  for door in EXITS["doors"]:
    origin_id = f"{door['origin']['north']}_{door['origin']['east']}"
    dest_id = f"{door['dest']['north']}_{door['dest']['east']}"

    origin_region = world.get_region(origin_id)
    dest_region = world.get_region(dest_id)

    entrance_name = f"Door {door['id']}"
    entrance = Entrance(world.player, entrance_name, parent=origin_region)
    origin_region.exits.append(entrance)
    entrance.connect(dest_region)

    # Reverse doors are listed as their own separate entry in EXITS["doors"]
    # (e.g. "door:stairsDown:21_21_20_21" alongside "door:stairsDown:20_21_21_21"),
    # so we never add a return connection here ourselves -- a door explicitly
    # marked one_way (no matching reverse entry in the data) stays one-way.


def connect_regions(world: World) -> None:
  return
  from ._room_geometry import GEOM

  # 1. Map out which room IDs have area configurations for quick lookup
  room_has_areas = {f"{r['north']}_{r['east']}": "areas" in r for r in GEOM}

  # 2. Direction inversion mapping
  opposites = {"north": "south", "south": "north", "east": "west", "west": "east"}

  for room in GEOM:
    roomId = f"{room['north']}_{room['east']}"
    if roomId in ("100_100", "300_300"):
      continue

    has_areas = "areas" in room
    if has_areas:
      _connect_internal_slots(world, room, roomId)
      for direction in ("north", "south", "east", "west"):
        num_exits = len(room["exits"][direction])
        for idx in range(num_exits):
          slot_region = world.get_region(f"{roomId}#{_slot_id(direction, idx)}")
          base_region = world.get_region(roomId)
          _ = slot_region.connect(base_region, f"{roomId} {direction}.{idx} to base")
          _ = base_region.connect(slot_region, f"{roomId} base to {direction}.{idx}")

    for direction in ("north", "south", "east", "west"):
      num_exits = len(room["exits"][direction])
      if num_exits == 0:
        continue

      target_north, target_east = room["north"], room["east"]
      if direction == "north":
        target_north += 1
      elif direction == "south":
        target_north -= 1
      elif direction == "east":
        target_east += 1
      elif direction == "west":
        target_east -= 1

      target_room_id = f"{target_north}_{target_east}"
      opposite_direction = opposites[direction]

      for idx in range(num_exits):
        source_region = (
          world.get_region(f"{roomId}#{_slot_id(direction, idx)}") if has_areas else world.get_region(roomId)
        )

        # If the target room utilizes sub-areas, land on its specific slot wrapper
        if room_has_areas.get(target_room_id, False):
          target_region = world.get_region(f"{target_room_id}#{_slot_id(opposite_direction, idx)}")
        else:
          target_region = world.get_region(target_room_id)

        entrance_name = f"Exit from {roomId} {direction}.{idx}"
        entrance = Entrance(world.player, entrance_name, parent=source_region)
        source_region.exits.append(entrance)
        entrance.connect(target_region)

        _ = target_region.add_event(
          location_name=f"{target_room_id} - entrance.{opposite_direction}{idx}",
          item_name=f"{target_room_id} - entrance.{opposite_direction}{idx}",
          location_type=locations.MathQuestLocation,
          item_type=items.MathQuestItem,
        )


def _connect_internal_slots(world: World, room: ExitBase, roomId: str) -> None:
  return
  # For every pair of slots, figure out the rule under which they're mutually
  # reachable inside this room (None = always reachable, no items needed).
  unconditional_pairs: set[frozenset[str]] = set()
  conditional_rules: dict[frozenset[str], Rule] = {}
  if "areas" not in room:
    return
  for area_node in room["areas"]:
    node_rule = _reqs_to_rule(area_node["reqs"])
    for group in area_node["areas"]:
      ids = [_slot_id(s["side"], s["idx"]) for s in group]
      for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
          pair = frozenset((ids[i], ids[j]))
          if pair in unconditional_pairs:
            continue
          if node_rule is None:
            unconditional_pairs.add(pair)
            _ = conditional_rules.pop(pair, None)
          else:
            existing = conditional_rules.get(pair)
            conditional_rules[pair] = node_rule if existing is None else (existing | node_rule)
            # print("conditional_rules", conditional_rules[pair])

  for pair in unconditional_pairs:
    a, b = tuple(pair)
    ra, rb = world.get_region(f"{roomId}#{a}"), world.get_region(f"{roomId}#{b}")
    _ = ra.connect(rb, f"{roomId} {a}<->{b} (fwd)")
    _ = rb.connect(ra, f"{roomId} {a}<->{b} (back)")

  for pair, rule in conditional_rules.items():
    a, b = tuple(pair)
    ra, rb = world.get_region(f"{roomId}#{a}"), world.get_region(f"{roomId}#{b}")
    e1 = ra.connect(rb, f"{roomId} {a}->{b}")
    e2 = rb.connect(ra, f"{roomId} {b}->{a}")
    world.set_rule(e1, rule)
    world.set_rule(e2, rule)
