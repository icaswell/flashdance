# from https://www.berlitz.com/blog/chinese-radicals-list

# This is a module in this package
from pinyin import get_pinyin


SINGLEWORD_DEFS = {}

with open("resources/definitions_and_pinyin/zi_singleword_defs.tsv", "r") as f:
  for i, line in enumerate(f):
    zi, deff = line.strip().split("\t")
    SINGLEWORD_DEFS[zi] = deff

def format_examples(examples_str):
  ex = []
  for zi in examples_str.split():
    assert(len(zi) == 1)
    deff = SINGLEWORD_DEFS.get(zi, "no definition found...this must be a very obscure character")
    pinyin = get_pinyin(zi)
    ex.append(zi)
    ex.append(f"[{pinyin}] {deff}")
    assert '"' not in ex[-1]
  if not ex:
    ex = ["no example characters" ,"possibly this is a rare radical"]
  return ex

with open("flashcards/iphone/radicals.flashcards.iphone.csv", "w") as outf:
  with open("resources/radicals.tsv", "r") as f:
    for line in f:
      no, radical, pinyin, meaning, examples = line.replace("\n", "").split("\t")
      radical = f"{radical}（部首 #{no}）"
      pinyin = f"{pinyin} (bù shǒu #{no})"
      meaning = f"{meaning} (radical #{no})"
      examples = format_examples(examples)
      parts = [radical, pinyin, meaning] + examples
      outf.write(";".join([f'"{x}"' for x in parts]) + "\n")




