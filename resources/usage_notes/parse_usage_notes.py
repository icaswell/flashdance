from glob import glob
import regex as re


HAN_REGEX_INC = "[《\p{Han}0-9““<>]"


NEWLINE = "<NEWLINE>"
DELIM = "~"  # input delimitor
USAGE = []
mothership = "resources/usage_notes/usage_notes.tsv"
with open(mothership, "r") as f:
  for line in f:
    ci, note = line.strip().split("\t")
    USAGE.append((ci, note))

USAGE_DICT = dict(USAGE)
NEW_USAGE = []
for fname in glob("output/usage_notes.*"):
  with open(fname, "r") as f:
    content = f.read()
    for chunk in content.split(DELIM):
      chunk = chunk.strip()
      lines =  chunk.split("\n")
      if "\t" in chunk:
        print("Error[TABS]:", chunk.replace("\t", "<TAB>"), fname)
        continue
      if len(lines) < 2:
        print("Error[short]:", chunk, fname)
        continue
      ci = lines[0]
      if not re.search(HAN_REGEX_INC, ci):
        print("Error[ci is not in Hanzi]:", chunk, fname)
        continue
      if ci in USAGE_DICT: continue
      note = chunk.split("\n", maxsplit=1)[1]
      note = note.replace("\n", NEWLINE)
      line = f"{ci}\t{note}\n"
      NEW_USAGE.append(line)

with open(mothership, "a") as f:
  for line in NEW_USAGE:
    f.write(line)



