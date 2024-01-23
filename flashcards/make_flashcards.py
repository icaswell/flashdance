import csv
import regex as re
import pinyin_jyutping_sentence
import random
from collections import defaultdict


# fname="/Users/icaswell/Documents/dancing_miao/flashcards/sample1.csv"
fname_out="flashcards/sample1.flashcards.csv"


# TSV: first col is the target ci
input_ci_fname = "resources/definitions_and_pinyin/hsk1to6_zi_pinyin_def_sample.tsv"

# TSV: maps ci to (short) definition
definitions_fname = "resources/definitions_and_pinyin/hsk1to6_zi_pinyin_def.tsv"

pinyin_fname = "resources/definitions_and_pinyin/hsk1to6_zi_pinyin_def.tsv"
zi_definitions_fname = "resources/definitions_and_pinyin/zi_singleword_defs.tsv"
multizi_definitions_fname = "resources/definitions_and_pinyin/all_multici.tsv__gpt-3.5-turbo-1106_t0.0_c40__multizi_prompt.txt"
use_same_zi_fname = "resources/use_same_zi/mega_hanzi.tsv"

# relatedwords_fname = "resources/related_words/hsk1to6.tsv"
relatedwords_explanation_fname = "resources/hsk1to6.tsv__gpt-3.5-turbo-1106_t0.0__related_words_prompt.csv"

# https://en.wikipedia.org/wiki/List_of_Unicode_characters#Miscellaneous_Symbols
examples_fnames = [
        ["❈", 3, "resources/example_sentences/general.tsv"],  # ❈ is "heavy sparkle"
        ["🐇", 2, "resources/example_sentences/cql.tsv"],
        ["☯", 2, "resources/example_sentences/daodejing.tsv"]
        # ☯️ ☯ ☾𖤓࿊
        # ☯
        # 
    #   𓆝 𓆟 𓆞 𓆝 𓆟
     
]
NEWLINE = "\r"

def somple(X):
  x = list(X.items())
  print("\n=================================")
  print(x[0:5], x[-5:])

TARGET_CI = []
with open(input_ci_fname, "r") as f:
  for line in f:
    TARGET_CI.append(line.strip().split("\t")[0])

DEFINITIONS = {}
with open(definitions_fname, "r") as f:
  for line in f:
    parts = line.strip().split("\t")
    if len(parts) >=3:
      deff = parts[2]
      if deff.startswith("/"):
        deff = deff[1:-1].replace("/", "; ")
      DEFINITIONS[parts[0]] = deff
print("DEFINITIONS" + "\n"); somple(DEFINITIONS)

PINYIN = {}
with open(pinyin_fname, "r") as f:
  for line in f:
    parts = line.strip().split("\t")
    PINYIN[parts[0]] = parts[1]
print("PINYIN" + "\n"); somple(PINYIN)

ZI_DEFS = {}
with open(zi_definitions_fname, "r") as f:
  for line in f:
    parts = line.strip().split("\t")
    ZI_DEFS[parts[0]] = parts[1]
print("ZI_DEFS" + "\n"); somple(ZI_DEFS)

with open(multizi_definitions_fname, "r") as f:
  for line in f:
    parts = line.strip().split("\t")
    ZI_DEFS[parts[0]] = parts[1]
print("ZI_DEFS" + "\n"); somple(ZI_DEFS)


# i zi  first_occurence hsk1  hsk2  hsk3  hsk4  hsk5  hsk6  nhsk1 nhsk2 nhsk3 nhsk4 nhsk5 nhsk6 stront1 weeb1  
USE_SAME_ZI = {}
with open(use_same_zi_fname, "r") as f:
  for line in f:
    parts = line.strip().split("\t")
    USE_SAME_ZI[parts[1]] = parts[-1]  # TODO handle logic for only the level below and equal
print("USE_SAME_ZI" + "\n"); somple(USE_SAME_ZI)

# RELATED_WORDS = {}
# with open(relatedwords_fname, "r") as f:
#   for line in f:
#     parts = line.strip().split("\t")
#     RELATED_WORDS[parts[0]] = parts[1]
# somple(RELATED_WORDS)

RELATED_WORDS = {}
with open(relatedwords_explanation_fname, "r") as f:
  reader = csv.reader(f, delimiter=';')
  for row in reader:
    RELATED_WORDS[row[0]] = row[1]
print("RELATED_WORDS" + "\n"); somple(RELATED_WORDS)

EXAMPLES = defaultdict(list)
for example_emoji, n_examples, examples_fname in examples_fnames:
  with open(examples_fname, "r") as f:
    for line in f:
      if "\t" not in line:
        continue
      ci, content = line.strip().split("\t", maxsplit=1)
      content = content.split("\t")
      # NB: this is silent failing and maybe a bad idea
      if len(content)%2 != 0:  
        content = content[0:-1]
      paired_examples = []
      for i, example in enumerate(content):
        if i%2 == 0:
          paired_examples.append([example])
        if i%2 == 1:
          paired_examples[-1].append(example)
      random.shuffle(paired_examples)
      for zhex, enex in paired_examples[0:n_examples]:
        if ci not in zhex: continue
        EXAMPLES[ci].append((example_emoji, zhex, enex))
print("EXAMPLES" + "\n"); somple(EXAMPLES)


INVERTED_EXAMPLES = defaultdict(list)
for ci in TARGET_CI:
  for cj, example_tups in EXAMPLES.items():
    for example_emoji, zhex, enex in example_tups:
      if cj == ci: continue
      if ci in zhex:
        # INVERTED_EXAMPLES[ci].append(("⏿" + example_emoji, zhex, enex))
        INVERTED_EXAMPLES[ci].append(("♻" + example_emoji, zhex, enex))
print("EXAMPLES" + "\n"); somple(EXAMPLES)

for ci, example_tups in INVERTED_EXAMPLES.items():
  EXAMPLES[ci] += example_tups

def pinyin(s):
  p =  pinyin_jyutping_sentence.pinyin(s)
  p = p.replace(" huán ", " hái ")
  p = p.replace(" dū ", " dōu ")
  return p

def conditional_append(ci, resource, out_line, field_name=None):
  if ci in resource:
    if field_name: out_line[0].append(field_name)
    out_line[0].append(resource[ci])
    return True
  else:
    if field_name is not None:
      return True
    return False


def get_other_ci_list(zi_j):
  other_ci_list = []
  other_ci_superset = USE_SAME_ZI[zi_j].split(";") if zi_j in USE_SAME_ZI else []
  for ci_k in other_ci_superset:
    ci_k = ci_k.strip()
    if ci_k == ci_j: continue
    if len(ci_k) > 4: continue
    addenda = []

    if ci_k in PINYIN:
      addenda.append(PINYIN[ci_k])
    if ci_k in ZI_DEFS:
      addenda.append(ZI_DEFS[ci_k])
    if addenda:
      ci_k = f"{ci_k} ({'; '.join(addenda)})"
    other_ci_list.append(ci_k)
  return other_ci_list

out_lines = []
for ci_j in TARGET_CI:
  out_line = [[ci_j]]
  if not conditional_append(ci_j, PINYIN, out_line): continue
  if not conditional_append(ci_j, DEFINITIONS, out_line): continue
  if not conditional_append(ci_j, RELATED_WORDS, out_line, "related words"): pass

  for zi_j in ci_j:
    other_ci_list = get_other_ci_list(zi_j)
    zi_j_decorated = f"{zi_j} ({ZI_DEFS[zi_j]})" if zi_j in ZI_DEFS else zi_j
    content = "There are no other HSK words in this level (or before) using this character."
    if other_ci_list:
      content = "Other words using this character: " + "; ".join(other_ci_list)
    out_line[0].append(zi_j_decorated)
    out_line[0].append(content)


  if ci_j in EXAMPLES:
    seen_examples = set()
    for ex_zh, ex_en, ex_emoji in EXAMPLES[ci_j]:
      if ex_zh in seen_examples: continue
      seen_examples.add(ex_zh)
      ex_en = pinyin(ex_zh) + NEWLINE + ex_en
      ex_zh = f"{ex_emoji} {ex_zh}"
      out_line[0].append(ex_zh)
      out_line[0].append(ex_en)
  out_lines.append(out_line[0])

print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
for xx in out_lines:
    print(xx)
  
out_lines = [
        [field.replace("\n", NEWLINE) for field in out_line]
        for out_line in out_lines
        ]

# writing to csv file
with open(fname_out, 'w') as csvfile:
  csvwriter = csv.writer(csvfile, delimiter =';', quoting=csv.QUOTE_ALL)
  csvwriter.writerows(out_lines)



TARGET_CI = set(TARGET_CI)
TARGET_ZI = {zi for ci in TARGET_CI for zi in ci}

missing = TARGET_CI - DEFINITIONS.keys() 
print(f"missing from DEFINITIONS: {'; '.join(missing)}\n")

missing = TARGET_CI - PINYIN.keys() 
print(f"missing from PINYIN: {'; '.join(missing)}\n")
missing = TARGET_ZI - PINYIN.keys() 
print(f"missing from PINYIN (ZI): {'; '.join(missing)}\n")

missing = TARGET_CI - RELATED_WORDS.keys() 
print(f"missing from RELATED_WORDS: {'; '.join(missing)}\n")

missing = TARGET_CI - EXAMPLES.keys() 
print(f"missing from EXAMPLES: {'; '.join(missing)}\n")

missing = TARGET_ZI - ZI_DEFS.keys() 
print(f"missing from ZI_DEFS: {'; '.join(missing)}\n")

missing = TARGET_ZI - USE_SAME_ZI.keys() 
print(f"missing from USE_SAME_ZI: {'; '.join(missing)}\n")


