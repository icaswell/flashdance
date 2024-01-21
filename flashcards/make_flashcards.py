import csv
import regex as re
import pinyin_jyutping_sentence


# fname="/Users/icaswell/Documents/dancing_miao/flashcards/sample1.csv"
fname_out="/Users/icaswell/Documents/dancing_miao/flashcards/sample1.flashcards.csv"


pinyin_fname = "/Users/icaswell/Documents/dancing_miao/flashcards/hsk1to6.tsv"
zi_definitions_fname = "resources/zi_singleword_defs.tsv"
use_same_zi_fname = "resources/use_same_zi/mega_hanzi.tsv"

relatedwords_fname = "resources/related_words/hsk1to6.tsv"
examples_fname ="resources/example_sentences/cql.tsv"
NEWLINE = "\r"


PINYIN = {}
with open(pinyin_fname, "r") as f:
  for line in f:
    parts = line.strip().split("\t")
    PINYIN[parts[0]] = parts[1]

ZI_DEFS = {}
with open(zi_definitions_fname, "r") as f:
  for line in f:
    parts = line.strip().split("\t")
    ZI_DEFS[parts[0]] = parts[1]

# i zi  first_occurence hsk1  hsk2  hsk3  hsk4  hsk5  hsk6  nhsk1 nhsk2 nhsk3 nhsk4 nhsk5 nhsk6 stront1 weeb1  
USE_SAME_ZI = {}
with open(use_same_zi_fname, "r") as f:
  for line in f:
    parts = line.strip().split("\t")
    USE_SAME_ZI[parts[1]] = parts[7]  # TODO handle logic for only the level below and equal

RELATED_WORDS = {}
with open(relatedwords_fname, "r") as f:
  for line in f:
    parts = line.strip().split("\t")
    RELATED_WORDS[parts[0]] = parts[1]

EXAMPLES = {}
with open(examples_fname, "r") as f:
  for line in f:
    parts = line.strip().split("\t")
    EXAMPLES[parts[0]] = parts[1]
  

def bold_han(s):
  # return s
  return re.sub("- (\p{Han}+( \([^\)]*\):)?)", "\r\\1\r", s)
  return re.sub("(\p{Han}+( \([^\)]*\):)?)", "**\\1**", s)


out_lines = []

CI_FIELD = lines[0].index("Chinese")
PINYIN_FIELD = lines[0].index("pinyin")
DEF_FIELD = lines[0].index("short definition")


RELATED_WORDS_FIELD = lines[0].index("related words")

ZI_FIELDS = [
(lines[0].index("zi 1"), lines[0].index("zi 1 examples")),
(lines[0].index("zi 2"), lines[0].index("zi 2 examples")),
(lines[0].index("zi 3"), lines[0].index("zi 3 examples")),
(lines[0].index("zi 4"), lines[0].index("zi 4 examples")),
]

EX_FIELDS = [
(lines[0].index("ex 1 Chinese"), lines[0].index("ex 1 English")),
(lines[0].index("ex 2 Chinese"), lines[0].index("ex 2 English")),
(lines[0].index("ex 3 Chinese"), lines[0].index("ex 3 English")),
(lines[0].index("ex 4 Chinese"), lines[0].index("ex 4 English")),
(lines[0].index("ex 5 Chinese"), lines[0].index("ex 5 English")),
(lines[0].index("ex 6 Chinese"), lines[0].index("ex 6 English")),
]

def pinyin(s):
  p =  pinyin_jyutping_sentence.pinyin(s)
  p = p.replace(" huán ", " hái ")
  p = p.replace(" dū ", " dōu ")
  return p

for line in lines[1:]:
  out_lines.append([])
  out_lines[-1].append(line[CI_FIELD]) 
  out_lines[-1].append(line[PINYIN_FIELD]) 
  out_lines[-1].append(line[DEF_FIELD]) 

  if line[RELATED_WORDS_FIELD]:
      out_lines[-1].append("related words")
      # out_lines[-1].append("tmp")
      out_lines[-1].append(bold_han(line[RELATED_WORDS_FIELD]))

  for zi_field, other_ci_field in ZI_FIELDS:
    if line[zi_field]:
      out_lines[-1].append(line[zi_field])
      if line[other_ci_field]:
        other_ci_list = []
        for ci in line[other_ci_field].split(";"):
          ci = ci.strip()
          if ci in PINYIN:
            ci = f"{ci} ({PINYIN[ci]})"
          other_ci_list.append(ci)

        out_lines[-1].append("Other words using this character: " + "; ".join(other_ci_list))
      else:
        out_lines[-1].append("There are no other HSK words in this level (or before) using this character.")

  seen_examples = set()
  for ex_zh_field, ex_en_field in EX_FIELDS:
    if line[ex_zh_field].startswith("#"): continue
    if line[ex_zh_field]:
      if line[ex_zh_field] in seen_examples: continue
      seen_examples.add(line[ex_zh_field])
      out_lines[-1].append(line[ex_zh_field])
      out_lines[-1].append(line[ex_en_field])

  
out_lines = [
        [field.replace("\n", NEWLINE) for field in out_line]
        for out_line in out_lines
        ]

# writing to csv file
with open(fname_out, 'w') as csvfile:
  csvwriter = csv.writer(csvfile, delimiter =';', quoting=csv.QUOTE_ALL)
  csvwriter.writerows(out_lines)
