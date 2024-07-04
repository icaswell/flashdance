import regex as re
import time
import random
from collections import defaultdict, Counter
import argparse
import csv
from typing import List, Dict

import jieba
import pinyin_jyutping_sentence

# This is a module in this package
from pinyin import get_pinyin

def get_pinyin_wrapper(s):
  x = get_pinyin(s).split("||")
  return "|".join([xi for i, xi in enumerate(x) if xi not in x[0:i]])




LEVELS = ["hsk1", "hsk2", "hsk3", "hsk4", "hsk5", "hsk6", "stront1", "stront2", "weeb1"]

LEVELED_CI = defaultdict(list)

for level in LEVELS:
  with open(f"resources/vocab_separate/{level}.tsv", "r") as f:
    for i, line in enumerate(f):
      parts = line.split("\t")
      if len(parts) != 3:
        raise ValueError(f"Line {i} should have three tab-separated values but doesn't: {line}")
      ci, _, _ = parts
      LEVELED_CI[level].append(ci)

# zi: {level_name: [ci_0, ci_1, ...]}
ZI_TO_LEVELS = defaultdict(list)
for level in LEVELS:
  for zi in LEVELED_CI[level]:
    if level not in ZI_TO_LEVELS[zi]:
      ZI_TO_LEVELS[zi].append(level) 


def get_ci_set(s):
  ci_in_s = set(jieba.cut(s, cut_all=False))
  ci_in_s |= set(jieba.cut(s, cut_all=True))
  return ci_in_s
def tokenize_zh(s):
  return list(jieba.cut(s))

# # debug
# def get_ci_set(s):
#   return set(s)
# def tokenize_zh(s):
#   return [c for c in s]

class Example():
  def __init__(self, zh, en):
    self.zh = zh
    self.en = en
    self.ci = get_ci_set(zh)
    self.toks = tokenize_zh(zh)


parser = argparse.ArgumentParser(description='Process input file and save the result to an output file.')
parser.add_argument('--level', type=str)
parser.add_argument('--mode', default="iphone", type=str)
args = parser.parse_args()

# These are the full definitions
definitions_fname = "resources/vocab_combined/all_ci_and_zi_defs.tsv"

# These are the one-word definitions. used in 
zi_definitions_fname = "resources/definitions_and_pinyin/zi_singleword_defs.tsv"
multizi_definitions_fname = "resources/definitions_and_pinyin/multizi_singleword_defs.tsv"

examples_fnames = [
        "resources/example_sentences/general2.tsv",
        "resources/example_sentences/multicoverage_4o.tsv",
        "resources/example_sentences/cql.tsv",
        "resources/example_sentences/raccoon.tsv",
]


if args.mode == "android":
  pass  # break into chunks and stuff could be added here

if args.mode == "iphone":
   NEWLINE = "\r"
elif args.mode == "android":
   NEWLINE = "<br></br>"

COLOR_PARITY = 0
def colorred(s: str) -> str:
  """Color the given string."""
  global COLOR_PARITY
  COLOR_PARITY  = (COLOR_PARITY + 1) %2
  color_i = 31 if COLOR_PARITY else 33
  # return f"<{s}>"
  return f"\033[{color_i}m{s}\033[0m"




TARGET_CI = set()
with open(f"resources/vocab_separate/{args.level}.tsv", "r") as f:
  for line in f:
    ci = line.strip().split("\t")[0]
    # since we can't programmatically determine whether something is being used as an adverb vs verb (e.g.),
    # we ignore the parentheticals.
    # Alas.
    ci = re.sub("(（| \().*", "", ci)
    # another sad approximation: structures with ellipses
    # e.g. 不但……而且……
    ci = re.sub(".*……(.*)……",   "\1", ci)
    TARGET_CI.add(ci.strip())


# We only want to consider shorter examples, so discard
# examples longer than this
ALL_EXAMPLES = []
MAX_CHARS_IN_EXAMPLE = 15
ALL_CI_WITH_EXAMPLES = set()
# CI_TO_EXAMPLES = defaultdict(list)
for examples_fname in examples_fnames:
  with open(examples_fname, "r") as f:
    for line in f:
      if "\t" not in line:
        continue
      unused_ci, content = line.strip().split("\t", maxsplit=1)
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
      for zhex, enex in paired_examples:
        # if it is longer than ~4 is is probably grammar and we don't need exact match
        if len(zhex) > MAX_CHARS_IN_EXAMPLE: continue
        ex = Example(zhex, enex)
        # if not ex.ci & TARGET_CI: continue
        ALL_EXAMPLES.append(ex)
        ALL_CI_WITH_EXAMPLES |= ex.ci
        # for ci in ci_in_zhex:
        #   CI_TO_EXAMPLES[ci].append((zhex, enex, ci_in_zhex))

# ALL_EXAMPLES = [ex for exes in CI_TO_EXAMPLES.values() for ex in exes]
print(f'{len(ALL_EXAMPLES)} example sentences loaded')
# handle each level separately

print(f"No example sentences for: |" + "|".join(TARGET_CI - ALL_CI_WITH_EXAMPLES) + "|")
TARGET_CI &= ALL_CI_WITH_EXAMPLES
del ALL_CI_WITH_EXAMPLES

#  # let's see what our coverage is!
#  # this will just report to the caller so they know whether their example sentences
#  # cover the desired characters
#  how_many_examples = defaultdict(list)
#  max_report = 5
#  for ci in TARGET_CI:
#    examples = CI_TO_EXAMPLES.get(ci, [])
#    n = min(len(examples), max_report)
#    how_many_examples[n].append(ci)
#  
#  for k in sorted(how_many_examples.keys(), reverse=True):
#    ex = how_many_examples[k]
#    print(f"{k}:  [{len(ex)}]", '|'.join(ex))


#=====================================================================
# Time for a terrifying, O(n**2) algorithm to approximate the NP-Hard
# knapsack problem.

# the examples that we will make our flashcards out of
SELECTED_EXAMPLES = set()

# this is updated whenever we add a new sentence and tracks how many times we have seen our target chars
CI_TO_N_EXAMPLES = {ci:0 for ci in TARGET_CI}
def get_pct_covered():
  return len([1 for k, v in CI_TO_N_EXAMPLES.items() if v])/len(CI_TO_N_EXAMPLES)

# penalty for adding extra characters that are not in the set we are looking at
DEAD_WEIGHT_PENALTY = - 0.2

# setting this equal to 2 basically means we try to find at least two examples per ci (asterisk, asterisk)
MAX_CT_WE_CARE_ABT = 0
LENGTH_PENALTY = 0

def points_given_current_ci_count(ct):
  # if you have thus far seen 0 of this ci, you get one point
  # if you have seen it once, you get 0.5 points, etc.
  # gains saturate at ct == 3
  if ct  >= 3: return 0
  return 1.0 / (1 + ct)

def get_score(ex):
  score, covered, deadweight = 0, 0, 0
  for ci in ex.ci:
    if ci not in TARGET_CI:
      deadweight += len(ci)
      score += len(ci) *  DEAD_WEIGHT_PENALTY 
    else:
      ct = CI_TO_N_EXAMPLES[ci]
      if ct <= MAX_CT_WE_CARE_ABT:
        covered += 1
      score += points_given_current_ci_count(ct)
  # length penalty
  score -= LENGTH_PENALTY*len(ex.toks)
  return score, covered, deadweight

def get_best_ex():
  best_ex = None
  best_score = -10000000
  no_new_coverage = set()
  for ex in ALL_EXAMPLES:
    score, n_covered, n_deadweight  = get_score(ex)
    if not n_covered:
      no_new_coverage.add(ex)
      continue
    if score > best_score:
      best_score = score
      best_ex = ex
  return best_ex, no_new_coverage

def update_variables(ex, no_new_coverage, iter_i):
  # one redundant call ain't gon hurt no one
  score, n_covered, n_deadweight  = get_score(ex)
  zhex_colored = "".join([(colorred(ci) if ci in TARGET_CI else ci) for ci in tokenize_zh(ex.zh)])
  print(f"score={score:.1f}\tcovered={n_covered}\tdeadweight={n_deadweight}\t#{iter_i}\t{get_pct_covered():.2%}\t{zhex_colored}")
  for ci in ex.ci:
    if ci not in TARGET_CI: continue
    CI_TO_N_EXAMPLES[ci] += 1

  global SELECTED_EXAMPLES
  global ALL_EXAMPLES
  SELECTED_EXAMPLES.add(ex)
  ALL_EXAMPLES = [ex for ex in ALL_EXAMPLES if ex not in no_new_coverage]


st = time.time()
i = 0
while True:
  i += 1
  best_ex, no_new_coverage = get_best_ex()
  if best_ex is None: break
  update_variables(best_ex, no_new_coverage | {best_ex}, i)
print(f"covered {len(TARGET_CI)} ci with {len(SELECTED_EXAMPLES)} examples")

blah = 0
for ex in SELECTED_EXAMPLES:
  blah += len(ex.ci & TARGET_CI)
print(f"Each ci is covered by an average of {blah/len(TARGET_CI):.1f} distinct example sentences.")


def format_cedict_cls(s):
  """Format the counter words in CEDICT so they use normal pinyin and don't include Traditional
  """
  s = re.sub("\p{Han}\|(\p{Han})\[", "\\1[", s)
  for _ in range(2):
    pinyins = re.findall("[^a-z]([a-z]{1,7}[1-5])[^a-z0-9]", s)
    for p in pinyins:
      p_better = pinyin_jyutping_sentence.romanization_conversion.decode_pinyin(p, False, False) 
      s = s.replace(p, p_better)
  return s
  
def fix_cedict_deff(deff):
  deff = format_cedict_cls(deff) 
  parts = deff.split("; ")
  cls = [p for p in parts if p.startswith("CL")]
  prs = [p for p in parts if " pr. " in p]
  proper_nouns = [p for p in parts if p[0].isupper() and p not in cls and p not in prs]
  surnames = [p for p in parts if p.startswith("surname ")]
  other = [p for p in parts if p not in cls + proper_nouns + surnames + prs]
  out_parts = other + surnames + proper_nouns + cls
  return "; ".join(out_parts)

DEFINITIONS = {}
with open(definitions_fname, "r") as f:
  for line in f:
    parts = line.strip().split("\t")
    if len(parts) >=3:
      deff = parts[2]
      if deff.startswith("/"):
        deff = deff[1:-1].replace("/", "; ")
      deff = fix_cedict_deff(deff)
      DEFINITIONS[parts[0]] = deff


ZI_DEFS = {}
with open(zi_definitions_fname, "r") as f:
  for line in f:
    parts = line.strip().split("\t")
    ZI_DEFS[parts[0]] = parts[1]

with open(multizi_definitions_fname, "r") as f:
  for line in f:
    parts = line.strip().split("\t")
    ZI_DEFS[parts[0]] = parts[1]



#===================================================================
# Now that we have prepared all the resources, we actually make the floshcards!
out_lines = []
print(len(SELECTED_EXAMPLES))
for ex_j in SELECTED_EXAMPLES:
  out_line = [ex_j.zh,
              get_pinyin_wrapper(ex_j.zh),
              ex_j.en]

  for ci_j in ex_j.toks:
    if not re.search("\p{Han}", ci_j):
      continue
    levels = "|".join(ZI_TO_LEVELS.get(ci_j, ["non-hsk"]))
    addenda = []
    if ci_j in ZI_DEFS:
      addenda.append(ZI_DEFS[ci_j])
    addenda.append(get_pinyin(ci_j))
    addenda.append(levels)
    addenda = [a for a in addenda if a]
    addendum = f"({'; '.join(addenda)})" if addenda else ""
    out_line += [
        f"{ci_j} {addendum}",
        DEFINITIONS.get(ci_j, "No definition found")
        ]
  out_lines.append(out_line)


out_lines = [
        [field.replace("\n", NEWLINE) for field in out_line]
        for out_line in out_lines
        ]

fname_out = f"flashcards/{args.mode}/{args.level}.inverted_flashcards.{args.mode}.csv"
with open(fname_out, 'w') as csvfile:
  csvwriter = csv.writer(csvfile, delimiter =';', quoting=csv.QUOTE_ALL)
  csvwriter.writerows(out_lines)
print(f"Wrote {fname_out}")

