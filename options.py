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
    "death_link": True,
    "all_quests_maxed": False,
    "del_del": 20,
    "nothing": 10,
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
  EntranceRando
  """

  # The docstring of an option is used as the description on the website and in the template yaml.

  # You'll also want to set a display name, which will determine what the option is called on the website.
  display_name: str = "EntranceRando"
  default: bool = option_presets["main"]["entrance_rando"]


class DeathLink(Toggle):
  """
  DeathLink
  """

  display_name: str = "DeathLink"
  default: bool = option_presets["main"]["death_link"]


class ItemRando(Toggle):
  """
  ItemRando
  """

  display_name: str = "ItemRando"
  default: bool = option_presets["main"]["item_rando"]


class FinalBoss(Toggle):
  """
  FinalBoss
  """

  display_name: str = "FinalBoss"
  default: bool = option_presets["main"]["final_boss"]


class EachQuestIsACheck(Toggle):
  """
  EachQuestIsACheck
  """

  display_name: str = "EachQuestIsACheck"
  default: bool = option_presets["main"]["each_quest_is_a_check"]


class AllQuestsMaxed(Toggle):
  """
  AllQuestsMaxed
  """

  display_name: str = "AllQuestsMaxed"
  default: bool = option_presets["main"]["all_quests_maxed"]


class DelDel(Range):
  """
  DelDel
  """

  range_end: int = 100
  display_name: str = "DelDel"
  default: bool = option_presets["main"]["del_del"]


class SpawnRandomEnemies(Range):
  """
  SpawnRandomEnemies
  """

  range_end: int = 100
  display_name: str = "SpawnRandomEnemies"
  default: bool = option_presets["main"]["spawn_random_enemies"]

class ProgressiveWeapons(Toggle):
  """
  ProgressiveWeapons
  """

  display_name: str = "ProgressiveWeapons"
  default: bool = option_presets["main"]["progressive_weapons"]
class ProgressiveArmor(Toggle):
  """
  ProgressiveArmor
  """

  display_name: str = "ProgressiveArmor"
  default: bool = option_presets["main"]["progressive_armor"]


class Nothing(Range):
  """
  Nothing
  """

  range_end: int = 100
  display_name: str = "Nothing"
  default: bool = option_presets["main"]["nothing"]


class AllowClips(OptionDict):
  """
  AllowClips
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


# If we want to group our options by similar type, we can do so as well. This looks nice on the website.
option_groups: list[OptionGroup] = [
  OptionGroup(
    "Gameplay Options",
    [
      # ItemRando,
      EntranceRando,
      DeathLink,
    ],
  ),
  # OptionGroup(
  #   "Check Options",
  #   [
  #     EachQuestIsACheck,
  #   ],
  # ),
  # OptionGroup(
  #   "Glitch Options",
  #   [
  #     # AllowClips,
  #   ],
  # ),
  OptionGroup(
    "Win Options",
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
    ],
  ),
]
