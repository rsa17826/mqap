
def trywritefile():
  from ._room_geometry import GEOM
  from .items import ITEM_NAME_TO_ID
  from .locations import LOCATION_NAME_TO_ID
  from .regions import table_js
  if len(LOCATION_NAME_TO_ID.keys())<3:
    return
  if len(ITEM_NAME_TO_ID.keys())<3:
    return
  # if not table_js or len(table_js)<3:
  #   return
  try:
    with open("./path", "r") as f:
      path = f.read().strip()
      import os

      path = os.path.abspath(os.path.expanduser(path))
      if os.path.isdir(path):
        with open(os.path.join(path, "archipelago_manifest.js"), "w", encoding="utf-8") as f: # noqa: PLW2901
          import json

          _ = f.write(
            f"""/**
* AUTO-GENERATED ARCHIPELAGO MANIFESTS
* Do not modify this file directly. Regenerate via your build script.
*/

const AP_LOCATION_IDS = {json.dumps(LOCATION_NAME_TO_ID, indent=2)}
const AP_ITEM_IDS = {json.dumps({v: k for k, v in ITEM_NAME_TO_ID.items()}, indent=2)}

const AP_ENTRANCE_IDS = {json.dumps(GEOM, indent=2)}
const ROOM_INTERNAL_WIDTH = 710.0
const ROOM_INTERNAL_HEIGHT = 560.0
const BLOCKS_X = 14
const BLOCKS_Y = 11
const BLOCK_W = ROOM_INTERNAL_WIDTH / BLOCKS_X
const BLOCK_H = ROOM_INTERNAL_HEIGHT / BLOCKS_Y

/**
 * @type (string|number)[][]
 */
var ER_TABLE = [{table_js or ""}]
var ER_MAP = new Map()
window.ER_MAP=ER_MAP
window.ER_TABLE=ER_TABLE

for (var i = 0; i < ER_TABLE.length; i++) {{
  var r = ER_TABLE[i]
  // Key by origin room: "north_east"
  var key = r[0] + "_" + r[1]
  if (!ER_MAP.has(key)) {{
    ER_MAP.set(key, [])
  }}
  ER_MAP.get(key).push({{
    origSide: r[2],
    origIdx: r[3],
    newNorth: r[4],
    newEast: r[5],
    exitSide: r[6],
    exitIdx: r[7]
  }})
}}
console.log(`[Archipelago] Database ready: ${{Object.keys(AP_LOCATION_IDS).length}} locations, ${{Object.keys(AP_ITEM_IDS).length}} items, ${{Object.keys(AP_ENTRANCE_IDS).length}} entrances.`);""" # noqa: E501
          )

          print(f"Success! Generated Client database at: {path}")
  except FileNotFoundError:
    pass
  except Exception as e:
    print(e)