from __future__ import annotations

from BaseClasses import Item, ItemClassification
from rule_builder.rules import Has, HasAll, Rule

from worlds.AutoWorld import World

from ._progression import PROG

# Every item must have a unique integer ID associated with it.
# We will have a lookup from item name to ID here that, in world.py, we will import and bind to the world class.
# Even if an item doesn't exist on specific options, it must be present in this lookup.
ITEM_NAME_TO_ID: dict[str, int] = {}

DEFAULT_ITEM_CLASSIFICATIONS = {}

_id_counter = 99999
traps = ("spawn_random_enemies", "del_del", "nothing")
for trap in traps:
  DEFAULT_ITEM_CLASSIFICATIONS[f"trap:{trap}"] = ItemClassification.trap
  ITEM_NAME_TO_ID[f"trap:{trap}"] = _id_counter
  _id_counter -= 1

HAS_LIST: dict[str, Rule[World]] = {}
maxQuests: dict[str, int] = {}

# Maps each individual weapon item name to its 1-based collection order.
# Used when `progressive_weapons` is on: instead of receiving "weapon:bombSword" directly,
# the player receives generic "weapon:progressive weapons" items, and reaching a specific
# weapon's logic requires having received at least that many progressive weapon items.
WEAPON_ORDER: dict[str, int] = {
  "weapon:aSword": 1,
  "weapon:club": 2,
  "weapon:dagger": 3,
  "weapon:sword": 4,
  "weapon:sKnife": 5,
  "weapon:pitchfork": 6,
  "weapon:warlockStaff": 7,
  "weapon:royalStaff": 8,
  "weapon:royalSword": 9,
  "weapon:sunSword": 10,
  "weapon:shadowStaff": 11,
  "weapon:refreshStaff": 12,
  "weapon:orcBlade": 13,
  "weapon:creeperCrusher": 14,
  "weapon:twinFury": 15,
  "weapon:baneBlade": 16,
  "weapon:axe": 17,
  "weapon:bombSword": 18,
  "weapon:soulSword": 19,
}
ARMOR_ORDER: dict[str, int] = {
  "armor:alphaArmor": 1,
  "armor:vest": 2,
  "armor:regenArmor": 3,
  "armor:robe": 4,
  "armor:iron": 5,
  "armor:mysticCloak": 6,
  "armor:sunArmor": 7,
  "armor:royalArmor": 8,
  "armor:phantomCoat": 9,
  "armor:speedVest": 10,
  "armor:soulArmor": 11,
  "armor:shadowCoat": 12,
  "armor:grimGear": 13,
  "armor:nobleArmor": 14,
  "armor:diamondArmor": 15,
}
MAGIC_ORDER: dict[str, int] = {
  "magic:slow": 1,
  "magic:crush": 2,
  "magic:blast": 3,
  "magic:heal": 4,
  "magic:fire": 5,
  "magic:weak": 6,
  "magic:blessing": 7,
  "magic:drain": 8,
  "magic:cloud": 9,
  "magic:regen": 10,
  "magic:refresh": 11,
  "magic:doubleDown": 12,
  "magic:ice": 13,
  "magic:lightning": 14,
}

_id_counter = 1

DEFAULT_ITEM_CLASSIFICATIONS["weapon:progressive weapons"] = ItemClassification.progression
ITEM_NAME_TO_ID["weapon:progressive weapons"] = _id_counter
_id_counter += 1
DEFAULT_ITEM_CLASSIFICATIONS["armor:progressive armor"] = ItemClassification.progression
ITEM_NAME_TO_ID["armor:progressive armor"] = _id_counter
_id_counter += 1
DEFAULT_ITEM_CLASSIFICATIONS["magic:progressive magic"] = ItemClassification.progression
ITEM_NAME_TO_ID["magic:progressive magic"] = _id_counter
_id_counter += 1

for thing in PROG:
  if "receive" in thing:
    for itemInfo in thing["receive"]:
      itemName = itemInfo
      # itemName = itemInfo.removesuffix("#1")
      if itemName not in ITEM_NAME_TO_ID:
        if itemInfo.startswith(
          (
            "magic:",
            "weapon:",
            # "flag:final boss dead",
            "permit:",
            "misc:fire crystal",
            "loot:gold",
            "item:",
            "skill:",
            "food:",
            "misc:blue crystal",
            "misc:headstoneSwitch1",
            "misc:headstoneSwitch2",
            "misc:headstoneSwitch3",
            "misc:headstoneSwitch4",
            # "entrance.",
            "armor:",
            # "quest:",
            # "area:",
          )
        ):
          DEFAULT_ITEM_CLASSIFICATIONS[itemName] = ItemClassification.progression
          ITEM_NAME_TO_ID[itemName] = _id_counter
        elif itemInfo.startswith(
          (
            "item:ring",
            "item:aurastones",
          )
        ):
          DEFAULT_ITEM_CLASSIFICATIONS[itemName] = ItemClassification.useful
          ITEM_NAME_TO_ID[itemName] = _id_counter
        elif itemInfo.startswith(
          (
            "misc:",
            "craft:",
          )
        ):
          DEFAULT_ITEM_CLASSIFICATIONS[itemName] = ItemClassification.filler
          ITEM_NAME_TO_ID[itemName] = _id_counter
        elif itemInfo.startswith(("quest:",)):
          questData = itemInfo.split(":", 1)[1].split(".")
          if questData[0] not in maxQuests or int(questData[1]) > maxQuests[questData[0]]:
            maxQuests[questData[0]] = int(questData[1])
          continue
        elif itemInfo.startswith(
          (
            "area:",
            "flag:",
            "power:",
          )
        ):
          continue
        elif itemInfo.startswith(("loot:",)):
          pass
        else:
          print(itemName, "not used")
          continue
        _id_counter += 1
        if itemName.split("#", 1)[0] not in HAS_LIST:
          HAS_LIST[itemName.split("#", 1)[0]] = Has(itemName)
        else:
          HAS_LIST[itemName.split("#", 1)[0]] = Has(itemName) | HAS_LIST[itemName.split("#", 1)[0]]


# Each Item instance must correctly report the "game" it belongs to.
# To make this simple, it is common practice to subclass the basic Item class and override the "game" field.
class MathQuestItem(Item):
  game: str = "MathQuest"


# Ontop of our regular itempool, our world must be able to create arbitrary amounts of filler as requested by core.
# To do this, it must define a function called world.get_filler_item_name(), which we will define in world.py later.
# For now, let's make a function that returns the name of a random filler item here in items.py.
def get_random_filler_item_name(world: World) -> str:
  weights = [getattr(world.options, trap) for trap in traps]

  if sum(weights) == 0:
    return "trap:nothing"

  # Selects one trap based on the weights list
  chosen_trap = world.random.choices(traps, weights=weights, k=1)[0]
  return f"trap:{chosen_trap}"


def create_item_with_correct_classification(world: World, name: str) -> MathQuestItem:
  # Our world class must have a create_item() function that can create any of our items by name at any time.
  # So, we make this helper function that creates the item by name with the correct classification.
  # Note: This function's content could just be the contents of world.create_item in world.py directly,
  # but it seemed nicer to have it in its own function over here in items.py.
  classification = DEFAULT_ITEM_CLASSIFICATIONS[name]

  # It is perfectly normal and valid for an item's classification to differ based on the player's options.
  # In our case, Health Upgrades are only relevant to logic (and thus labeled as "progression") in hard mode.
  # if name == "Health Upgrade" and world.options.hard_mode:
  #   classification = ItemClassification.progression

  return MathQuestItem(name, classification, ITEM_NAME_TO_ID[name], world.player)


# With those two helper functions defined, let's now get to actually creating and submitting our itempool.
def create_all_items(world: World) -> None:
  itempool: list[Item] = []

  for k in ITEM_NAME_TO_ID.keys():
    # Skip creating the filler trap unconditionally
    if k.startswith("trap:"):
      continue

    # Check the option before creating quest items
    if k.startswith("quest:") and not world.options.each_quest_is_a_check:
      continue
    if k.startswith("weapon:"):
      if world.options.progressive_weapons:
        if k == "weapon:progressive weapons":
          continue
        k = "weapon:progressive weapons"
        print(k)
      else:
        if k == "weapon:progressive weapons":
          continue
    if k.startswith("armor:"):
      if world.options.progressive_armor:
        if k == "armor:progressive armor":
          continue
        k = "armor:progressive armor"
        print(k)
      else:
        if k == "armor:progressive armor":
          continue
      if world.options.progressive_magic:
        if k == "magic:progressive magic":
          continue
        k = "magic:progressive magic"
        print(k)
      else:
        if k == "magic:progressive magic":
          continue

    itempool.append(world.create_item(k))

  number_of_items = len(itempool)
  number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
  needed_number_of_filler_items = number_of_unfilled_locations - number_of_items

  itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]
  world.multiworld.itempool += itempool
