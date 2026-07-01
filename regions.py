from __future__ import annotations

from BaseClasses import Entrance, Region
from rule_builder.rules import Has, HasAll, Rule

from worlds.AutoWorld import World

from . import items, locations
from ._room_geometry import ExitBase


def _reqs_to_rule(reqs: list[list[str]]) -> Rule | None:
  if any(len(option) == 0 for option in reqs):
    return None
  rule: Rule | None = None
  for option in reqs:
    sub_rule: Rule = HasAll(*option) if len(option) > 1 else Has(option[0])
    rule = sub_rule if rule is None else (rule | sub_rule)
  return rule


def _get_or_create_root(world: World, n: int, e: int, exit_regions: dict) -> Region:
  """Finds or creates the central 'root' region for a specific room coordinate."""
  root_key = (n, e, "root", 0)
  if root_key in exit_regions:
    return exit_regions[root_key]

  root_name = f"{n}_{e}: root"
  root_region = Region(root_name, world.player, world.multiworld)
  world.multiworld.regions.append(root_region)
  exit_regions[root_key] = root_region
  return root_region


def _connect_with_root(world: World, source: Region, target: Region, rule: Rule | None, exit_regions: dict) -> None:
  """Connects source to target, and routes standard exits one-way into their room's root."""
  # First, link the source and target normally
  _connect(world, source, target, rule)

  # Process both regions; if they are standard exits, route them into the root
  for region in (source, target):
    if ": " in region.name and "root" not in region.name:
      try:
        coords, _ = region.name.split(": ")
        n_str, e_str = coords.split("_")
        n, e = int(n_str), int(e_str)

        root_region = _get_or_create_root(world, n, e, exit_regions)

        # ONE-WAY ONLY: From the exit into the root, unconditionally
        _connect(world, region, root_region, rule=None)

      except ValueError:
        continue


def _connect(world: World, source: Region, target: Region, rule: Rule | None) -> None:
  """Add a one-way entrance from source to target, with an optional access rule."""
  name = f"{source.name} -> {target.name}"

  # 1. Check if an entrance between these specific regions already exists
  existing = next((e for e in source.exits if e.name == name), None)

  if existing:
    # If the new connection is unconditional, it overrides any existing logic requirements.
    if rule is None:
      existing.access_rule = lambda state: True
      existing._is_unconditional = True
      if hasattr(existing, "_rule_object"):
        delattr(existing, "_rule_object")

    # If both the old and new connections have requirements, logically OR them together.
    elif not getattr(existing, "_is_unconditional", False):
      old_rule = getattr(existing, "_rule_object", None)
      # Rule builder rules MUST be combined using the bitwise | operator
      combined_rule = old_rule | rule if old_rule else rule

      world.set_rule(existing, combined_rule)
      existing._rule_object = combined_rule
    return

  # 2. If it doesn't exist, create it cleanly
  entrance = Entrance(world.player, name, parent=source)

  if rule is None:
    # Explicitly flag unconditional paths to handle future overlaps cleanly
    entrance.access_rule = lambda state: True
    entrance._is_unconditional = True
  else:
    # Use rule_builder's built-in set_rule helper to correctly resolve and register the rule
    world.set_rule(entrance, rule)
    entrance._rule_object = rule
    entrance._is_unconditional = False

  source.exits.append(entrance)
  entrance.connect(target)


def create_and_connect_regions(world: World) -> None:
  from ._room_geometry import GEOM

  # Key: (north, east, side, idx) -> Region
  exit_regions: dict[tuple[int, int, str, int], Region] = {}

  # ── Pass 1: create one Region per exit in every room + root regions ───────
  for room in GEOM:
    n, e = room["north"], room["east"]

    # Pre-create the root region for this room up front
    root_name = f"{n}_{e}: root"
    root_region = Region(root_name, world.player, world.multiworld)
    world.multiworld.regions.append(root_region)
    exit_regions[(n, e, "root", 0)] = root_region

    for side, exit_list in room.get("exits", {}).items():
      for idx in range(len(exit_list)):
        name = f"{n}_{e}: {side} {idx}"
        region = Region(name, world.player, world.multiworld)
        world.multiworld.regions.append(region)
        exit_regions[(n, e, side, idx)] = region

        # ONE-WAY ONLY: Establish the connection right here during creation!
        _connect(world, region, root_region, rule=None)

        # ─── ADD THIS BLOCK TO GENERATE THE ENTRANCE VIRTUAL EVENTS ───
        event_name = f"{n}_{e} - entrance.{side}{idx}"
        _=region.add_event(
          location_name=event_name,
          item_name=event_name,
          location_type=locations.MathQuestLocation,
          item_type=items.MathQuestItem,
        )

  # ── Pass 2: connect exits *within* each room via area groups ──────────────
  for room in GEOM:
    n, e = room["north"], room["east"]

    if "areas" not in room:
      # No area data → all exits in this room connect freely
      all_regions = [
        exit_regions[(n, e, side, idx)]
        for side, exit_list in room.get("exits", {}).items()
        for idx in range(len(exit_list))
        if (n, e, side, idx) in exit_regions
      ]
      for i, src in enumerate(all_regions):
        for dst in all_regions[i + 1 :]:
          _connect(world, src, dst, rule=None)
          _connect(world, dst, src, rule=None)
      continue

    for area_group in room["areas"]:
      rule = _reqs_to_rule(area_group["reqs"])

      # Each inner list is a "node" - exits that share the same physical area.
      # Exits in the same node are directly connected (no rule).
      # All nodes in the same group connect to each other via the group rule.
      node_reps: list[Region] = []

      for node in area_group["areas"]:
        node_regions = [
          exit_regions[(n, e, ex["side"], ex["idx"])]
          for ex in node
          if (n, e, ex["side"], ex["idx"]) in exit_regions
        ]
        if not node_regions:
          continue

        # Wire exits inside a node together unconditionally
        rep = node_regions[0]
        for other in node_regions[1:]:
          _connect(world, rep, other, rule=None)
          _connect(world, other, rep, rule=None)

        node_reps.append(rep)

      # Wire every node to every other node in this group (bidirectional)
      for i, src in enumerate(node_reps):
        for dst in node_reps[i + 1 :]:
          _connect_with_root(world, src, dst, rule=rule, exit_regions=exit_regions)
          _connect_with_root(world, dst, src, rule=rule, exit_regions=exit_regions)

  # ── Pass 3: connect exits *across* room boundaries ────────────────────────
  OPPOSITE = {"east": "west", "west": "east", "north": "south", "south": "north"}
  DELTA = {"east": (0, 1), "west": (0, -1), "north": (1, 0), "south": (-1, 0)}

  seen: set[frozenset] = set()
  for (n, e, side, idx), region in exit_regions.items():
    # SKIP ROOT ENTRIES: roots do not cross physical room boundaries!
    if side == "root":
      continue

    dn, de = DELTA[side]
    neighbor_key = (n + dn, e + de, OPPOSITE[side], idx)
    pair = frozenset([(n, e, side, idx), neighbor_key])

    if neighbor_key in exit_regions and pair not in seen:
      seen.add(pair)
      neighbor = exit_regions[neighbor_key]

      # Since we handle exit -> root linkages explicitly during Pass 1,
      # we can safely go back to using standard _connect here!
      _connect(world, region, neighbor, rule=None)
      _connect(world, neighbor, region, rule=None)

  # Create the warp region
  warps = (
    {
      "rule": _reqs_to_rule([["permit:volcano"]]),
      "connections": ((17, 17, "south", 0), (17, 17, "west", 0), (18, 17, "south", 0)),
    },
    {
      "rule": None,
      "connections": ((4, 13, "root", 0), (100, 100, "south", 0)),
    },
    {
      "rule": None,
      "connections": ((3, 16, "root", 0), (200, 200, "north", 0)),
    },
    {
      "rule": None,
      "connections": ((200, 200, "root", 0), (201, 200, "root", 0)),
    },
    {
      "rule": _reqs_to_rule([["magic:drain", "quest:aSword.1"]]),
      "connections": ((18, 25, "root", 0), (500, 500, "north", 0)),
    },
    {
      "rule": None,
      "connections": ((6, 21, "root", 0), (300, 300, "south", 0)),
    },
    {
      "rule": None,
      "connections": ((10, 16, "root", 0), (10, 17, "south", 0)),
    },
    {
      "rule": _reqs_to_rule([["permit:bomb"]]),
      "connections": ((11, 13, "root", 0), (11, 14, "south", 0)),
    },
    {
      "rule": None,
      "connections": ((11, 14, "root", 0), (9, 13, "root", 0)),
    },
    {
      "rule": _reqs_to_rule([["magic:drain"]]),
      "connections": ((9, 13, "root", 0), (10, 13, "root", 0), (9, 14, "root", 0)),
    },
    {
      "rule": _reqs_to_rule([["magic:drain"]]),
      "connections": ((9, 14, "root", 0), (10, 14, "north", 0)),
    },
    {
      "rule": _reqs_to_rule([["misc:fire crystal"]]),
      "connections": ((8, 9, "root", 0), (7, 9, "south", 0)),
    },
    {
      "rule": _reqs_to_rule([["flag:lit torch 2", "flag:lit torch 1"]]),
      "connections": ((6, 23, "root", 0), (5, 23, "south", 0)),
    },
    {
      "rule": None,
      "connections": ((17, 14, "root", 0), (18, 14, "north", 0)),
    },
    {
      "rule": None,
      "connections": ((20, 12, "root", 0), (21, 12, "south", 0)),
    },
    {
      "rule": None,
      "connections": ((22, 10, "root", 0), (22, 13, "east", 0), (22, 13, "north", 0)),
    },
    {
      "rule": None,
      "connections": ((21, 13, "east", 1), (22, 11, "south", 0), (22, 11, "north", 0)),
    },
    {
      "rule": None,
      "connections": ((22, 12, "root", 0), (21, 9, "north", 0)),
    },
    {
      "rule": None,
      "connections": ((18, 12, "root", 0), (18, 11, "west", 0)),
    },
    {
      "rule": _reqs_to_rule([["permit:bomb"]]),
      "connections": ((10, 12, "root", 0), (7, 12, "south", 0)),
    },
    {
      "rule": _reqs_to_rule([["permit:bomb"]]),
      "connections": ((12, 21, "root", 0), (11, 21, "root", 0)),
    },
    {
      "rule": None,
      "connections": ((18, 16, "root", 0), (19, 16, "south", 0)),
    },
    {
      "rule": None,
      "connections": ((19, 16, "root", 0), (19, 15, "north", 0)),
    },
    {
      "rule": None,
      "connections": ((9, 22, "north", 0), (9, 21, "root", 0)),
    },
    {
      "rule": _reqs_to_rule([["permit:bomb.2"]]),
      "connections": ((12, 14, "root", 0), (9, 21, "root", 0)),
    },
    {
      "rule": None,
      "connections": ((21, 21, "east", 0), (20, 21, "root", 0)),
    },
    {
      "rule": _reqs_to_rule([["permit:bomb", "magic:lightning"]]),
      "connections": ((20, 21, "root", 0), (19, 22, "root", 0)),
    },
    {
      "rule": _reqs_to_rule([["permit:bomb.2"]]),
      "connections": ((12, 23, "root", 0), (12, 22, "north", 0)),
    },
    {
      "rule": None,
      "connections": ((24, 10, "root", 0), (23, 14, "north", 0)),
    },
    {
      "rule": None,
      "connections": ((24, 13, "root", 0), (23, 10, "root", 0)),
    },
    {
      "rule": _reqs_to_rule([["quest:gTree.9"]]),
      "connections": ((17, 19, "root", 0), (17.1, 19, "root", 0)),
    },
    {
      "rule": _reqs_to_rule([["quest:gTree.9"]]),
      "connections": ((15, 17, "root", 0), (17.1, 19, "root", 0)),
    },
    {
      "rule": _reqs_to_rule([["flag:10.1 code"]]),
      "connections": ((10, 21, "root", 0), (10.1, 21, "root", 0)),
    },
  )
  warp = Region("10.1_21: warp 0", world.player, world.multiworld)
  warpDest = Region("9.11_20: warp 0", world.player, world.multiworld)
  _connect(world, warpDest, warp, rule=None)
  _connect(world, warp, warpDest, rule=None)
  for warpData in warps:
    warp = Region(
      f"{warpData['connections'][0][0]}_{warpData['connections'][0][1]}: warp 0", world.player, world.multiworld
    )
    world.multiworld.regions.append(warp)
    for con in warpData["connections"]:
      _connect(world, exit_regions[*con], warp, rule=warpData["rule"])
      _connect(world, warp, exit_regions[*con], rule=warpData["rule"])

  # Connections INTO the warp
  # _connect(world, exit_regions[(17, 17, "south", 0)], warp, rule=_reqs_to_rule([['permit:volcano']]))
  # _connect(world, exit_regions[(17, 17, "west", 0)], warp, rule=_reqs_to_rule([['permit:volcano']]))

  # # Connections OUT of the warp — this is what was missing
  # _connect(world, warp, exit_regions[(18, 17, "south", 0)], rule=_reqs_to_rule([['permit:volcano']]))
  # _connect(world, warp, exit_regions[(17, 17, "south", 0)], rule=_reqs_to_rule([['permit:volcano']]))
  # _connect(world, warp, exit_regions[(17, 17, "west", 0)], rule=_reqs_to_rule([['permit:volcano']]))


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
