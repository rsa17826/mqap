import sys

from _progression import PROG


def find_providers(required_item):
  """Finds all nodes/rooms that provide the specified item."""
  providers = []
  clean_req = required_item.split("#")[0]
  for node in PROG:
    for item in node.get("receive", []):
      if item.split("#")[0] == clean_req:
        providers.append(node)
  return providers


def find_room_by_location_string(search_str):
  """If the user enters '13_16 - weapon:survival knife', finds that specific room node."""
  # Try parsing coordinate prefix like '13_16'
  parts = search_str.split(" - ")
  if len(parts) > 1 and "_" in parts[0]:
    coord_part = parts[0]
    item_part = parts[1].split("#")[0]
    try:
      n_str, e_str = coord_part.split("_")
      north = float(n_str) if "." in n_str else int(n_str)
      east = float(e_str) if "." in e_str else int(e_str)

      for node in PROG:
        if node["room"]["north"] == north and node["room"]["east"] == east:
          if any(item.split("#")[0] == item_part for item in node.get("receive", [])):
            return node, item_part
    except ValueError:
      pass

  # Fallback: treat the entire string as the target item name
  return None, search_str.split("#")[0]


def trace_item_logic(target_item, current_node=None, visited=None, depth=0):
  if visited is None:
    visited = set()

  indent = "  " * depth
  clean_target = target_item.split("#")[0]

  # Base skip for special flags/areas that might not be items
  if clean_target in visited:
    print(f"{indent}  🔄 Circular dependency detected for '{clean_target}'!")
    return
  visited.add(clean_target)

  # If we specified a target room node directly, use it first; otherwise find all providers
  if current_node:
    providers = [current_node]
  else:
    providers = find_providers(clean_target)

  if not providers:
    print(f"{indent}  ❌ NO PROVIDER FOUND for '{clean_target}' (Is it an item pool issue, or missing logic?)")
    return

  for node in providers:
    room_str = f"{node['room']['north']}_{node['room']['east']}"
    print(f"{indent}  ↳ Checked Room [{room_str}] providing '{clean_target}'")

    requires_clauses = node.get("requires", [])
    if not requires_clauses or requires_clauses == [[]]:
      print(f"{indent}    🔓 Accessible from start! (No requirements)")
      continue

    print(f"{indent}    🔒 Locked by Requirements (OR conditions):")
    for i, and_list in enumerate(requires_clauses):
      print(f"{indent}      Alternative Path {i + 1} (All items below required):")
      for req in and_list:
        # Recursively trace what blocks this requirement
        trace_item_logic(req, current_node=None, visited=visited.copy(), depth=depth + 4)


if __name__ == "__main__":
  search_query = input("Enter item or location (e.g. '13_16 - weapon:survival knife'): ").strip()

  print("\n" + "=" * 70)
  print(f"DIAGNOSTIC LOGIC TRACE FOR: {search_query}")
  print("=" * 70)
  # Temporary debug snippet to print out raw requirements of 13_16
  for node in PROG:
      if node["room"]["north"] == 13 and node["room"]["east"] == 16:
          print("Raw Requirements for 13_16:", node.get("requires"), node.get("receive"))
  # Match room specific node if coordinates given
  specific_node, target_item_name = find_room_by_location_string(search_query)

  trace_item_logic(target_item_name, current_node=specific_node)
