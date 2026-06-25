from _progression import PROG


def find_unrewarded_requirements(data):
  all_requires = set()
  all_receives = set()

  for entry in data:
    # Collect all receives (flattening the list)
    if "receive" in entry:
      for item in entry["receive"]:
        item = item.split("#")[0]
        if "entrance" not in item:
          all_receives.add(item)

    # Collect all requires (flattening the nested lists)
    if "requires" in entry:
      for sublist in entry["requires"]:
        for item in sublist:
          item = item.split("#")[0]
          if "entrance" not in item:
            all_requires.add(item)

  # Find requirements that are NOT in the receives set
  unrewarded = all_requires - all_receives

  return sorted(list(unrewarded))


# Run the function and print the results
missing_requirements = find_unrewarded_requirements(PROG)

print("Requirements that are not in receives:")
for item in missing_requirements:
  print(f"- {item}")
