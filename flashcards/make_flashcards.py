import csv
import regex as re
import pinyin_jyutping_sentence


# fname="/Users/icaswell/Documents/dancing_miao/flashcards/sample1.csv"
fname_out="flashcards/sample1.flashcards.csv"


# TSV: first col is the target ci
input_ci_fname = "resources/hsk1to6_zi_pinyin_def_sample.tsv"

# TSV: maps ci to (short) definition
definitions_fname = "resources/hsk1to6_zi_pinyin_def.tsv"

pinyin_fname = "resources/hsk1to6_zi_pinyin_def.tsv"
zi_definitions_fname = "resources/zi_singleword_defs.tsv"
use_same_zi_fname = "resources/use_same_zi/mega_hanzi.tsv"

# relatedwords_fname = "resources/related_words/hsk1to6.tsv"
relatedwords_explanation_fname = "resources/hsk1to6.tsv__gpt-3.5-turbo-1106_t0.0__related_words_prompt.csv"
examples_fnames = [
        ["🐇", 2, "resources/example_sentences/cql.tsv"]
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
      DEFINITIONS[parts[0]] = parts[2]
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

EXAMPLES = {}
for example_emoji, n_examples, examples_fname in examples_fnames:
  with open(examples_fname, "r") as f:
    for line in f:
      if "\t" not in line:
        # print(line)
        continue
      ci, content = line.strip().split("\t", maxsplit=1)
      content = content.split("\t")
      if len(content)%2 != 0:
          # print(content)
          content = content[0:-1]
      if ci not in EXAMPLES:
        EXAMPLES[ci] = {"zh": [], "en": []}
      for i, example in enumerate(content):
        if i%2 == 0: EXAMPLES[ci]["zh"].append(f"{example_emoji} {example}")
        if i%2 == 1: EXAMPLES[ci]["en"].append(example)
print("EXAMPLES" + "\n"); somple(EXAMPLES)


# def bold_han(s):
#   # return s
#   return re.sub("- (\p{Han}+( \([^\)]*\):)?)", "\r\\1\r", s)
#   return re.sub("(\p{Han}+( \([^\)]*\):)?)", "**\\1**", s)


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
    if "missing" not in resource:
      resource["missing"] = []
    resource["missing"].append(ci)
    if field_name is not None:
      return True
    return False
  

out_lines = []
for ci_j in TARGET_CI:
  out_line = [[ci_j]]
  if not conditional_append(ci_j, PINYIN, out_line): continue
  if not conditional_append(ci_j, DEFINITIONS, out_line): continue
  if not conditional_append(ci_j, RELATED_WORDS, out_line, "related words"): pass

  for zi_j in ci_j:
    if zi_j in ZI_DEFS: out_line[0].append(f"{zi_j} ({ZI_DEFS[zi_j]})")
    else: out_line[0].append(f"{zi_j}")

    other_ci_list = []
    other_ci_superset = USE_SAME_ZI[zi_j].split(";") if zi_j in USE_SAME_ZI else []
    for ci_k in other_ci_superset:
      ci_k = ci_k.strip()
      if ci_k == ci_j: continue
      if len(ci_k) > 4: continue
      if ci_k in PINYIN: ci_k = f"{ci_k} ({PINYIN[ci_k]})"
      other_ci_list.append(ci_k)
    if other_ci_list:
      out_line[0].append("Other words using this character: " + "; ".join(other_ci_list))
    else:
      out_lines[0].append("There are no other HSK words in this level (or before) using this character.")


  if ci_j not in EXAMPLES:
    if "missing" not in EXAMPLES:
      EXAMPLES["missing"] = []
      EXAMPLES["missing"].append(ci_j)
  else:
    seen_examples = set()
    for ex_zh, ex_en in zip(EXAMPLES[ci_j]["zh"], EXAMPLES[ci_j]["en"]):
      if ex_zh in seen_examples: continue
      seen_examples.add(ex_zh)
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

missing = TARGET_CI - DEFINITIONS.keys() 
print(f"missing from DEFINITIONS: {'; '.join(missing)}\n")

missing = TARGET_CI - PINYIN.keys() 
print(f"missing from PINYIN: {'; '.join(missing)}\n")


missing = TARGET_CI - RELATED_WORDS.keys() 
print(f"missing from RELATED_WORDS: {'; '.join(missing)}\n")

missing = TARGET_CI - EXAMPLES.keys() 
print(f"missing from EXAMPLES: {'; '.join(missing)}\n")



print(f"missing from ZI_DEFS: {ZI_DEFS.get('missing', [])}\n")
print(f"missing from USE_SAME_ZI: {USE_SAME_ZI.get('missing', [])}\n")
