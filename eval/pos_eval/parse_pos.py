import regex as re

def finesse(s):
  s = s.replace("adjective", "adj")
  s = s.replace("adverb", "adv")
  s = s.replace("conjunction", "conj")
  s = s.replace("interjection", "interj")
  s = s.replace("measure", "measure")
  s = s.replace("noun", "n")
  s = s.replace("preposition", "pp")
  s = s.replace("verb", "vb")
  return s

chonks = ['']
with open("pos_raw.txt", "r") as f:
  for line in f:
    line = finesse(line.strip())
    if not line:
      if chonks[-1]:
        chonks.append('')
    else:
      chonks[-1] = f"{chonks[-1]}\n{line}"

chonks = [c for c in chonks if c]
POSS = set()    
HANZI = []
def parse_chonk(chonk):
  global POSS
  hanzi = None
  poss = set()
  for line in chonk.split("\n"):
    m = re.match("(\p{Han}+)(.*)", line)
    if not m: continue
    hanzii, pos = m.groups()
    if hanzi and hanzi != hanzii:
      raise ValueError(f"argh: {hanzi}/{hanzii}")
    hanzi = hanzii
    pos = pos.strip().split("(")[0].strip()
    if not pos: continue
    pos = pos.lower()
    poss.add(pos)
    POSS.add(pos)
  print(f"{hanzi}: {'/'.join(sorted(list(poss)))}")
  global HANZI
  HANZI.append(hanzi)

for chonk in chonks:
  parse_chonk(chonk)

print()
print(';'.join(sorted(list(POSS))))
print("\n".join(HANZI))
