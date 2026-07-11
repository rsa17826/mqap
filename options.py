from dataclasses import dataclass
from typing import ClassVar

from Options import OptionDict, OptionGroup, PerGameCommonOptions, Toggle, Range

# In this file, we define the options the player can pick.
# The most common types of options are Toggle, Range and Choice.

# Options will be in the game's template yaml.
# They will be represented by checkboxes, sliders etc. on the game's options page on the website.
# (Note: Options can also be made invisible from either of these places by overriding Option.visibility.
#  MathQuest doesn't have an example of this, but this can be used for secret / hidden / advanced options.)

# For further reading on options, you can also read the Options API Document:
# https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/options%20api.md
option_presets: dict[str, dict[str, bool | int]] = {
  "main": {
    "item_rando": True,
    "entrance_rando": False,
    # "three_orbs": True,
    "final_boss": True,
    "progressive_weapons": True,
    "progressive_armor": True,
    "progressive_magic": False,
    "death_link": True,
    "all_quests_maxed": False,
    "infinite_gold": False,
    "infinite_keys": False,
    "del_del": 20,
    "nothing": 10,
    "filler_gold": 30,
    "spawn_random_enemies": 70,
    # "allow_clips": 0,
    "each_quest_is_a_check": False,
  },
}


# The first type of Option we'll discuss is the Toggle.
# A toggle is an option that can either be on or off. This will be represented by a checkbox on the website.
# The default for a toggle is "off".
# If you want a toggle to be on by default, you can use the "DefaultOnToggle" class instead of the "Toggle" class.
class EntranceRando(Toggle):
  """
  Shuffles the connections between different areas, doors, or dungeons.
  When enabled, walking through a screen transition may lead to a completely different location than normal.
  """

  # The docstring of an option is used as the description on the website and in the template yaml.

  # You'll also want to set a display name, which will determine what the option is called on the website.
  display_name: str = "EntranceRando"
  default: bool = option_presets["main"]["entrance_rando"]


class DeathLink(Toggle):
  """
  Links your fate to other players in the multiworld.
  When enabled, if you die, everyone else on Death Link dies too. If they die, you die. Use with caution!
  """

  display_name: str = "DeathLink"
  default: bool = option_presets["main"]["death_link"]


class ItemRando(Toggle):
  """
  Shuffles the locations of items throughout the game.
  Progression items, equipment, and upgrades will be scattered across different checks instead of being in their vanilla spots.
  """

  display_name: str = "ItemRando"
  default: bool = option_presets["main"]["item_rando"]


class FinalBoss(Toggle):
  """
  Defeat the Final Boss to beat the game to achieve victory.
  """

  display_name: str = "FinalBoss"
  default: bool = option_presets["main"]["final_boss"]


class EachQuestIsACheck(Toggle):
  """
  Changes how quests handle rewards.
  When enabled, every individual quest completed acts as a randomized location check, allowing it to hold multiworld items.
  """

  display_name: str = "EachQuestIsACheck"
  default: bool = option_presets["main"]["each_quest_is_a_check"]


class AllQuestsMaxed(Toggle):
  """
  Requires the player to complete and max out every single quest in the game to achieve victory.
  """

  display_name: str = "AllQuestsMaxed"
  default: bool = option_presets["main"]["all_quests_maxed"]


class DelDel(Range):
  """
  Adjusts the frequency of the DelDel trap item appearing as the filler item. Higher values increase its spawn rate.
  """

  range_end: int = 100
  display_name: str = "DelDel"
  default: bool = option_presets["main"]["del_del"]


class SpawnRandomEnemies(Range):
  """
  Adjusts the weight/frequency of the Enemy Spawn trap appearing in the pool.
  When a player receives this trap, unexpected enemies will immediately spawn around them.
  """

  range_end: int = 100
  display_name: str = "SpawnRandomEnemies"
  default: bool = option_presets["main"]["spawn_random_enemies"]


class ProgressiveWeapons(Toggle):
  """
  Determines how weapons are received.
  When enabled, weapon items found in the world will always upgrade your current weapon to the next tier sequentially.
  """

  display_name: str = "ProgressiveWeapons"
  default: bool = option_presets["main"]["progressive_weapons"]


class ProgressiveArmor(Toggle):
  """
  Determines how armor is received.
  When enabled, armor items found in the world will always upgrade your current armor to the next tier sequentially.
  """

  display_name: str = "ProgressiveArmor"
  default: bool = option_presets["main"]["progressive_armor"]


class ProgressiveMagic(Toggle):
  """
  Determines how magic spells or upgrades are received.
  When enabled, finding a magic item will unlock spells in a strict linear progression.
  """

  display_name: str = "ProgressiveMagic"
  default: bool = option_presets["main"]["progressive_magic"]


class InfiniteGold(Toggle):
  """
  Grants the player an infinite or maxed-out supply of gold right from the start of the game, bypassing the need to farm money.
  """

  display_name: str = "InfiniteGold"
  default: bool = option_presets["main"]["infinite_gold"]


class InfiniteKeys(Toggle):
  """
  Grants the player an infinite supply of keys. chests requiring standard keys can be opened freely without consuming resources.
  """

  display_name: str = "InfiniteKeys"
  default: bool = option_presets["main"]["infinite_keys"]


class Nothing(Range):
  """
  Adjusts the weight/frequency of "Nothing" filler items in the pool.
  Finding this item gives the player absolutely nothing, serving as pure empty filler.
  """

  range_end: int = 100
  display_name: str = "Nothing"
  default: bool = option_presets["main"]["nothing"]


class FillerGold(Range):
  """
  filler gold..., more like fill 'yr pockets with gold; 500 gold to be exact
  Adjusts the weight/frequency of getting gold filler items in the pool.
  """

  range_end: int = 100
  display_name: str = "FillerGold"
  default: bool = option_presets["main"]["filler_gold"]


class AllowClips(OptionDict):
  """
  Determines how logic handles clipping through walls or boundaries.

  no clips allowed: Standard logic; out-of-bounds glitches are not expected.
  clips always send to vanilla location: Logic assumes clipping through a transition takes you where it normally would, bypassing entrance rando remappings.
  clips send to default exit: Logic assumes clipping takes you to the map's default error/safety exit, following entrance rando remappings.
  """

  value: ClassVar[dict[str, int]] = {
    "no clips allowed": 0,
    "clips always send to vanilla location": 1,
    "clips send to default exit": 2,
  }
  display_name: str = "AllowClips"


# We must now define a dataclass inheriting from PerGameCommonOptions that we put all our options in.
# This is in the format "option_name_in_snake_case: OptionClassName".
@dataclass
class MathQuestOptions(PerGameCommonOptions):
  item_rando: ItemRando
  entrance_rando: EntranceRando
  final_boss: FinalBoss
  death_link: DeathLink
  each_quest_is_a_check: EachQuestIsACheck
  allow_clips: AllowClips
  all_quests_maxed: AllQuestsMaxed
  del_del: DelDel
  spawn_random_enemies: SpawnRandomEnemies
  nothing: Nothing
  progressive_weapons: ProgressiveWeapons
  progressive_armor: ProgressiveArmor
  progressive_magic: ProgressiveMagic
  infinite_gold: InfiniteGold
  infinite_keys: InfiniteKeys
  filler_gold: FillerGold


# If we want to group our options by similar type, we can do so as well. This looks nice on the website.
option_groups: list[OptionGroup] = [
  OptionGroup(
    "Gameplay",
    [
      # ItemRando,
      EntranceRando,
      DeathLink,
    ],
  ),
  OptionGroup(
    "Progress",
    [
      ProgressiveWeapons,
      ProgressiveArmor,
      ProgressiveMagic,
    ],
  ),
  OptionGroup(
    "Infinites",
    [
      InfiniteGold,
      InfiniteKeys,
    ],
  ),
  # OptionGroup(
  #   "Glitches",
  #   [
  #     # AllowClips,
  #   ],
  # ),
  OptionGroup(
    "Win Condition",
    [
      AllQuestsMaxed,
      FinalBoss,
    ],
  ),
  OptionGroup(
    "Traps",
    [
      DelDel,
      SpawnRandomEnemies,
      Nothing,
      FillerGold,
    ],
  ),
]
