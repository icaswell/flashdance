import regex as re
HERE = "/Users/icaswell/Documents/dancing_miao/lexicons"
DOWNLOADS = "/Users/icaswell/Downloads"
levels="hsk1 hsk2 hsk3".split()
# levels="hsk4 hsk5 hsk6".split()
# levels="hsk5".split()

CCEDICT = {}
with open(HERE + "/cedict_1_0_ts_utf-8_mdbg.txt") as f:
  for line in f:
    # line = '五寨縣 五寨县 [Wu3 zhai4 xian4] /Wuzhai county in Xinzhou 忻州[Xin1 zhou1], Shanxi/'
    m = re.match("(^[\p{Han}]+) ([\p{Han}]+) \[([^\]]+)\](.*)", line.strip())
    if not m: continue
    g = [gi.strip() for gi in m.groups()]
    if len(g) != 4: continue
    CCEDICT[g[1]] = g[3]


for level in levels:
  with open(HERE + "/" + level + ".tsv", "r") as f:
    # with open(DOWNLOADS + "/" + level + ".tsv", "w") as outf:
    with open(HERE + "/" + level + ".cedict.tsv", "w") as outf:
      for line in f:
        parts = line.replace("\n", "").split("\t")
        if len(parts) != 3:
          print("oops: ", line)
        zi, pinyin, deff = parts
        if zi not in CCEDICT: print(level, zi, deff)
        deff = CCEDICT[zi] if zi in CCEDICT else deff
        outf.write(f"{zi}\t{pinyin}\t{deff}\n")
# print(CCEDICT.keys())


