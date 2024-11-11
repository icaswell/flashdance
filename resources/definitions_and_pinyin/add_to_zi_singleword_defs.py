from glob import glob

ZIDEF = []
mothership = "resources/definitions_and_pinyin/zi_singleword_defs.tsv"
with open(mothership, "r") as f:
  for line in f:
    zi, deff = line.strip().split("\t")
    ZIDEF.append((zi, deff))

ZIDEF_DICT = dict(ZIDEF)
NEW_ZIDEF = []
for fname in glob("output/zi_defs.*"):
  with open(fname, "r") as f:
    for line in f:
      parts = line.strip().split("\t")
      if len(parts) != 2:
        print("Error:", parts, fname)
        continue
      if parts[0] in ZIDEF_DICT: continue
      NEW_ZIDEF.append(line)

with open(mothership, "a") as f:
  for line in NEW_ZIDEF:
    f.write(line)



