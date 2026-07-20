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
from rule_builder.rules import False_, True_

from .items import AREA_MAP, ARMOR_ORDER, HAS_LIST, MAGIC_ORDER, WEAPON_ORDER

_QUEST_RE = re.compile(r"^quest:([^.]+)\.(\d+)$")
_POWER_RE = re.compile(r"^power:(\d+)$")


def _reqs_to_rule(world: World, reqs: list[list[str]]) -> Rule | None:
  if any(len(option) == 0 for option in reqs):
    return None

  rule: Rule | None = None
  for option in reqs:
    sub_rule: Rule | None = None
    for item in option:
      tname = item.split("#", 1)[0]
      quest_match = _QUEST_RE.match(tname)

      # Intercept and convert progressive weapons dynamically
      if world.options.each_quest_is_a_check and quest_match:
        qname, qlevel = quest_match.group(1), int(quest_match.group(2))
        temprule = Has(f"quest:{qname}", qlevel)
      elif world.options.progressive_weapons and tname in WEAPON_ORDER:
        temprule = Has("weapon:progressive weapons", WEAPON_ORDER[tname])
      elif world.options.progressive_armor and tname in ARMOR_ORDER:
        temprule = Has("armor:progressive armor", ARMOR_ORDER[tname])
      elif world.options.progressive_magic and tname in MAGIC_ORDER:
        temprule = Has("magic:progressive magic", MAGIC_ORDER[tname])
      elif tname in HAS_LIST:
        temprule = HAS_LIST[tname]
      else:
        temprule = Has(item)

      if sub_rule is None:
        sub_rule = temprule
      else:
        sub_rule = sub_rule & temprule


    assert sub_rule is not None
    rule = sub_rule if rule is None else (rule | sub_rule)

  return rule


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
  # print("asdasdadsdsaasdadssd")
  """Call this from World.connect_entrances (never from create_regions — Generic ER's own docs
  require randomize_entrances to run at that stage). By this point _mq_er_candidates already
  holds real, vanilla-connected Entrance objects (tagged during Pass 3 in create_and_connect_regions),
  so disconnect_entrance_for_randomization has an actual connected_region to split — no need to
  fabricate throwaway connections just to immediately tear them apart."""
  er_candidates: list[Entrance] = getattr(world, "_mq_er_candidates", [])
  if not er_candidates:
    world.er_pairings = []
    return

  # print(er_candidates)
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


from ._room_geometry import GEOM, WARPS


def create_and_connect_regions(world: World) -> None:
  """Called from World.create_regions. Always builds the complete VANILLA region graph —
  including cross-room exits and warps — regardless of entrance_rando. If entrance_rando is on,
  the Pass 3 cross-room entrances are additionally tagged and stashed on world._mq_er_candidates
  for finalize_entrance_randomization (called later, from World.connect_entrances) to actually
  disconnect and re-shuffle. Building the real vanilla graph up front means ER has genuine
  connected_region entrances to split, rather than needing throwaway fake connections."""

  exit_regions: dict[tuple[float | int, int | float, str, int], Region] = {}

  _create_exit_regions_and_roots(world, exit_regions)
  _connect_intra_room(world, exit_regions)

  er_candidates = _connect_cross_room_vanilla(world, exit_regions, tag_for_er=bool(world.options.entrance_rando))
  world._mq_er_candidates = er_candidates # picked up later by finalize_entrance_randomization

  # Warps always wire vanilla, whether or not entrance_rando is on (see _connect_warps_vanilla).
  _connect_warps_vanilla(world, exit_regions)


from ._progression import AREA_POWER_REQS

for k, v in AREA_POWER_REQS.items():
  if isinstance(v, int):
    AREA_POWER_REQS[k] = [[weapon] for weapon, i in WEAPON_ORDER.items() if i > v]


def _create_exit_regions_and_roots(
  world: World,
  exit_regions: dict[tuple[float | int, int | float, str, int], Region],
) -> None:
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
        powerRule = None
        area = AREA_MAP[f"{n}_{e}"]
        if not world.options.no_power_reqs and area in AREA_POWER_REQS:
          powerRule = _reqs_to_rule(world, AREA_POWER_REQS[area])

        _ = _connect(world, region, root_region, rule=powerRule)

        # ─── ADD THIS BLOCK TO GENERATE THE ENTRANCE VIRTUAL EVENTS ───
        event_name = f"{n}_{e} - entrance.{side}{idx}"
        _ = region.add_event(
          location_name=event_name,
          item_name=event_name,
          location_type=locations.MathQuestLocation,
          item_type=items.MathQuestItem,
        )




def _connect_intra_room(world: World, exit_regions: dict) -> None:
  # ── Pass 2: connect exits *within* each room via area groups ──────────────
  for room in GEOM:
    n, e = room["north"], room["east"]

    if "areas" not in room:
      # No area data → all exits in this room connect freely
      all_regions = [exit_regions[(n, e, side, idx)] for side, exit_list in room.get("exits", {}).items() for idx in range(len(exit_list)) if (n, e, side, idx) in exit_regions]
      for i, src in enumerate(all_regions):
        for dst in all_regions[i + 1 :]:
          _connect(world, src, dst, rule=None)
          _connect(world, dst, src, rule=None)


      continue

    for area_group in room["areas"]:
      rule = _reqs_to_rule(world, area_group["reqs"])

      for node in area_group["areas"]:
        node_regions = [exit_regions[(n, e, ex["side"], ex["idx"])] for ex in node if (n, e, ex["side"], ex["idx"]) in exit_regions]
        if len(node_regions) < 2:
          continue # single-exit node — nothing to wire, just a placeholder

        rep = node_regions[0]
        for other in node_regions[1:]:
          _connect(world, rep, other, rule=rule)
          _connect(world, other, rep, rule=rule)





def _connect_cross_room_vanilla(world: World, exit_regions: dict, tag_for_er: bool = False) -> list[Entrance]:
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

      # Gate each direction by the AREA_POWER_REQS of the room being *entered* —
      # forward walks (n,e) -> neighbor room, so it's gated by the neighbor's area;
      # backward walks neighbor -> (n,e), so it's gated by (n,e)'s own area.
      area_here = AREA_MAP[f"{n}_{e}"]
      area_there = AREA_MAP[f"{neighbor_key[0]}_{neighbor_key[1]}"]

      forward_rule = _reqs_to_rule(world, AREA_POWER_REQS[area_there]) if not world.options.no_power_reqs and area_there in AREA_POWER_REQS else None
      backward_rule = _reqs_to_rule(world, AREA_POWER_REQS[area_here]) if not world.options.no_power_reqs and area_here in AREA_POWER_REQS else None

      # Since we handle exit -> root linkages explicitly during Pass 1,
      # we can safely go back to using standard _connect here!
      forward = _connect(world, region, neighbor, rule=forward_rule)
      backward = _connect(world, neighbor, region, rule=backward_rule)

      if tag_for_er:
        for entrance, entrance_side in ((forward, side), (backward, OPPOSITE[side])):
          entrance.randomization_type = EntranceType.TWO_WAY
          entrance.randomization_group = _SIDE_GROUP[entrance_side]
          er_candidates.append(entrance)




  return er_candidates


def _connect_warps_vanilla(world: World, exit_regions: dict) -> None:
  """Vanilla (always-on) warp wiring. Warps are deliberately NOT part of entrance randomization:

  several WARPS entries are many-to-one hubs (e.g. warp 0 connects three separate rooms so that any
  spoke reaches any other spoke), and coupled Generic ER fundamentally pairs single entrances 1:1.
  Flattening a hub into independent two-way edges and letting them shuffle globally breaks that
  "any spoke reaches any other spoke" semantics and can deadlock the ER solver (dead-end warp
  targets with no reachable matching warp exit left to pair against). So regardless of whether
  entrance_rando is on, warps always get wired here exactly as in vanilla."""
  for i, warpData in enumerate(WARPS):
    warp = Region(f"{warpData['connections'][0][0]}_{warpData['connections'][0][1]}: warp {i}", world.player, world.multiworld)
    world.multiworld.regions.append(warp)
    rule = _reqs_to_rule(world, warpData.get("reqs", [[]]))
    for con in warpData["connections"]:
      _ = _connect(world, exit_regions[*con], warp, rule=rule)
      _ = _connect(world, warp, exit_regions[*con], rule=rule)



_EXIT_REGION_RE = re.compile(r"^(-?\d+(?:\.\d+)?)_(-?\d+(?:\.\d+)?): (\w+) (\d+)$")

_DELTA = {"east": (0, 1), "west": (0, -1), "north": (1, 0), "south": (-1, 0)}

BLOCK_W = 710 / 14 # 14 blocks horizontally (0-13)
BLOCK_H = 560 / 11 # 11 blocks vertically (0-10)


def _num(s: str) -> int | float:
  n = float(s)
  return int(n) if n == int(n) else n


table_js = []


def write_er_connections_json(world: World) -> None:
  """Writes worlds/mathquest/json/connections.json — the file patch_rooms.py reads at patch time
  (its OUT_DIR is the mathquest package's own directory, not the AP output folder). Call this from
  World.generate_output. No-ops (writes an empty connections list) when entrance_rando is off."""
  global table_js
  if world.options.entrance_rando:
    er_candidates: list[Entrance] = getattr(world, "_mq_er_candidates", [])

    for entrance in er_candidates:
      origin_match = _EXIT_REGION_RE.match(entrance.parent_region.name)
      dest_match = _EXIT_REGION_RE.match(entrance.connected_region.name) if entrance.connected_region else None
      if not origin_match or not dest_match:
        continue # skip anything that isn't a plain "n_e: side idx" exit region (e.g. warps, roots)

      on, oe, oside, oidx_s = origin_match.groups()
      on, oe = _num(on), _num(oe)

      dn, de, dside, didx_s = dest_match.groups()
      dn, de = _num(dn), _num(de)
      table_js.append(
        (
          on,
          oe,
          oside,
          oidx_s,
          dn,
          de,
          dside,
          didx_s,
        )
      )


