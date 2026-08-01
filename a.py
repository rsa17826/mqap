from collections import Counter
from _progression import PROG
pairs = Counter()

for thing in PROG:
  if "receive" not in thing:
    continue

  room = f"{thing['room']['north']}_{thing['room']['east']}"

  for item in thing["receive"]:
    if item.startswith(("food:cherries", "food:gingerBread", "food:holyWater")):
      pairs[(room, item)] += 1



for pair, count in pairs.items():
  if count > 1:
    print(pair, count)

