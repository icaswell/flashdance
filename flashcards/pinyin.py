import csv
import regex as re
import pinyin_jyutping_sentence
import random
from collections import defaultdict


# pinyin_fname = "resources/vocab_combined/all_ci_and_zi_pinyin.tsv"
pinyin_fname = "resources/vocab_combined/all_ci_and_zi_defs.tsv"

def format_variant_pr(pr):
  parts = pr.split()
  out = []
  for p in parts:
    if 1 < len(p)  and any(i in p for i in '12345'):
      # print(p, end="")
      out.append(pinyin_jyutping_sentence.romanization_conversion.decode_pinyin(p, False, False))
      # print(">>")
    else:
      out.append(p)
  pr_i = out.index('pr.')
  out = out[pr_i - 1:]
  out = " ".join(out)
  out = re.sub("[\(\)]", "", out)
  return out


PINYIN = {}
with open(pinyin_fname, "r") as f:
  for i, line in enumerate(f):
    parts = line.strip().split("\t")
    if len(parts) < 3: print(i, line); continue

    # ai1 --> āi
    p_better = []
    for p_i in parts[1].split("||"):
      if any(i in p_i for i in '12345'):
        p_better.append(pinyin_jyutping_sentence.romanization_conversion.decode_pinyin(p_i, False, False))
      else:
        p_better.append(p_i)
    PINYIN[parts[0]] = "||".join(p_better)

    # look for variant prs
    prs = [pr for pr in re.split("/|; |\|\|", parts[2]) if " pr. " in pr]
    all_prs = [PINYIN[parts[0]]] + [format_variant_pr(pr) for pr in prs]
    PINYIN[parts[0]] = "; ".join(all_prs)


def get_pinyin(s):
  if s in PINYIN:
    p = PINYIN[s]
  else:
    p = pinyin_jyutping_sentence.pinyin(s)
  p = p.replace(" huán ", " hái ")
  p = p.replace(" dū ", " dōu ")
  p = p.replace(" ，", ",")
  p = p.replace(" 。", ".")
  p = p.replace(" ！", "!")
  p = p.replace(" ？", "?")
  return p

# print(get_pinyin("唉"))
# print(get_pinyin("这"))
# print(get_pinyin("绿光"))

