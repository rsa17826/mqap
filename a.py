from collections import Counter
from _progression import PROG

pairs = Counter()

for thing in PROG:
  if "receive" not in thing:
    continue

  room = f"{thing['room']['north']}_{thing['room']['east']}"

  for item in thing["requires"]:
    for i in item:
      if not i.startswith(("food:", "magic:", "weapon:", "skill:", "flag:", "quest:", "area:", "loot:", "item:", "entr", "armor:", "misc:", "permit:")):
        print(i)



