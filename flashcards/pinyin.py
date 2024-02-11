import csv
import regex as re
import pinyin_jyutping_sentence
import random
from collections import defaultdict


pinyin_fname = "resources/vocab_combined/all_ci_and_zi_pinyin.tsv"

PINYIN = {}
with open(pinyin_fname, "r") as f:
  for i, line in enumerate(f):
    parts = line.strip().split("\t")
    if len(parts) != 2: print(i, line)
    else: PINYIN[parts[0]] = parts[1]

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
