import regex as re
from collections import defaultdict
HERE = "/Users/icaswell/Documents/dancing_miao/lexicons"
levels="hsk1 hsk2 hsk3 hsk4 hsk5 hsk6".split()
# levels="hsk1 hsk2 hsk3 hsk4".split()
# levels="hsk1".split()


def normalize_def(deff):
  # deffa = deff
  deff = deff.lower()
  deff = re.sub(" (at|for|to|with|through|against|without|around|out|in|by|after|of|up|off)$", "", deff)
  deff = re.sub("\p{Han}", "", deff)
  # deff = re.sub("([^ ]*[\p{Han}]+[^ ]*)", "", deff)
  deff = re.sub("^(a|the|to|be) ", "", deff)
  deff = re.sub("^\([^\)]*\) ", "", deff)
  deff = deff.replace(".", "")
  deff = deff.split("(")[0]
  deff = deff.split(",")[0]
  deff = deff.replace("to ", "")
  # if not deff.strip(): return deffa
  return deff.strip()

def read_tsv(level, src):
  assert src == "old" or src == "cedict"
  ret = []
  with open(HERE + f"/{level}.{src}.tsv", "r") as f:
    for line in f:
      parts = line.replace("\n", "").split("\t")
      zi, pinyin, deffs = parts
      delim = "/" if src == "cedict" else ";"
      deffs = deffs.split(delim)
      deffs = [d.strip() for d in deffs if d.strip()]
      ret.append((zi, deffs))
  return ret

# sign	标记
# to sign (an agreement)	签署
# to sign (one's name)	签
# to sign up (for)	报名
# signal	信号


ci_to_norm = defaultdict(set)
norm_to_cis = defaultdict(list)
ci_to_defs = defaultdict(list)
ci_to_level = {}

for level in levels:
  for ci, defs in read_tsv(level, "old"):
    ci_to_level[ci] = level
    for deff in defs:
      ci_to_defs[ci].append(deff)
      deffnorm = normalize_def(deff)
      if not deffnorm: continue
      ci_to_norm[ci].add(deffnorm)
      if ci not in norm_to_cis[deffnorm]:
        norm_to_cis[deffnorm].append(ci)

ci_to_related = defaultdict(set)

for ci, norms in ci_to_norm.items():
  for deffnorm in norms:
    for cj in norm_to_cis[deffnorm]:
      if ci_to_level[cj] > ci_to_level[ci]: continue
      if ci == cj: continue
      ci_to_related[ci].add(cj)

for ci, defs in ci_to_defs.items():
  ci_to_defs[ci] =  "; ".join(ci_to_defs[ci])

# for ci, related in ci_to_related.items():
#   print("\n#" + "-"*79)
#   print(f"{ci}\t{ci_to_defs[ci]}")
#   for cj in related:
#     print(f" • {cj}\t{ci_to_defs[cj]}")

for ci, related in ci_to_related.items():
  print("\t".join([cj] + related))

# print("ci_to_defs")
# print(ci_to_defs)
# print()
# print("norm_to_cis")
# print(norm_to_cis)
# print()
# print("ci_to_related")
# print(ci_to_related)

# def customsorter(s):
#   return s[0]
# norm_to_cis = sorted(norm_to_cis.items(), key=customsorter)
# for en, zis in norm_to_cis:
#   ziss = '\t'.join(zis)
#   print(f"{en}|\t{ziss}")
# 

# for each character, list other chars that are similar



