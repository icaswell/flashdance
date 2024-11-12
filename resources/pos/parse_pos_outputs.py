from glob import glob

POS = []
mothership = "resources/pos/pos.tsv"
with open(mothership, "r") as f:
  for i, line in enumerate(f):
    if not line.strip(): continue
    try:
      zi, deff = line.strip().split("\t")
    except Exception as e:
      print(f"line={i}; vim {mothership}", e)
      raise ValueError("oops")
    POS.append((zi, deff))

POS_DICT = dict(POS)
NEW_POS = []
for fname in glob("output/pos*"):
  with open(fname, "r") as f:
    for i, line in enumerate(f):
      if not line.strip(): continue
      parts = line.strip().split("\t")
      if len(parts) != 2:
        print(f"line {i} bad line:", parts, fname)
      if parts[0] in POS_DICT: continue
      NEW_POS.append(line)

with open(mothership, "a") as f:
  for line in NEW_POS:
    f.write(line)



