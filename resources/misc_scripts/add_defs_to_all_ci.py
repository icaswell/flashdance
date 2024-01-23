import regex as re

ci = []
with open("lexicons/all_ci.txt", "r") as f:
  for line in f:
    ci.append(line.strip())

CCEDICT = {}
with open("lexicons/cedict_1_0_ts_utf-8_mdbg.txt") as f:
  for line in f:
    # line = '五寨縣 五寨县 [Wu3 zhai4 xian4] /Wuzhai county in Xinzhou 忻州[Xin1 zhou1], Shanxi/'
    m = re.match("(^[\p{Han}]+) ([\p{Han}]+) \[([^\]]+)\](.*)", line.strip())
    if not m: continue
    g = [gi.strip() for gi in m.groups()]
    if len(g) != 4: continue
    CCEDICT[g[1]] = g[3]

STRONT = {}
with open("lexicons/stront1.tsv") as f:
  for line in f:
    parts = line.replace("\n", "").split("\t")
    if len(parts) < 3: continue
    STRONT[parts[0]] = parts[2]


WEEB = {}
with open("lexicons/weeb1.tsv") as f:
  for line in f:
    parts = line.replace("\n", "").split("\t")
    if len(parts) < 4: continue
    WEEB[parts[1]] = parts[3]
    if len(parts) >=5 and parts[4]:
      WEEB[parts[1]] += ". " + parts[4]


ci_defined = []
for cj in ci:
  if cj in CCEDICT:
    deff = CCEDICT[cj][1:-1].replace("/", "; ")
  elif cj in STRONT:
    deff = STRONT[cj]
  elif cj in WEEB:
    deff = WEEB[cj]
  else:
    deff = None
  if deff:
    ci_defined.append((cj, deff))

ci_defined = sorted(ci_defined, key=lambda x: len(x[1]))

with open("lexicons/all_ci.tsv", "w") as f:
  for (cj, deff) in ci_defined:
    f.write(f"{cj}\t{deff}\n")
