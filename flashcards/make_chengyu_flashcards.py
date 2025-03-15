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
from definitions import DEFINITIONS, add_existing_defs, get_pinyin_for_definition, chinese_pos_regex

parser = argparse.ArgumentParser(description='Process input file and save the result to an output file.')
parser.add_argument('--mode', default='iphone', type=str)
parser.add_argument('--source', default='wukongsch', type=str)
args = parser.parse_args()

MAX_SAME_ZI_EXAMPLES = 10
DELIM = "~==~"


# These are the one-word definitions. used in 
zi_definitions_fname = "resources/definitions_and_pinyin/zi_singleword_defs.tsv"
multizi_definitions_fname = "resources/definitions_and_pinyin/multizi_singleword_defs.tsv"

if args.mode == "iphone":
   NEWLINE = "\r"
   NEWLINE = "                                                                   "
   format_pinyin = lambda x: f"【{get_pinyin(x)}】"
elif args.mode == "android":
   NEWLINE = "<br></br>"
   format_pinyin = lambda x: f"<i>{get_pinyin(x)}</i>"
else:
  raise ValueError("argh")

print("getting single zi and multizi defs....")
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


LEVELS = ["hsk1", "hsk2", "hsk3", "hsk4", "hsk5", "hsk6", "nhsk1", "nhsk2", "nhsk3", "nhsk4", "nhsk5", "nhsk6", "stront1", "stront2", "stront3", "weeb1"]

print("getting all zi in all levels....")
ORIGIN_NOTE_PERCI = defaultdict(set)
ZI_TO_CI = defaultdict(set)
for level in LEVELS:
  with open(f"resources/vocab_separate/{level}.tsv", "r") as f:
    for i, line in enumerate(f):
      parts = line.split("\t")
      if len(parts) not in {3, 4}:
        raise ValueError(f"Line {i} should have 3-4 tab-separated values but doesn't: {line}")
      ci = parts[0]
      if len(ci) == 1:
        continue
      # if there is no explicit origin note, fall back to the level
      origin_note = parts[3].strip() if len(parts) == 4 else level
      ORIGIN_NOTE_PERCI[ci].add(origin_note)
      for zi in ci:
        ZI_TO_CI[zi].add(ci)


MISSING_CI_WITH_SAME_ZI_MEANING = set()
def get_other_ci_list(zi_j) -> List[str]:
  """Get other words that use the Hanzi zi_j
  
  The list will have the short (one-word) definitions in parentheses.

  EXAMPLE:

  zi_j = 合
  return = ["合适 (suitable)", "适合 (to adapt)", ...]
  """
  other_ci_list = []
  other_ci_superset = ZI_TO_CI[zi_j]
  for ci_k in other_ci_superset:
    ci_k = ci_k.strip()
    if len(ci_k) > 8: continue
    addenda = []

    if ci_k in ZI_DEFS:
      addenda.append(ZI_DEFS[ci_k])
    elif re.sub(chinese_pos_regex, "", ci_k) in ZI_DEFS:  
      addenda.append(ZI_DEFS[re.sub(chinese_pos_regex, "", ci_k)])
    addenda.append(get_pinyin(ci_k))
    if addenda:
      ci_k = f"{ci_k} ({'; '.join(addenda)})"
    other_ci_list.append(ci_k)
  return other_ci_list[0:MAX_SAME_ZI_EXAMPLES]

def chunk_to_flashcard(chunk):
  # resources/chengyu/wukongsch.txt
  parts = chunk.strip().split("\n")
  chengyu, pinyin, short_def = parts[0:3]
  story_heading, story = parts[3:5]
  source_heading, source = parts[-2:]

  # Break down meaning of each constituent zi
  zi_breakdown = []
  for zi_j in chengyu:
    if not re.match("\p{Han}", zi_j): continue
    other_ci_list = get_other_ci_list(zi_j)
    zi_j_decorated = f"{zi_j} ({ZI_DEFS[zi_j]})" if zi_j in ZI_DEFS else zi_j
    content = "No other ci using this hanzi have been found"
    if other_ci_list:
      content = "Other words using this character: " + "; ".join(other_ci_list)
    zi_breakdown.append(zi_j_decorated)
    zi_breakdown.append(content)

  examples = parts[5:-2]
  if len(examples)%2 != 0:
   print('-'*80 + f"\nbad n examples: {examples}")
   print(f"parts: {parts}")
  examples_out = []
  for zh, en in list(zip(examples, examples[1:])):
    if not re.search("\\p{Han}", zh):
      print('-'*80 + f"\nexample lacks Han: {zh} {parts}")
    if not re.search("\\p{Latn}",en):
      print('-'*80 + f"\nexample lacks Latn: {zh} {parts}")
    decorated_en = f"{format_pinyin(zh)}{NEWLINE}{en}"
    examples_out.append(zh)
    examples_out.append(decorated_en)
  csv_fields = [
      chengyu,
      pinyin,
      short_def,
      story_heading,
      story,
  ] + zi_breakdown + examples_out + [source_heading, source]
  return csv_fields


print("making flashcards...")
#===================================================================
# Now that we have prepared all the resources, we actually make the floshcards!
out_lines = []
with open(f"resources/chengyu/{args.source}.txt", "r") as f:
  chunks = f.read().split(DELIM)
  for chunk in chunks:
    if not chunk.strip(): continue
    prepped = chunk_to_flashcard(chunk)
    out_lines.append(prepped)

out_lines = [
        [field.replace("\n", NEWLINE) for field in out_line]
        for out_line in out_lines
        ]

fname_out = f"flashcards/{args.mode}/chengyu-{args.source}.flashcards.{args.mode}.csv"
with open(fname_out, 'w') as csvfile:
  csvwriter = csv.writer(csvfile, delimiter =';', quoting=csv.QUOTE_ALL)
  csvwriter.writerows(out_lines)
print(f"Wrote {fname_out}")
