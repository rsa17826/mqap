from dataclasses import dataclass
from typing import ClassVar

from Options import OptionDict, OptionGroup, PerGameCommonOptions, Toggle

# In this file, we define the options the player can pick.
# The most common types of options are Toggle, Range and Choice.

# Options will be in the game's template yaml.
# They will be represented by checkboxes, sliders etc. on the game's options page on the website.
# (Note: Options can also be made invisible from either of these places by overriding Option.visibility.
#  MathQuest doesn't have an example of this, but this can be used for secret / hidden / advanced options.)

# For further reading on options, you can also read the Options API Document:
# https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/options%20api.md


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


class DeathLink(Toggle):
  """
  DeathLink
  """

  display_name: str = "DeathLink"


class ItemRando(Toggle):
  """
  ItemRando
  """

  display_name: str = "ItemRando"


class ThreeOrbs(Toggle):
  """
  ThreeOrbs
  """

  display_name: str = "ThreeOrbs"


class FinalBoss(Toggle):
  """
  FinalBoss
  """

  display_name: str = "FinalBoss"


class EachQuestIsACheck(Toggle):
  """
  EachQuestIsACheck
  """

  display_name: str = "EachQuestIsACheck"


class AllQuestsMaxed(Toggle):
  """
  AllQuestsMaxed
  """

  display_name: str = "AllQuestsMaxed"


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
  three_orbs: ThreeOrbs
  final_boss: FinalBoss
  death_link: DeathLink
  each_quest_is_a_check: EachQuestIsACheck
  allow_clips: AllowClips
  all_quests_maxed: AllQuestsMaxed


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
      # ThreeOrbs,
      AllQuestsMaxed,
      FinalBoss,
    ],
  ),
]

# Finally, we can define some option presets if we want the player to be able to quickly choose a specific "mode".
option_presets: dict[str, dict[str, bool | int]] = {
  "main": {
    # "item_rando": True,
    "entrance_rando": False,
    "three_orbs": True,
    "final_boss": True,
    "death_link": True,
    "all_quests_maxed": False,
    # "allow_clips": 0,
    # "each_quest_is_a_check": False,
  },
}
