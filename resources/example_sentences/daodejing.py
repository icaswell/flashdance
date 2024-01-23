import regex as re
from collections import defaultdict

with open("resources/vocab_combined/all_ci.tsv", "r") as f:
  ALL_CI = {line.split("\t")[0] for line in f}

with open("resources/daodejing.raw.txt", "r") as f:
  lines = [line.replace("\n", "") for line in f]


def is_zh_line(line):
  s = re.sub("[_(•)\[\] ]", "", line)
  if re.match("^[\p{Han}]", s): return True
  return False


zh = []
en = []
section = "zh"
CHAPTERS = []
for line in lines:
  if not line.strip(): continue
  if line.startswith("Notes :"):
    section = "notes"
    continue
  if line.startswith("Chapter"):
    CHAPTERS.append((zh, en))
    section = "zh"
    zh = []
    en = []
  elif section == "zh":
    if is_zh_line(line):
      zh.append(re.sub("[(•) ]", "", line))
    else:
      section = "en"
      en.append(line)
  elif section == "en":
    if len(en) == len(zh) : continue
    if line.startswith(" "):
      en[-1] += line.strip()
    else:
      en.append(line)

def pront(zh, en):
  for i in range(max(len(en), len(zh))):
    zhi = zh[i] if i < len(zh) else "-"
    eni = en[i] if i < len(en) else "-"
    print(f"{zhi}========={eni}")

for zh, en in CHAPTERS:
  print(len(zh), len(en))
  pront(zh, en)
  print("\n\n")

EXAMPLES = {}# defaultdict(list)
for ci in ALL_CI:
  exomples = []
  for i, (zh, en) in enumerate(CHAPTERS):
    for zhi, eni in zip(zh, en):
      if not zhi or not eni: continue
      if ci not in zhi: continue
      exomples.append((zhi, eni))
  if exomples:
    EXAMPLES[ci] = exomples


# # print(CHAPTERS[0])
# with open("resources/daodejing.tsv", "w") as f:
#   for i, (zh, en) in enumerate(CHAPTERS):
#     for zhi, eni in zip(zh, en):
#       # f.write(f"{zhi}\t{eni}\t{i+1}\n")
#       f.write(f"{zhi}\t{eni.strip()} (Chapter {i+1})\n")
# print(CHAPTERS[0])
with open("resources/example_sentences/daodejing.tsv", "w") as f:
  for ci, exomples in EXAMPLES.items():
    f.write(ci)
    # print(exomples)
    for zhi, eni in exomples:
      f.write(f"\t{zhi}\t{eni}")
    f.write("\n")
print("resources/example_sentences/daodejing.tsv")
