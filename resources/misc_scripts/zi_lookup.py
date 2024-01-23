import regex as re
from collections import defaultdict

DOWNLOADS = "/Users/icaswell/Downloads"
levels="hsk1 hsk2 hsk3".split()
# levels="hsk4 hsk5 hsk6".split()
# levels="hsk5".split()
HERE = "/Users/icaswell/Documents/dancing_miao/lexicons"
levels="hsk1 hsk2 hsk3 hsk4 hsk5 hsk6 nhsk1 nhsk2 nhsk3 nhsk4 nhsk5 nhsk6 stront1 weeb1".split()

all_zi = set()
for level in levels:
  if not level: continue
  with open(HERE + "/" + level + ".txt", "r") as f:
    for line in f:
      zi = set(re.findall("\p{Han}", line))
      all_zi |= zi


CCEDICT = defaultdict(list)
PINYINDICT = defaultdict(set)
with open(HERE + "/cedict_1_0_ts_utf-8_mdbg.txt") as f:
  for line in f:
    # line = '五寨縣 五寨县 [Wu3 zhai4 xian4] /Wuzhai county in Xinzhou 忻州[Xin1 zhou1], Shanxi/'
    m = re.match("(^[\p{Han}]+) ([\p{Han}]+) \[([^\]]+)\](.*)", line.strip())
    if not m: continue
    g = [gi.strip() for gi in m.groups()]
    if len(g) != 4: continue
    CCEDICT[g[1]].append(g[3])
    PINYINDICT[g[1]].add(g[2])
    if len(g[1]) == 2 and g[1][0] == g[1][1]:
      CCEDICT[g[1][0]].append(g[3])

for zi in all_zi:
  if zi in CCEDICT:
    defs = '/'.join(CCEDICT[zi])
    defs = re.sub("//+", "/", defs)
    pinyin = ";".join(PINYINDICT[zi])
    print(f"{zi}\t{pinyin}\t{defs}")
  else:
    print(f"{zi}\tno pinyin found\tno definition found")
