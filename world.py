from collections.abc import Mapping
from typing import ClassVar, cast, override

from Options import PerGameCommonOptions
from worlds.AutoWorld import WebWorld, World

from . import items, locations, regions, rules, web_world
from . import options as MathQuest_options


class MathQuestWorld(World):
  """
  MathQuest is a minimal 8bit-era inspired adventure game with grid-like movement.
  Good games don't need more than six checks.
  """

  # The docstring should contain a description of the game, to be displayed on the WebHost.

  # You must override the "game" field to say the name of the game.
  game: ClassVar[str] = "MathQuest"

  # The WebWorld is a definition class that governs how this world will be displayed on the website.
  web: ClassVar[WebWorld] = web_world.MathQuestWebWorld()

  # This is how we associate the options defined in our options.py with our world.
  # (Note: options.py has been imported as "MathQuest_options" at the top of this file to avoid a name conflict)
  options_dataclass: ClassVar[type[PerGameCommonOptions]] = cast(
    type[PerGameCommonOptions], MathQuest_options.MathQuestOptions
  )
  options: MathQuest_options.MathQuestOptions

  # Our world class must have a static location_name_to_id and item_name_to_id defined.
  # We define these in regions.py and items.py respectively, so we just set them here.
  location_name_to_id: ClassVar[dict[str, int]] = locations.LOCATION_NAME_TO_ID
  item_name_to_id: ClassVar[dict[str, int]] = items.ITEM_NAME_TO_ID

  # There is always one region that the generator starts from & assumes you can always go back to.
  # This defaults to "Menu", but you can change it by overriding origin_region_name.
  origin_region_name: str = "20_20: south 0"

  # Our world class must have certain functions ("steps") that get called during generation.
  # The main ones are: create_regions, set_rules, create_items.
  # For better structure and readability, we put each of these in their own file.
  @override
  def create_regions(self) -> None:
    regions.create_and_connect_regions(self)
    locations.create_all_locations(self)

  @override
  def set_rules(self) -> None:
    rules.set_all_rules(self)

  @override
  def create_items(self) -> None:
    items.create_all_items(self)

  # Our world class must also have a create_item function that can create any one of our items by name at any time.
  # We also put this in a different file, the same one that create_items is in.
  @override
  def create_item(self, name: str) -> items.MathQuestItem:
    return items.create_item_with_correct_classification(self, name)

  # For features such as item links and panic-method start inventory, AP may ask your world to create extra filler.
  # The way it does this is by calling get_filler_item_name.
  # For this purpose, your world *must* have at least one infinitely repeatable item (usually filler).
  # You must override this function and return this infinitely repeatable item's name.
  # In our case, we defined a function called get_random_filler_item_name for this purpose in our items.py.
  @override
  def get_filler_item_name(self) -> str:
    return items.get_random_filler_item_name(self)

  # There may be data that the game client will need to modify the behavior of the game.
  # This is what slot_data exists for. Upon every client connection, the slot's slot_data is sent to the client.
  # slot_data is just a dictionary using basic types, that will be converted to json when sent to the client.
  @override
  def fill_slot_data(self) -> Mapping[str, bool]:
    # If you need access to the player's chosen options on the client side, there is a helper for that.
    return self.options.as_dict(*MathQuest_options.option_presets["main"].keys())
