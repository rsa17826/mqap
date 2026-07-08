from typing import NotRequired, TypedDict


class PowerDict(TypedDict):
  requires: NotRequired[list[list[str]]]
  power: NotRequired[int]
  magicPower: NotRequired[int]


class MagicCost(TypedDict):
  value: float
  cost: int


magicPower = "magicPower"
power = "power"

# @regex power:
# @replace "power":
# @endregex
# @regex magicPower:
# @replace "magicPower":
# @endregex

# OFF_MAGIC: dict[str, MagicCost] = {
#   "ice": {"value": 0.8, "cost": 20},
#   "fire": {"value": 0.8, "cost": 13},
#   "drain": {"value": 0.75, "cost": 20},
#   "heal": {"value": 1, "cost": 5},
#   "blessing": {"value": 0.75, "cost": 20},
#   "blast": {"value": 1, "cost": 10},
#   "lightning": {"value": 1, "cost": 55},
# }
POWER_TABLE: dict[str, list[PowerDict]] = {
  "weapon:pitchfork": [{"power": 13}],
  "weapon:orcBlade": [{"power": 90}],
  "weapon:sKnife": [{"power": 12}],
  "weapon:warlockStaff": [{"magicPower": 25}],
  "weapon:sunSword": [{"power": 19}],
  "weapon:axe": [{"power": 100}],
  "weapon:baneBlade": [{"power": 76, "magicPower": 50}],
  "weapon:shadowStaff": [{"power": 12, "magicPower": 100}],
  "weapon:sword": [{"power": 10}],
  "weapon:bombSword": [
    # {"requires": [["permit:bomb"]], "power": 110},
    {"power": 10},
  ],
  "weapon:royalStaff": [{"power": 0, "magicPower": 50}],
  "weapon:refreshStaff": [{"power": 25, "magicPower": 220}],
  "weapon:soulSword": [{"power": 130}],
  "weapon:club": [{"power": 2}],
  "weapon:royalSword": [{"power": 17}],
  "weapon:dagger": [{"power": 6}],
  "weapon:aSword": [{"power": 30}],
  "weapon:twinFury": [{"power": 94}],
  "weapon:creeperCrusher": [{"power": 75}],
  "armor:alphaArmor": [{"power": 30, "magicPower": 30}],
  "armor:regenArmor": [{"power": 0}],
  "armor:diamondArmor": [{"power": 0}],
  "armor:phantomCoat": [{"power": 0}],
  "armor:grimGear": [{"power": 90, "magicPower": 200}],
  "armor:shadowCoat": [{"power": 0}],
  "armor:sunArmor": [{"power": 25}],
  "armor:soulArmor": [{"power": 15}],
  "armor:vest": [{"power": 1}],
  "armor:robe": [{"power": 0, "magicPower": 20}],
  "armor:iron": [{"power": 48}],
  "armor:royalArmor": [{"power": 115}],
  "armor:mysticCloak": [{"power": 0, "magicPower": 50}],
  "armor:speedVest": [{"power": 4}],
  "armor:nobleArmor": [{"power": 300}],
}
