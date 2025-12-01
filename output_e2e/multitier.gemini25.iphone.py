from collections import Counter

c = Counter()
with open("multitier.gemini25.iphone.csv", "r") as f:
  for i, line in enumerate(f):
    cat = line.split('";"')[0:-2]
    c[cat] += 1

f

