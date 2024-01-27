import regex as re
import pinyin_jyutping_sentence
from glob import glob
DOWNLOADS = "/Users/icaswell/Downloads"
levels="hsk1 hsk2 hsk3".split()
# levels="hsk4 hsk5 hsk6".split()
# levels="hsk5".split()



# with open("resources/vocab_combined/all_ci.tsv", "r") as f:
#     all_ci = {line.split("\t")[0]: line for line in f}
# 
# with open("resources/vocab_combined/all_ci.tsv", "r") as f:
#     all_ci_list = [line.split("\t")[0] for line in f]
# 
# print(len(all_ci))

extra_pinyin = {}
extra_defs = {}
for fname in glob("resources/vocab_separate/*"): 
  with open(fname, "r") as f:
      print(fname)
      for line in f:
          parts = line.strip().split("\t", maxsplit=2)
          if len(parts) != 3:
              print(line)
              continue
          ci, pinyin, meaning = parts
          meaning =meaning.replace("\t", ". ")
          # if ci not in all_ci:
          #     all_ci[ci] = f"{ci}\t{meaning}\n"
          #     all_ci_list.append(ci)
          extra_pinyin[ci] = pinyin
          extra_defs[ci] = meaning

CCEDICT = {}
with open("resources/cedict_1_0_ts_utf-8_mdbg.txt", "r") as f:
  for line in f:
    # line = '五寨縣 五寨县 [Wu3 zhai4 xian4] /Wuzhai county in Xinzhou 忻州[Xin1 zhou1], Shanxi/'
    m = re.match("(^[\p{Han}]+) ([\p{Han}]+) \[([^\]]+)\](.*)", line.strip())
    if not m: continue
    g = [gi.strip() for gi in m.groups()]
    if len(g) != 4: continue
    CCEDICT[g[1]] = (g[2], g[3])


with open("missing", "r") as f:
  with open("missing.def", "w") as outf:
    for line in f:
        ci = line.strip()
        if ci in CCEDICT:
          outf.write(f"{ci}\t{CCEDICT[ci][1]}\n")
        elif ci in extra_defs:
          outf.write(f"{ci}\t{extra_defs[ci]}\n")
        else:
          print(ci)
      

def write_pinyin(outf, ci):
  if ci in extra_pinyin:
    pinyin = extra_pinyin[ci]
  else:
    pinyin, _ = CCEDICT.get(ci, ("-", "no definition found"))
    pinyin = pinyin_jyutping_sentence.romanization_conversion.decode_pinyin(pinyin, False, False)
  pinyin = pinyin if pinyin else "-"
  outf.write(f"{ci}\t{pinyin}\n")

already_written = set()
with open("resources/vocab_combined/all_ci.tsv", "r") as f:
  with open("resources/vocab_combined/all_ci_and_zi_pinyin.tsv", "w") as outf:
    for line in f:
      parts = line.strip().split("\t")
      if len(parts) != 2:
        print(line.strip())
        continue
      to_do = {zi for zi in parts[0]} | {parts[0]}
      for ci in to_do:
        if ci in already_written: continue
        write_pinyin(outf, ci)
        already_written.add(ci)

# with open("input/multizi_input.txt", "r") as f:
#   with open("input/multizi_input.tsv", "w") as outf:
#     for line in f:
#       ci = line.strip()
#       deff = CCEDICT.get(ci, "no definition found")

# for level in levels:
#   with open(HERE + "/" + level + ".tsv", "r") as f:
#     # with open(DOWNLOADS + "/" + level + ".tsv", "w") as outf:
#     with open(HERE + "/" + level + ".cedict.tsv", "w") as outf:
#       for line in f:
#         parts = line.replace("\n", "").split("\t")
#         if len(parts) != 3:
#           print("oops: ", line)
#         zi, pinyin, deff = parts
#         if zi not in CCEDICT: print(level, zi, deff)
#         deff = CCEDICT[zi] if zi in CCEDICT else deff
#         outf.write(f"{zi}\t{pinyin}\t{deff}\n")
# # print(CCEDICT.keys())

