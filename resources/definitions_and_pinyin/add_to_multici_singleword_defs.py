from glob import glob

ZIDEF = []
mothership = "resources/definitions_and_pinyin/multizi_singleword_defs.tsv"
with open(mothership, "r") as f:
  for i, line in enumerate(f):
    if not line.strip(): continue
    try:
      zi, deff = line.strip().split("\t")
    except Exception as e:
      print(f"line={i}; vim {mothership}", e)
      raise ValueError("oops")
    ZIDEF.append((zi, deff))

ZIDEF_DICT = dict(ZIDEF)
NEW_ZIDEF = []
for fname in glob("output/*multici*"):
  with open(fname, "r") as f:
    for i, line in enumerate(f):
      parts = line.strip().split("\t")
      if len(parts) != 2:
        print(f"line {i} bad line:", parts, fname)
      if parts[0] in ZIDEF_DICT: continue
      NEW_ZIDEF.append(line)

with open(mothership, "a") as f:
  for line in NEW_ZIDEF:
    f.write(line)



