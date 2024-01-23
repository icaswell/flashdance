import regex as re
import csv

fname="output/hsk1to6.tsv__gpt-3.5-turbo-1106_t0.0__related_words_prompt__full.txt"
ofname="resources/hsk1to6.tsv__gpt-3.5-turbo-1106_t0.0__related_words_prompt.csv"

# consider removing all explanations with:
# "have their own nuances and usage."
# have their own specific meanings and usage.


EXPLANATIONS = [['', '']]
with open(fname, "r") as f:
  for line in f:
    if "word,synonym(s),explanation of differences" in line: continue
    if not line.strip(): continue
    m = re.match("^([\p{Han}]*),([\p{Han};]*),(.*)", line)
    if m:
      ci, syns, explanation_start = m.groups()
      if explanation_start.startswith('"'):
        explanation_start = explanation_start[1:] + "\n"
      EXPLANATIONS.append([ci, explanation_start])
    else:
      EXPLANATIONS[-1][1] += line

EXPLANATIONS = [[ci, re.sub('"[ \n]*$', '', exp).replace('""', '"')] for ci, exp in EXPLANATIONS]
EXPLANATIONS = [[ci, re.sub('\n(\p{Han})', '\n\n\\1', exp)] for ci, exp in EXPLANATIONS]

for i in range(3000):
  if i >= len(EXPLANATIONS): break
  if not i: continue
  print("\n\n#==================================#")
  print(f"# {i}")
  print(">>>", EXPLANATIONS[i][0])
  print(EXPLANATIONS[i][1])

with open(ofname, 'w') as csvfile:
  csvwriter = csv.writer(csvfile, delimiter =';', quoting=csv.QUOTE_ALL)
  csvwriter.writerows(EXPLANATIONS)

print(fname)
print(ofname)
