import regex as re
import pinyin_jyutping_sentence
from collections import defaultdict
from typing import List, Dict

# This is a module in this package
from pinyin import get_pinyin

# These are the full definitions
definitions_fname = "resources/vocab_combined/all_ci_and_zi_defs.tsv"

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
def canonicalize_def_list(deffs:str):
  deffs = deffs.replace("‘", "'")
  deffs = deffs.replace("/", DEF_DELIM)
  # remove traditional script from CEDict defininitions
  deffs = re.sub("\p{Han}+\|(\p{Han}+)", "\\1", deffs) 
  deffs = deffs.split(DEF_DELIM)
  for i, deff in enumerate(deffs):
    if deff in deffs[0:i]:
      deffs[i] = None  # remove if this has already occurred
      continue
    decorated = "to " + deff
    if decorated in deffs[i+1:]:
      deffs[i] = decorated  # This will cause the NEXT one to be removed
  deff =  DEF_DELIM.join([deff for deff in deffs if deff]) 
  deff = deff.strip().strip(";")
  return deff

with open(definitions_fname, "r") as f:
  for line in f:
    parts = line.strip().split("\t")
    if len(parts) >=3:
      ci, pinyins, deff = parts[0:3]
      deff = deff.replace("/", DEF_DELIM)
      # # I think this is no longer relevant, but doesn't hurt
      # if deff.startswith("/") and deff.endswith("/"):
      #   deff = deff[1:-1].replace("/", DEF_DELIM)
      # if re.findall("[a-zA-Z]/[a-zA-Z]", deff):
      #   deff = deff.replace("/", DEF_DELIM)
      deff = fix_cedict_deff(deff)
      deff = canonicalize_def_list(deff)
      if "||" in pinyins:
        CI_TO_MULTI_PINYIN[ci] = decode_multipinyin(pinyins)
      DEFINITIONS[ci] = deff


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
    "介",  # preposition
    "形",  # adjective
    "、",
}) + "]+）"

# add in the existing definitions
def add_existing_defs(LEVELS_TO_DO):
  for level in LEVELS_TO_DO:
    with open(f"resources/vocab_separate/{level}.tsv", "r") as f:
      for line in f:
        parts = line.strip().split("\t")
        if len(parts) >=3:
          ci, unused_pinyin, deff = parts[0:3]
          existing_defs_lower = DEFINITIONS.get(ci, '').lower().split(DEF_DELIM)
          if deff.lower() in existing_defs_lower: continue
    
          existing_defs = DEFINITIONS.get(ci, '').split(DEF_DELIM)
          stripped = re.sub(chinese_pos_regex, "", ci)
          if stripped != ci and stripped in DEFINITIONS:
            existing_defs += DEFINITIONS[stripped].split(DEF_DELIM)
    
          deff = fix_cedict_deff(DEF_DELIM.join([deff] + existing_defs))
          deff = canonicalize_def_list(deff)
          DEFINITIONS[ci] = deff

