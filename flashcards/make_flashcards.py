import csv
import regex as re
import pinyin_jyutping_sentence
import random
from collections import defaultdict
import argparse
from typing import List, Dict
import time

# This is a module in this package
from pinyin import get_pinyin

parser = argparse.ArgumentParser(description='Process input file and save the result to an output file.')
parser.add_argument('--verbose', type=bool, default=False)
parser.add_argument('--level', type=str)
parser.add_argument('--exclude_levels', type=str, default="", help="whether to ignore ci in --level that occur in one of these levels (comma-separated)")
parser.add_argument('--mode', default='iphone', type=str)
parser.add_argument('--existing_defs', type=str, default="concat", help="what to do with the pinyin and definitions in the input TSV")
args = parser.parse_args()

VTIME = time.time()
def vprint(s):
  if not args.verbose:
    return
  global VTIME
  t = time.time()
  print(f"\033[92m...[{t - VTIME:.2f}s]\n{s}...\033[0m")
  VTIME = t

# These are the full definitions
definitions_fname = "resources/vocab_combined/all_ci_and_zi_defs.tsv"

# These are the POS annotations
pos_fname = "resources/pos/pos.tsv"

# These are the one-word definitions. used in 
zi_definitions_fname = "resources/definitions_and_pinyin/zi_singleword_defs.tsv"
multizi_definitions_fname = "resources/definitions_and_pinyin/multizi_singleword_defs.tsv"

# relatedwords_fname = "resources/related_words/hsk1to6.tsv"
# relatedwords_explanation_fname = "resources/hsk1to6.tsv__gpt-3.5-turbo-1106_t0.0__related_words_prompt.csv"
usage_notes_fname = "resources/usage_notes/usage_notes.tsv"

# https://en.wikipedia.org/wiki/List_of_Unicode_characters#Miscellaneous_Symbols
examples_fnames = [
        ["❈", 3, "resources/example_sentences/general.tsv"],  # ❈ is "heavy sparkle"
        ["🐇", 2, "resources/example_sentences/cql.tsv"],
        ["🦝", 2, "resources/example_sentences/raccoon.tsv"],
        # ☯️ ☯ ☾𖤓࿊
        #   𓆝 𓆟 𓆞 𓆝 𓆟
]
OBFUSTICATOR = "⠀" # invisible character to prevent deduping
MAX_EXAMPLES = 12
MAX_SAME_ZI_EXAMPLES = 10

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
   format_pinyin = lambda x: f"【{get_pinyin(x)}】"
elif args.mode == "android":
   NEWLINE = "<br></br>"
   format_pinyin = lambda x: f"<i>{get_pinyin(x)}</i>"
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
    "stront2": 6,
    "stront3": 6,
    "weeb1": 6,
}
if args.level not in LEVELS:
  LEVELS[args.level] = max(LEVELS.values())


vprint("getting all zi in all levels....")
LEVELED_CI = defaultdict(list)
ORIGIN_NOTE_PERCI = defaultdict(set)
ALL_ZI_IN_LEVELS = set()
for level in LEVELS:
  with open(f"resources/vocab_separate/{level}.tsv", "r") as f:
    for i, line in enumerate(f):
      parts = line.split("\t")
      if len(parts) not in {3, 4}:
        raise ValueError(f"Line {i} should have 3-4 tab-separated values but doesn't: {line}")

      ci = parts[0]
      # if there is no explicit origin note, fall back to the level
      origin_note = parts[3].strip() if len(parts) == 4 else level
      ORIGIN_NOTE_PERCI[ci].add(origin_note)
      LEVELED_CI[level].append(ci)
      ALL_ZI_IN_LEVELS |= {zi for zi in ci}

def get_ci_with_this_zi_conditioned_on_level(zi, level_name):
  # applicable_levels: levels that are at this level or below
  applicable_levels = [lev for lev in LEVELS if LEVELS[lev] <= LEVELS[level_name]]
  output_ci = []
  output_ci_set = set()
  for lev in applicable_levels:
    for ci in LEVELED_CI[lev]:
      if ci in output_ci_set: continue # using a set 2xed the speed
      if zi in ci:
        output_ci.append(ci)
        output_ci_set.add(ci)
  return output_ci

vprint("getting all leveled zi....")
# zi: {level_name: [ci_0, ci_1, ...]}
ZI_TO_LEVELED_CI = defaultdict(lambda: defaultdict(list))
for zi in ALL_ZI_IN_LEVELS:
  for level_name in LEVELS:
    ZI_TO_LEVELED_CI[zi][level_name] = get_ci_with_this_zi_conditioned_on_level(zi, level_name)

# Read in the ci that you are making flashcards for. Ignore definitions and pinyin for now.
# existing definitions will be added in if --args.existing_defs has the right value.
vprint("getting target ci....")
TARGET_CI = []
with open(f"resources/vocab_separate/{args.level}.tsv", "r") as f:
  seen = set()  # 🎵 did it all for the O(1) 
  for line in f:
    ci = line.strip().split("\t")[0].strip()
    if ci in seen:
      continue
    seen.add(ci)
    TARGET_CI.append(ci)

for anti_level in args.exclude_levels.split(','):
  if not anti_level: continue
  if anti_level not in LEVELED_CI:
    raise ValueError(f"level {anti_level} not in LEVELED_CI")
  to_exclude = set(LEVELED_CI[anti_level])
  TARGET_CI = [ci for ci in TARGET_CI if ci not in to_exclude]


vprint("getting pos....")
POS_ANNOTATIONS = {}
with open(pos_fname, "r") as f:
  for line in f:
    ci, pos = line.strip().split("\t")
    POS_ANNOTATIONS[ci] = pos


vprint("getting official definitions.")
# get the "official" ccdict definitions
def format_cedict_cls(s):
  """Format the counter words in CEDICT so they use normal pinyin and don't include Traditional
  """
  s = re.sub("\p{Han}\|(\p{Han})\[", "\\1[", s)
  for _ in range(2):
    pinyins = re.findall("[^a-z]([a-zA-Z]{1,7}[1-5])[^a-z0-9]", s)
    for p in pinyins:
      p_better = pinyin_jyutping_sentence.romanization_conversion.decode_pinyin(p, False, False) 
      s = s.replace(p, p_better)
  return s
  
def fix_cedict_deff(deff):
  deff = format_cedict_cls(deff) 
  parts = deff.split("; ")
  parts = [p for p in parts if p]
  cls = [p for p in parts if p.startswith("CL")]
  prs = [p for p in parts if " pr. " in p]
  proper_nouns = [p for p in parts if p[0].isupper() and p not in cls and p not in prs]
  surnames = [p for p in parts if p.startswith("surname ")]
  other = [p for p in parts if p not in cls + proper_nouns + surnames + prs]
  out_parts = other + surnames + proper_nouns + cls
  return DEF_DELIM.join(out_parts)

def get_pinyin_for_definition(ci):
  """Wrapper that gives multipinyin specifically for the main pinyin field in the flashcards.

  e.g. 'shù||shǔ'
  """
  if ci in CI_TO_MULTI_PINYIN:
    return CI_TO_MULTI_PINYIN[ci]
  return get_pinyin(ci)

def decode_multipinyin(pinyins):
  """decode_multipinyin('shu4||shu3') == 'shù||shǔ'
  """
  out = [pinyin_jyutping_sentence.romanization_conversion.decode_pinyin(p, False, False) for p in pinyins.split("||") ]
  return "||".join(out)

DEFINITIONS = {}
DEF_DELIM = "; "  # the delimtor to separate definitions in the flashcard with
CI_TO_MULTI_PINYIN = {}  #  special cases where there are multiple pinyins
#                           that have to be kept in sync with the definitions
with open(definitions_fname, "r") as f:
  for line in f:
    parts = line.strip().split("\t")
    if len(parts) >=3:
      ci, pinyins, deff = parts[0:3]
      # I think this is no longer relevant, but doesn't hurt
      if deff.startswith("/") and deff.endswith("/"):
        deff = deff[1:-1].replace("/", "; ")
      if re.findall("[a-z]/[a-z]", deff):
        deff = deff.replace("/", DEF_DELIM)
      deff = fix_cedict_deff(deff)
      if "||" in pinyins:
        CI_TO_MULTI_PINYIN[ci] = decode_multipinyin(pinyins)
      DEFINITIONS[ci] = deff.strip(";")

vprint("adding preexisting defs....")
# add in the existing definitions
with open( f"resources/vocab_separate/{args.level}.tsv", "r") as f:
  for line in f:
    parts = line.strip().split("\t")
    if len(parts) >=3:
      ci, unused_pinyin, deff = parts[0:3]
      existing_defs_lower = DEFINITIONS.get(ci, '').lower().split(DEF_DELIM)
      if deff.lower() in existing_defs_lower: continue

      existing_defs = DEFINITIONS.get(ci, '').split(DEF_DELIM)
      DEFINITIONS[ci] = DEF_DELIM.join([deff] + existing_defs)

vprint("getting single zi and multizi defs....")
ZI_DEFS = {}
with open(zi_definitions_fname, "r") as f:
  for line in f:
    parts = line.strip().split("\t")
    ZI_DEFS[parts[0]] = parts[1]

with open(multizi_definitions_fname, "r") as f:
  for line in f:
    parts = line.strip().split("\t")
    if len(parts) == 2:
      ZI_DEFS[parts[0]] = parts[1]


# Deprecating this until we have a better source
RELATED_WORDS = {}
# def format_related_words(s):
#   f = re.findall("([^\)])\n([A-Za-z, ]{0,20}(oth |summary|example|hese words|hese two words|hese three words|hese four words|The words|While|So, ))", s)
#   if not f: return s
#   for g in f:
#     s = s.replace(g[1], "\n" + g[1])
#   return s
# with open(relatedwords_explanation_fname, "r") as f:
#   reader = csv.reader(f, delimiter=';')
#   for row in reader:
#     if not re.match("\p{Han}", row[1]): continue
#     RELATED_WORDS[row[0]] = format_related_words(row[1])

vprint("getting usage notes....")
USAGE_NOTES = {}
with open(usage_notes_fname, "r") as f:
  for line in f:
    ci, note = line.strip().split("\t")
    note = note.replace("<NEWLINE>", NEWLINE)
    USAGE_NOTES[ci] = note

def ignore_usage_note(note):
  # One might want to include these, e.g.:
  # There is no difference between the use of 玩儿 (wánr) in Chinese and "to play" or "to have fun" in English.
  # howeve,r in practice this probably mainly adds to the noise.
  # punts = ["There is no difference", "No special notes.", "No additional notes.", "Nothing special to note.",  "There's nothing special about this word."]
  punts = ["There is no difference", "No special notes.", "No additional notes.", "othing special"]
  for punt in punts:
    if punt in note: return True
  return False

vprint("getting all examples....")
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
        # if it is longer than ~4 is is probably grammar and we don't need exact match
        if len(ci) <= 4 and ci not in zhex: continue
        EXAMPLES[ci].append((example_emoji, zhex, enex))


vprint("getting inverted examples...")
INVERTED_EXAMPLES = defaultdict(list)
for ci in TARGET_CI:
  for cj, example_tups in EXAMPLES.items():
    if cj == ci: continue
    n_existing = len(EXAMPLES[ci]) if ci in EXAMPLES else 0
    for example_emoji, zhex, enex in example_tups:
      if len(INVERTED_EXAMPLES[ci]) + n_existing > MAX_EXAMPLES : continue
      if ci in zhex:
        recycle_emoji = "♸"
        INVERTED_EXAMPLES[ci].append((recycle_emoji + example_emoji, zhex, enex))

for ci, example_tups in INVERTED_EXAMPLES.items():
  EXAMPLES[ci] += example_tups

  

MISSING_CI_WITH_SAME_ZI_MEANING = set()
def get_other_ci_list(zi_j, level) -> List[str]:
  """Get other words that use the Hanzi zi_j and are at the same or lower level.
  
  The list will have the short (one-word) definitions in parentheses.

  EXAMPLE:

  zi_j = 合
  return = ["合适 (suitable)", "适合 (to adapt)", ...]
  """
  other_ci_list = []
  other_ci_superset = ZI_TO_LEVELED_CI[zi_j][level]
  for ci_k in other_ci_superset:
    ci_k = ci_k.strip()
    if ci_k == ci_j: continue
    if len(ci_k) > 4: continue
    addenda = []

    if ci_k in ZI_DEFS:
      addenda.append(ZI_DEFS[ci_k])
    elif re.sub(chinese_pos_regex, "", ci_k) in ZI_DEFS:  
      addenda.append(ZI_DEFS[re.sub(chinese_pos_regex, "", ci_k)])
    else:
      MISSING_CI_WITH_SAME_ZI_MEANING.add(ci_k)
    addenda.append(get_pinyin(ci_k))
    if addenda:
      ci_k = f"{ci_k} ({'; '.join(addenda)})"
    other_ci_list.append(ci_k)
  return other_ci_list[0:MAX_SAME_ZI_EXAMPLES]

chinese_pos_regex = "（[" +  "".join({
    "动",  # verb
    "代",  # pronoun
    "名",  # noun
    "量",  # measure
    "叹",  # exclamation
    "连",  # conjunction
    "数",  # number
    "副",  # adverb
    "助",  # auxiliary
    "介",  # medial
    "形",  # adjective
}) + "]）"


RADICAL_ANNOTATIONS = {}  # TODO :(

MISSING_POS = set()
MISSING_USAGE_NOTES = set()
MISSING_RADICALS = set()

vprint("making flashcards...")
#===================================================================
# Now that we have prepared all the resources, we actually make the floshcards!
out_lines = []
for ci_j in TARGET_CI:
  out_line = [ci_j + OBFUSTICATOR]

  out_line.append(get_pinyin_for_definition(ci_j))

  if ci_j in DEFINITIONS:
    out_line.append(DEFINITIONS[ci_j])


  # Break down meaning of each constituent zi
  for zi_j in ci_j:
    if not re.match("\p{Han}", zi_j): continue
    other_ci_list = get_other_ci_list(zi_j, args.level)  # other ci using this zi
    zi_j_decorated = f"{zi_j} ({ZI_DEFS[zi_j]})" if zi_j in ZI_DEFS else zi_j
    content = "There are no other HSK words in this level (or before) using this character."
    if other_ci_list:
      content = "Other words using this character: " + "; ".join(other_ci_list)
    out_line.append(zi_j_decorated)
    out_line.append(content)


  if ci_j in USAGE_NOTES:
    if ignore_usage_note(USAGE_NOTES[ci_j]):
      # note: we don't add it to MISSING_USAGE_NOTES since this was probably a punt
      continue
    out_line.append("usage notes")
    out_line.append(USAGE_NOTES[ci_j])
  else:
    MISSING_USAGE_NOTES.add(ci_j)

  if ci_j in POS_ANNOTATIONS:
    # prepend to English definition
    # out_line[2] = f"{[POS_ANNOTATIONS[ci_j]]} {out_line[2]}"
    out_line += ["parts of speech", POS_ANNOTATIONS[ci_j]]
  else:
    MISSING_POS.add(ci_j)

  if ci_j in RADICAL_ANNOTATIONS:
    out_line += ["radicals", RADICAL_ANNOTATIONS[ci_j]]
  else:
    MISSING_RADICALS.add(ci_j)

  # below clause triggers largely for NHSK vocabs that have the POS
  # in parens afterwards, but the example sentence ignored it
  if ci_j not in EXAMPLES:
    stripped = re.sub(chinese_pos_regex, "", ci_j)
    if stripped in EXAMPLES:
      EXAMPLES[ci_j] = EXAMPLES[stripped]

  if ci_j in EXAMPLES:
    seen_examples = set()
    to_add = EXAMPLES[ci_j][0:MAX_EXAMPLES]

    for ex_emoji, ex_zh, ex_en in EXAMPLES[ci_j][0:MAX_EXAMPLES]:
      if ex_zh in seen_examples: continue
      seen_examples.add(ex_zh)
      ex_en = f"{format_pinyin(ex_zh)}{NEWLINE}{ex_en}"
      ex_zh = f"{ex_emoji} {ex_zh}"
      out_line.append(ex_zh)
      out_line.append(ex_en)
  out_lines.append(out_line)


  if ci_j in ORIGIN_NOTE_PERCI:
    out_line += ["origin", '/'.join(sorted(list(ORIGIN_NOTE_PERCI[ci_j])))]
  
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



def write_missing(missing, name, max_chars=None):
  if not missing:
    print(f"Nothing missing from {name}!")
    return
  missing = {m for m in missing if max_chars is None or len(m) <= max_chars}
  print(f"missing from {name}: {'; '.join(missing)}")
  fname = f"missing/{name}.tsv"
  with open(fname, "w") as f:
    for ci in missing:
      f.write(f"{ci}\t{DEFINITIONS.get(ci, 'no definition')}\n")
      # f.write(f"{cij}\t{get_pinyin(cij)}\t{DEFINITIONS.get(cij, 'no definition')}\n")
  print(f"wrote to {fname}\n")

TARGET_CI = set(TARGET_CI)
# TARGET_ZI = {zi for ci in TARGET_CI for zi in ci if not re.match("[a-zA-Z\p{punctuation}]", zi)}
TARGET_ZI = {zi for ci in TARGET_CI for zi in ci if re.match("\p{Han}", zi)}


write_missing(MISSING_USAGE_NOTES, "usage_notes", max_chars=3) # no exmple sentences for things > 4 Hanzi long

missing = TARGET_CI - DEFINITIONS.keys() 
write_missing(missing, "definitions")

missing = TARGET_CI - EXAMPLES.keys() 
write_missing(missing, "examples", max_chars=4) # no exmple sentences for things > 4 Hanzi long

missing = TARGET_ZI - ZI_DEFS.keys()
write_missing(missing, "zi_defs")

write_missing(MISSING_CI_WITH_SAME_ZI_MEANING, "single_defs_for_shared_zi_multici")

write_missing(MISSING_POS, "pos", max_chars=3)


#    ("examples.tsv", "cql_example_prompt3_3examples.txt"),
api_cmd_fname = "missing/api_commands.sh"
with open(api_cmd_fname, "w") as f:
  f.write("python3 api_main_gembini.py --chunk_size=40 --input=missing/usage_notes.tsv --system_prompt=prompts/usage_notes_prompt.txt --model=gemini-1.5-pro\n")
  f.write("python3 api_main_gembini.py --chunk_size=40 --input=missing/examples.tsv --system_prompt=prompts/general_example_prompt_3examples.txt\n")
  f.write("python3 api_main_gembini.py --chunk_size=100 --input=missing/single_defs_for_shared_zi_multici.tsv --system_prompt=prompts/multizi_prompt.txt\n")
  f.write("python3 api_main_gembini.py --chunk_size=100 --input=missing/pos.tsv --system_prompt=prompts/pos_prompt.txt\n")
  f.write("python3 api_main_gembini.py --chunk_size=100 --input=missing/zi_defs.tsv --system_prompt=prompts/singlezi_prompt.txt\n")
  f.write("tail -n 5 output/LOG.tsv | cut -f 1\n")


print(f"Wrote flashcards to {fname_out}")
print(f"Wrote api commands to {api_cmd_fname}")
vprint("done!")
