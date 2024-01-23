
HERE = "/Users/icaswell/Documents/dancing_miao/lexicons"
levels="hsk4 hsk5 hsk6".split()
levels="hsk5".split()

def isss(a, b):
  # is strict substring
  if " " not in b: return False
  # if len(a) >= len(b): return False
  return (a in b) and (a != b)

def split_def(deff):
  out = ['']
  in_parenthetical = False
  for ch in deff:
    if ch == "(": in_parenthetical = True
    if in_parenthetical:
      out[-1] += ch
      if ch == ")": in_parenthetical = False
      continue
    if ch in {',', ';'}:
      out.append('')
    else:
      out[-1] += ch
  return [x.strip() for x in out]

def join_def(deff):
  out = ""
  for i, d in enumerate(deff):
    if i:
      if d.startswith("CL"):
        out += ", "
      else:
        out += "; "
    out += d
  return out

for level in levels:
  with open(HERE + "/" + level + ".tsv", "r") as f:
    for line in f:
      parts = line.strip().split("\t")
      if len(parts) != 3:
        print("oops: ", line)
      zi, pinyin, deff = parts
      # print(deff ,  "-->", split_def(deff))
      # print(deff)
      deff = split_def(deff)
      # print(deff)
      outdef = []
      for i, d in enumerate(deff):
        this_is_redundant = False
        for j, dj in enumerate(deff):
          if i == j: continue
          if d == dj and i > j: this_is_redundant = True
          # print(f"   '{d}' | '{dj}' | {isss(d, dj)}")
          if isss(d, dj): this_is_redundant = True
        if not this_is_redundant:
          outdef.append(d)
      print(f"{zi}\t{pinyin}\t{join_def(outdef)}")

