import csv
import regex as re
import pinyin_jyutping_sentence
import random
from collections import defaultdict
import argparse

parser = argparse.ArgumentParser(description='Process input file and save the result to an output file.')
parser.add_argument('--level', type=str)
parser.add_argument('--mode', type=str)
args = parser.parse_args()


definitions_fname = "resources/definitions_and_pinyin/hsk1to6strontweeb_zi_pinyin_def.tsv"

pinyin_fname = "resources/vocab_combined/all_ci_and_zi_pinyin.tsv"
zi_definitions_fname = "resources/definitions_and_pinyin/zi_singleword_defs.tsv"
multizi_definitions_fname = "resources/definitions_and_pinyin/all_multici.tsv__gpt-3.5-turbo-1106_t0.0_c40__multizi_prompt.txt"
use_same_zi_fname = "resources/use_same_zi/mega_hanzi.tsv"

# relatedwords_fname = "resources/related_words/hsk1to6.tsv"
relatedwords_explanation_fname = "resources/hsk1to6.tsv__gpt-3.5-turbo-1106_t0.0__related_words_prompt.csv"

# https://en.wikipedia.org/wiki/List_of_Unicode_characters#Miscellaneous_Symbols
examples_fnames = [
        ["❈", 3, "resources/example_sentences/general.tsv"],  # ❈ is "heavy sparkle"
        ["🐇", 2, "resources/example_sentences/cql.tsv"],
        # ["☯", 2, "resources/example_sentences/daodejing.tsv"]
        # ☯️ ☯ ☾𖤓࿊
        #   𓆝 𓆟 𓆞 𓆝 𓆟
]
OBFUSTICATOR = "⠀" # invisible character to prevent deduping
MAX_EXAMPLES = 20
MAX_EXAMPLES = 12

BREAK_INTO_N_CHUNKS = 1

if args.mode == "android":
  if args.level == "hsk4":
    MAX_EXAMPLES = 6
  if args.level == "hsk5":
    examples_fnames[1][1] = 1
    MAX_EXAMPLES = 5
    BREAK_INTO_N_CHUNKS = 2
  if args.level == "hsk6":
    examples_fnames[1][1] = 1
    MAX_EXAMPLES = 5
    BREAK_INTO_N_CHUNKS = 6
  if args.level == "weeb1":
    MAX_EXAMPLES = 6
    BREAK_INTO_N_CHUNKS = 4

if args.mode == "iphone":
   NEWLINE = "\r"
   format_pinyin = lambda x: f"【{pinyin(x)}】"
elif args.mode == "android":
   NEWLINE = "<br></br>"
   format_pinyin = lambda x: f"<i>{pinyin(x)}</i>"
else:
  raise ValueError("argh")


LEVELS = {
    "hsk1": 1,
    "hsk2": 2,
    "hsk3": 3,
    "hsk4": 4,
    "hsk5": 5,
    "hsk6": 6,
    "stront1": 6,
    "weeb1": 6,
}


LEVELED_CI = defaultdict(list)

ALL_ZI_IN_LEVELS = set()
for level in LEVELS:
  with open(f"resources/vocab_separate/{level}.tsv", "r") as f:
    for line in f:
      ci, _, _ = line.split("\t", maxsplit=2)
      LEVELED_CI[level].append(ci)
      ALL_ZI_IN_LEVELS |= {zi for zi in ci}

# zi: {level_name: [ci]}
ZI_TO_LEVELED_CI = defaultdict(lambda: defaultdict(list))
for zi in ALL_ZI_IN_LEVELS:
  for level_name in LEVELS:
    applicable_levels = {lev for lev in LEVELS if LEVELS[lev] <= LEVELS[level_name]}
    for lev in applicable_levels:
      for ci in LEVELED_CI[lev]:
        if zi in ci:
          ZI_TO_LEVELED_CI[zi][level_name].append(ci)
# for lev in ZI_TO_LEVELED_CI["人"]:
#     print(lev)
#     print(ZI_TO_LEVELED_CI["人"][lev])

def somple(X):
  pass
  # x = list(X.items())
  # print("\n=================================")
  # print(x[0:5], x[-5:])

TARGET_CI = []
with open(f"resources/vocab_separate/{args.level}.tsv", "r") as f:
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
# print("DEFINITIONS" + "\n"); somple(DEFINITIONS)

PINYIN = {}
with open(pinyin_fname, "r") as f:
  for i, line in enumerate(f):
    parts = line.strip().split("\t")
    if len(parts) != 2: print(i, line)
    else: PINYIN[parts[0]] = parts[1]
# print("PINYIN" + "\n"); somple(PINYIN)

ZI_DEFS = {}
with open(zi_definitions_fname, "r") as f:
  for line in f:
    parts = line.strip().split("\t")
    ZI_DEFS[parts[0]] = parts[1]
# print("ZI_DEFS" + "\n"); somple(ZI_DEFS)

with open(multizi_definitions_fname, "r") as f:
  for line in f:
    parts = line.strip().split("\t")
    ZI_DEFS[parts[0]] = parts[1]
# print("ZI_DEFS" + "\n"); somple(ZI_DEFS)


# # i zi  first_occurence hsk1  hsk2  hsk3  hsk4  hsk5  hsk6  nhsk1 nhsk2 nhsk3 nhsk4 nhsk5 nhsk6 stront1 weeb1  
# USE_SAME_ZI = {}
# with open(use_same_zi_fname, "r") as f:
#   for line in f:
#     parts = line.strip().split("\t")
#     USE_SAME_ZI[parts[1]] = parts[-1]  # TODO handle logic for only the level below and equal
# print("USE_SAME_ZI" + "\n"); somple(USE_SAME_ZI)

# RELATED_WORDS = {}
# with open(relatedwords_fname, "r") as f:
#   for line in f:
#     parts = line.strip().split("\t")
#     RELATED_WORDS[parts[0]] = parts[1]
# somple(RELATED_WORDS)


def format_related_words(s):
  f = re.findall("([^\)])\n([A-Za-z, ]{0,20}(oth |summary|example|hese words|hese two words|The words|While|So, ))", s)
  if not f: return s
  for g in f:
    s = s.replace(g[1], "\n" + g[1])
  return s
RELATED_WORDS = {}
with open(relatedwords_explanation_fname, "r") as f:
  reader = csv.reader(f, delimiter=';')
  for row in reader:
    if not re.match("\p{Han}", row[1]): continue
    RELATED_WORDS[row[0]] = format_related_words(row[1])
# print("RELATED_WORDS" + "\n"); somple(RELATED_WORDS)

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
# print("EXAMPLES" + "\n"); somple(EXAMPLES)


INVERTED_EXAMPLES = defaultdict(list)
for ci in TARGET_CI:
  for cj, example_tups in EXAMPLES.items():
    for example_emoji, zhex, enex in example_tups:
      if cj == ci: continue
      if ci in zhex:
        # INVERTED_EXAMPLES[ci].append(("⏿" + example_emoji, zhex, enex))
        INVERTED_EXAMPLES[ci].append(("♻" + example_emoji, zhex, enex))
# print("EXAMPLES" + "\n"); somple(EXAMPLES)

for ci, example_tups in INVERTED_EXAMPLES.items():
  EXAMPLES[ci] += example_tups

def pinyin(s):
  p =  pinyin_jyutping_sentence.pinyin(s)
  p = p.replace(" huán ", " hái ")
  p = p.replace(" dū ", " dōu ")
  p = p.replace(" ，", ",")
  p = p.replace(" 。", ".")
  p = p.replace(" ！", "!")
  p = p.replace(" ？", "?")
  return p

def format_cls(s):
  # if "CL:" not in s: return s
  s = re.sub("\p{Han}\|(\p{Han})\[", "\\1[", s)
  # pinyins = re.findall("[\p{Han}]\[([a-z1-5]{2,7})\].?", s)
  pinyins = re.findall("[^a-z]([a-z]{1,7}[1-5])[^a-z0-9]", s)
  for p in pinyins:
    p_better = pinyin_jyutping_sentence.romanization_conversion.decode_pinyin(p, False, False) 
    s = s.replace(p, p_better)
  return s

  

def conditional_append(ci, resource, out_line, field_name=None):
  if ci in resource:
    if field_name: out_line[0].append(field_name)
    out_line[0].append(resource[ci])
    return True
  else:
    if field_name is not None:
      return True
    return False

MISSING_OTHER_CI_PINYIN = []
MISSING_OTHER_CI_MEANING = []
def get_other_ci_list(zi_j, level):
  other_ci_list = []
  other_ci_superset = ZI_TO_LEVELED_CI[zi_j][level]
  # other_ci_superset = USE_SAME_ZI[zi_j].split(";") if zi_j in USE_SAME_ZI else []
  for ci_k in other_ci_superset:
    ci_k = ci_k.strip()
    if ci_k == ci_j: continue
    if len(ci_k) > 4: continue
    addenda = []

    if ci_k in PINYIN:
      addenda.append(PINYIN[ci_k])
    else:
      MISSING_OTHER_CI_PINYIN.append(ci_k)
    if ci_k in ZI_DEFS:
      addenda.append(ZI_DEFS[ci_k])
    else:
      MISSING_OTHER_CI_MEANING.append(ci_k)
    if addenda:
      ci_k = f"{ci_k} ({'; '.join(addenda)})"
    other_ci_list.append(ci_k)
  return other_ci_list




out_lines = []
for ci_j in TARGET_CI:
  out_line = [[ci_j + OBFUSTICATOR]]
  if not conditional_append(ci_j, PINYIN, out_line): continue
  if ci_j in DEFINITIONS:
    out_line[0].append(format_cls(DEFINITIONS[ci_j]))

  if not conditional_append(ci_j, RELATED_WORDS, out_line, "related words"): pass

  for zi_j in ci_j:
    other_ci_list = get_other_ci_list(zi_j, args.level)
    zi_j_decorated = f"{zi_j} ({ZI_DEFS[zi_j]})" if zi_j in ZI_DEFS else zi_j
    content = "There are no other HSK words in this level (or before) using this character."
    if other_ci_list:
      content = "Other words using this character: " + "; ".join(other_ci_list)
    out_line[0].append(zi_j_decorated)
    out_line[0].append(content)


  if ci_j in EXAMPLES:
    seen_examples = set()
    for ex_emoji, ex_zh, ex_en in EXAMPLES[ci_j][0:MAX_EXAMPLES]:
      if ex_zh in seen_examples: continue
      seen_examples.add(ex_zh)
      ex_en = f"{format_pinyin(ex_zh)}{NEWLINE}{ex_en}"
      ex_zh = f"{ex_emoji} {ex_zh}"
      out_line[0].append(ex_zh)
      out_line[0].append(ex_en)
  out_lines.append(out_line[0])

# print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
# for xx in out_lines:
#     print(xx)
  
out_lines = [
        [field.replace("\n", NEWLINE) for field in out_line]
        for out_line in out_lines
        ]

if BREAK_INTO_N_CHUNKS == 1:
  fname_out = f"flashcards/{args.mode}/{args.level}.flashcards.{args.mode}.csv"
  with open(fname_out, 'w') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter =';', quoting=csv.QUOTE_ALL)
    csvwriter.writerows(out_lines)
  print(f"Wrote {fname_out}")
else:
  chunk_size = int(len(out_lines)/float(BREAK_INTO_N_CHUNKS)) + 1
  for part_i in range(BREAK_INTO_N_CHUNKS):
    out_lines_i = out_lines[part_i*chunk_size:(part_i+1)*chunk_size]
    fname_out = f"flashcards/{args.mode}/{args.level}.flashcards.{args.mode}.{part_i + 1}-of-{BREAK_INTO_N_CHUNKS}.csv"
    with open(fname_out, 'w') as csvfile:
      csvwriter = csv.writer(csvfile, delimiter =';', quoting=csv.QUOTE_ALL)
      csvwriter.writerows(out_lines_i)
    print(f"Wrote {fname_out}")



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


print(f"missing from MISSING_OTHER_CI_MEANING: {'; '.join(MISSING_OTHER_CI_MEANING)}\n")
print(f"missing from MISSING_OTHER_CI_PINYIN: {'; '.join(MISSING_OTHER_CI_PINYIN)}\n")

print(f"Wrote {fname_out}")
