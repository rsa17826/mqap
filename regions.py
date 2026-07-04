from __future__ import annotations

import re

from BaseClasses import Entrance, Region
from entrance_rando import EntranceType, disconnect_entrance_for_randomization, randomize_entrances
from rule_builder.rules import Has, HasAll, Rule

from worlds.AutoWorld import World

from . import items, locations
from ._room_geometry import ExitBase

# arbitrary but consistent group IDs — one per literal side, so we can force opposite-side
# pairing (north only connects to south, east only to west) instead of same-axis pairing.
GROUP_NORTH = 1
GROUP_SOUTH = 2
GROUP_EAST = 3
GROUP_WEST = 4
# NOTE: warps are intentionally excluded from ER — see _connect_warps_vanilla for why. There is
# no GROUP_WARP entry in TARGET_GROUP_LOOKUP because no ER exit is ever tagged with a warp group.

TARGET_GROUP_LOOKUP: dict[int, list[int]] = {
  GROUP_NORTH: [GROUP_SOUTH],
  GROUP_SOUTH: [GROUP_NORTH],
  GROUP_EAST: [GROUP_WEST],
  GROUP_WEST: [GROUP_EAST],
}


def _reqs_to_rule(reqs: list[list[str],]) -> Rule | None | bool:
  if any(len(option) == 0 for option in reqs):
    return None
  rule: Rule | None = None
  for option in reqs:
    sub_rule: Rule = HasAll(*option) if len(option) > 1 else Has(option[0])
    rule = sub_rule if rule is None else (rule | sub_rule)
  return rule


# Moved to module scope (was previously built inline inside the old monolithic region-connection
# function): both the vanilla wiring path (_connect_cross_room_vanilla) and the always-vanilla
# warp wiring (_connect_warps_vanilla) need to iterate the exact same warp definitions.
WARPS: tuple[dict, ...] = (
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
  {
    "rule": None,
    "connections": ((10.1, 21, "root", 0), (9.11, 20, "root", 0)),
  },
)


# def _get_or_create_root(world: World, n: int, e: int, exit_regions: dict) -> Region:
#   """Finds or creates the central 'root' region for a specific room coordinate."""
#   root_key = (n, e, "root", 0)
#   if root_key in exit_regions:
#     return exit_regions[root_key]

#   root_name = f"{n}_{e}: root"
#   root_region = Region(root_name, world.player, world.multiworld)
#   world.multiworld.regions.append(root_region)
#   exit_regions[root_key] = root_region
#   return root_region


# def _connect_with_root(world: World, source: Region, target: Region, rule: Rule | None, exit_regions: dict) -> None:
#   """Connects source to target, and routes standard exits one-way into their room's root."""
#   # First, link the source and target normally
#   _connect(world, source, target, rule)

#   # Process both regions; if they are standard exits, route them into the root
#   for region in (source, target):
#     if ": " in region.name and "root" not in region.name:
#       try:
#         coords, _ = region.name.split(": ")
#         n_str, e_str = coords.split("_")
#         n, e = int(n_str), int(e_str)

#         root_region = _get_or_create_root(world, n, e, exit_regions)

#         # ONE-WAY ONLY: From the exit into the root, unconditionally
#         _connect(world, region, root_region, rule=None)

#       except ValueError:
#         continue


def _connect(world: World, source: Region, target: Region, rule: Rule | None) -> Entrance:
  """Add a one-way entrance from source to target, with an optional access rule.
  Returns the Entrance (existing or newly created) so callers can tag it further, e.g. for ER."""
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
      combined_rule = old_rule | rule if old_rule is not None else rule

      world.set_rule(existing, combined_rule)
      existing._rule_object = combined_rule
    return existing

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
  return entrance


_SIDE_GROUP: dict[str, int] = {"north": GROUP_NORTH, "south": GROUP_SOUTH, "east": GROUP_EAST, "west": GROUP_WEST}


def finalize_entrance_randomization(world: World) -> None:
  print("asdasdadsdsaasdadssd")
  """Call this from World.connect_entrances (never from create_regions — Generic ER's own docs
    require randomize_entrances to run at that stage). By this point _mq_er_candidates already
    holds real, vanilla-connected Entrance objects (tagged during Pass 3 in create_and_connect_regions),
    so disconnect_entrance_for_randomization has an actual connected_region to split — no need to
    fabricate throwaway connections just to immediately tear them apart."""
  er_candidates: list[Entrance] = getattr(world, "_mq_er_candidates", [])
  if not er_candidates:
    world.er_pairings = []
    return
  print(er_candidates)
  for entrance in er_candidates:
    disconnect_entrance_for_randomization(entrance)

  placement_state = randomize_entrances(
    world,
    coupled=True,
    target_group_lookup=TARGET_GROUP_LOOKUP,
    exits=er_candidates,
  )
  world.er_pairings = placement_state.pairings
  write_er_connections_json(world)


def create_and_connect_regions(world: World) -> None:
  """Called from World.create_regions. Always builds the complete VANILLA region graph —
  including cross-room exits and warps — regardless of entrance_rando. If entrance_rando is on,
  the Pass 3 cross-room entrances are additionally tagged and stashed on world._mq_er_candidates
  for finalize_entrance_randomization (called later, from World.connect_entrances) to actually
  disconnect and re-shuffle. Building the real vanilla graph up front means ER has genuine
  connected_region entrances to split, rather than needing throwaway fake connections."""
  from ._room_geometry import GEOM

  exit_regions: dict[tuple[int, int, str, int], Region] = {}

  _create_exit_regions_and_roots(world, GEOM, exit_regions)
  _connect_intra_room(world, GEOM, exit_regions)

  er_candidates = _connect_cross_room_vanilla(world, GEOM, exit_regions, tag_for_er=bool(world.options.entrance_rando))
  world._mq_er_candidates = er_candidates # picked up later by finalize_entrance_randomization

  # Warps always wire vanilla, whether or not entrance_rando is on (see _connect_warps_vanilla).
  _connect_warps_vanilla(world, exit_regions)


def _create_exit_regions_and_roots(world: World, GEOM, exit_regions: dict) -> None:
  # NOTE: exit_regions is populated in place (do NOT shadow it with a fresh local dict here —
  # the caller's dict is what gets passed into _connect_intra_room / the Pass 3 functions below).

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
        _ = region.add_event(
          location_name=event_name,
          item_name=event_name,
          location_type=locations.MathQuestLocation,
          item_type=items.MathQuestItem,
        )


def _connect_intra_room(world: World, GEOM, exit_regions: dict) -> None:
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

      for node in area_group["areas"]:
        node_regions = [
          exit_regions[(n, e, ex["side"], ex["idx"])] for ex in node if (n, e, ex["side"], ex["idx"]) in exit_regions
        ]
        if len(node_regions) < 2:
          continue # single-exit node — nothing to wire, just a placeholder

        rep = node_regions[0]
        for other in node_regions[1:]:
          _connect(world, rep, other, rule=rule)
          _connect(world, other, rep, rule=rule)


def _connect_cross_room_vanilla(world: World, GEOM, exit_regions: dict, tag_for_er: bool = False) -> list[Entrance]:
  # ── Pass 3: connect exits *across* room boundaries ────────────────────────
  # Always builds real vanilla connections. When tag_for_er is True, each created entrance is
  # additionally marked with a randomization_group/type and returned so connect_entrances can
  # later call disconnect_entrance_for_randomization + randomize_entrances on genuine, already-
  # connected entrances (see finalize_entrance_randomization).
  OPPOSITE = {"east": "west", "west": "east", "north": "south", "south": "north"}
  DELTA = {"east": (0, 1), "west": (0, -1), "north": (1, 0), "south": (-1, 0)}

  er_candidates: list[Entrance] = []
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
      forward = _connect(world, region, neighbor, rule=None)
      backward = _connect(world, neighbor, region, rule=None)

      if tag_for_er:
        for entrance, entrance_side in ((forward, side), (backward, OPPOSITE[side])):
          entrance.randomization_type = EntranceType.TWO_WAY
          entrance.randomization_group = _SIDE_GROUP[entrance_side]
          er_candidates.append(entrance)

  return er_candidates


def _connect_warps_vanilla(world: World, exit_regions: dict, warps: tuple[dict, ...] = WARPS) -> None:
  """Vanilla (always-on) warp wiring. Warps are deliberately NOT part of entrance randomization:
  several WARPS entries are many-to-one hubs (e.g. warp 0 connects three separate rooms so that any
  spoke reaches any other spoke), and coupled Generic ER fundamentally pairs single entrances 1:1.
  Flattening a hub into independent two-way edges and letting them shuffle globally breaks that
  "any spoke reaches any other spoke" semantics and can deadlock the ER solver (dead-end warp
  targets with no reachable matching warp exit left to pair against). So regardless of whether
  entrance_rando is on, warps always get wired here exactly as in vanilla."""
  for i, warpData in enumerate(warps):
    warp = Region(
      f"{warpData['connections'][0][0]}_{warpData['connections'][0][1]}: warp {i}", world.player, world.multiworld
    )
    world.multiworld.regions.append(warp)
    for con in warpData["connections"]:
      _connect(world, exit_regions[*con], warp, rule=warpData["rule"])
      _connect(world, warp, exit_regions[*con], rule=warpData["rule"])


_EXIT_REGION_RE = re.compile(r"^(-?\d+(?:\.\d+)?)_(-?\d+(?:\.\d+)?): (\w+) (\d+)$")

_DELTA = {"east": (0, 1), "west": (0, -1), "north": (1, 0), "south": (-1, 0)}

# Ported verbatim from the standalone shuffle_exits.py script (its all_exits_raw builder).
# GEOM's exit dicts ARE the same "gap" objects that script reads out of its geometry module —
# {"left":.., "right":..} for north/south, {"top":.., "bottom":..} for east/west, with the same
# optional newX/newY override keys — so the exact same pixel-position formula applies unmodified.
BLOCK_W = 710 / 14 # 14 blocks horizontally (0-13)
BLOCK_H = 560 / 11 # 11 blocks vertically (0-10)


def _num(s: str) -> int | float:
  n = float(s)
  return int(n) if n == int(n) else n


# def _get_exit_gap(GEOM, n, e, side, idx) -> dict:
#   """Look up the raw exit gap dict for a given room/side/idx out of GEOM. Returns {} if not found
#   (e.g. for warp-hub connections, which never appear here since _mq_er_candidates only ever
#   contains Pass 3 room-exit entrances)."""
#   for room in GEOM:
#     if room["north"] == n and room["east"] == e:
#       exit_list = room.get("exits", {}).get(side, [])
#       if idx < len(exit_list):
#         return exit_list[idx]
#   return {}


# def _compute_exit_position(gap: dict, side: str) -> dict:
#   """Computes src_coord/dest_x/dest_y/xIsEven/yIsEven for one exit gap, exactly matching
#   shuffle_exits.py's per-direction formula. Every exit gets this computed uniformly regardless of
#   whether it ends up used as the "from" or "to" side of a connection — the caller picks which
#   fields it actually needs (from_exit -> src_coord/direction, to_exit -> dest_x/dest_y/xIsEven/yIsEven)."""
#   pos: dict = {}
#   if side == "north":
#     mid_block_x = (gap["left"] + gap["right"]) / 2
#     pos["src_coord"] = mid_block_x * BLOCK_W
#     pos["dest_x"] = mid_block_x * BLOCK_W
#     pos["dest_y"] = 0 * BLOCK_H
#     if (gap["left"] + gap["right"]) % 2 == 1:
#       pos["xIsEven"] = BLOCK_W / 2
#   elif side == "south":
#     mid_block_x = (gap["left"] + gap["right"]) / 2
#     pos["src_coord"] = mid_block_x * BLOCK_W
#     pos["dest_x"] = mid_block_x * BLOCK_W
#     pos["dest_y"] = 10 * BLOCK_H
#     if (gap["left"] + gap["right"]) % 2 == 1:
#       pos["xIsEven"] = BLOCK_W / 2
#   elif side == "west":
#     mid_block_y = (gap["top"] + gap["bottom"]) / 2
#     pos["src_coord"] = mid_block_y * BLOCK_H
#     pos["dest_x"] = 0 * BLOCK_W
#     pos["dest_y"] = mid_block_y * BLOCK_H
#     if (gap["top"] + gap["bottom"]) % 2 == 1:
#       pos["yIsEven"] = BLOCK_H / 2
#   elif side == "east":
#     mid_block_y = (gap["top"] + gap["bottom"]) / 2
#     pos["src_coord"] = mid_block_y * BLOCK_H
#     pos["dest_x"] = 13 * BLOCK_W
#     pos["dest_y"] = mid_block_y * BLOCK_H
#     if (gap["top"] + gap["bottom"]) % 2 == 1:
#       pos["yIsEven"] = BLOCK_H / 2

#   # Per-gap overrides, same as shuffle_exits.py's `if "newY"/"newX" in gap: ...`
#   if "newY" in gap:
#     pos["dest_y"] = gap["newY"]
#   if "newX" in gap:
#     pos["dest_x"] = gap["newX"]

#   return pos


def build_er_connections_data(world: World) -> list[dict]:
  """Builds one row per randomized entrance, in the shape patch_rooms.py's connections.json
  reader expects (originNorth/East, vanillaDestNorth/East, newDestNorth/East, newX/Y, srcCoord,
  direction, xIsEven, yIsEven). newX/newY/xIsEven/yIsEven come from the DESTINATION exit's own
  computed position (where you land), srcCoord/direction come from the ORIGIN exit's (where you
  approached from) — matching shuffle_exits.py's make_connection(from_exit, to_exit).

  mechanism/fromExitId/toExitId/requires are NOT consumed by patch_rooms.py's row builder (only
  originNorth/East, vanillaDest*, newDest*, newX/Y, srcCoord, direction, xIsEven/yIsEven are read
  when building ER_TABLE rows), so they're included here only as best-effort debug context —
  mechanism is always "edge" since warps are excluded from ER entirely (see _connect_warps_vanilla),
  and the exit ids are synthesized rather than cross-referenced against _exits.py's own id strings."""

  er_candidates: list[Entrance] = getattr(world, "_mq_er_candidates", [])
  connections: list[dict] = []

  for entrance in er_candidates:
    origin_match = _EXIT_REGION_RE.match(entrance.parent_region.name)
    dest_match = _EXIT_REGION_RE.match(entrance.connected_region.name) if entrance.connected_region else None
    if not origin_match or not dest_match:
      continue # skip anything that isn't a plain "n_e: side idx" exit region (e.g. warps, roots)

    on, oe, oside, oidx_s = origin_match.groups()
    on, oe = _num(on), _num(oe)

    dn, de, dside, didx_s = dest_match.groups()
    dn, de = _num(dn), _num(de)

    connections.append(
      {
        "north": on,
        "east": oe,
        "side": oside,
        "idx": oidx_s,
        "exitNorth": dn,
        "exitEast": de,
        "exitSide": dside,
        "exitIdx": didx_s,
      }
    )

  return connections


table_js = None


def write_er_connections_json(world: World) -> None:
  """Writes worlds/mathquest/json/connections.json — the file patch_rooms.py reads at patch time
  (its OUT_DIR is the mathquest package's own directory, not the AP output folder). Call this from
  World.generate_output. No-ops (writes an empty connections list) when entrance_rando is off."""
  connections = build_er_connections_data(world) if world.options.entrance_rando else []

  def fmt_num(n):
    if n is None:
      return "-1"
    if isinstance(n, str):
      return f'"{n}"'
    if n == int(n):
      return str(int(n))
    return f"{n:.4f}"

  global table_js
  rows = [
    "[{},{},{},{},{},{},{},{}]".format(
      fmt_num(c["north"]),
      fmt_num(c["east"]),
      fmt_num(c["side"]),
      fmt_num(c["idx"]),
      fmt_num(c["exitNorth"]),
      fmt_num(c["exitEast"]),
      fmt_num(c["exitSide"]),
      fmt_num(c["exitIdx"]),
    )
    for c in connections
  ]
  table_js = ",".join(rows)
  from .__trywritefile import trywritefile
  trywritefile()
  # try:
  #   with open("./path", "r") as f:
  #     path = f.read().strip()
  #     import os

  #     path = os.path.abspath(os.path.expanduser(path))
  #     if os.path.isdir(path):
  #       with open(os.path.join(path, "json", "connections.json"), "w", encoding="utf-8") as f: # noqa: PLW2901

  #         json.dump({"connections": connections, "seed": world.multiworld.seed_name}, f, indent=2)

  #         print(f"Success! Generated Client connections at: {path}")
  # except FileNotFoundError:
  #   pass
  # except Exception as e:
  #   print(e)
