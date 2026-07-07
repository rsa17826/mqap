from __future__ import annotations

from BaseClasses import Item, ItemClassification
from rule_builder.rules import Has, HasAll, Rule

from worlds.AutoWorld import World

from ._progression import PROG

# Every item must have a unique integer ID associated with it.
# We will have a lookup from item name to ID here that, in world.py, we will import and bind to the world class.
# Even if an item doesn't exist on specific options, it must be present in this lookup.
ITEM_NAME_TO_ID: dict[str, int] = {"trap:deldel": 99999}

DEFAULT_ITEM_CLASSIFICATIONS = {
  "trap:deldel": ItemClassification.trap,
}

HAS_LIST: dict[str, Rule[World]] = {}
maxQuests: dict[str, int] = {}

_id_counter = 1
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
        elif itemInfo.startswith(("area:",)):
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
def get_random_filler_item_name(_world: World) -> str:
  # MathQuest has an option called "trap_chance".
  # This is the percentage chance that each filler item is a Math Trap instead of a Confetti Cannon.
  # For this purpose, we need to use a random generator.

  # IMPORTANT: Whenever you need to use a random generator, you must use world.random.
  # This ensures that generating with the same generator seed twice yields the same output.
  # DO NOT use a bare random object from Python's built-in random module.
  # if world.random.randint(0, 99) < world.options.trap_chance:
  #   return "Math Trap"
  return "trap:deldel"


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
    if k == "trap:deldel":
      continue

    # Check the option before creating quest items
    if k.startswith("quest:") and not world.options.each_quest_is_a_check:
      continue

    itempool.append(world.create_item(k))

  number_of_items = len(itempool)
  number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
  needed_number_of_filler_items = number_of_unfilled_locations - number_of_items

  itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]
  world.multiworld.itempool += itempool
