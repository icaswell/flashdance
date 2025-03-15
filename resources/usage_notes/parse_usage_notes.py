from glob import glob
import regex as re

def ignore_usage_note(note):
  # One might want to include these, e.g.:
  # There is no difference between the use of 玩儿 (wánr) in Chinese and "to play" or "to have fun" in English.
  # howeve,r in practice this probably mainly adds to the noise.
  # punts = ["There is no difference", "No special notes.", "No additional notes.", "Nothing special to note.",  "There's nothing special about this word."]
  punts = ["There is no difference", "No special notes.", "No additional notes.", "othing special", "No unusual notes.", "No special usage notes."]
  for punt in punts:
    if punt in note: return True
  return False



HAN_REGEX_INC = "[《\p{Han}0-9““<>]"


NEWLINE = "<NEWLINE>"
INPUT_DELIM = "~"  # input delimitor
DUPLICATE_OUTPUT_DELIM = f"--------"
USAGE = []
mothership = "resources/usage_notes/usage_notes.tsv"
with open(mothership, "r") as f:
  for line in f:
    ci, note = line.strip().split("\t")
    note = note.replace(NEWLINE, "\n").strip()
    notes = {n.strip() for n in note.split(DUPLICATE_OUTPUT_DELIM) if n.strip()}
    USAGE.append((ci, notes))

def strip_pinyin(ci):
  # e.g. "毛笔 (máobǐ)" -> "毛笔"
  if "(" not in ci: return ci
  # ensure that there is exactly one Han char in the beginning bit
  # m = re.match("(.*\p{Han}.*) \(\p{Latn}*\)", s)
  return re.sub(" \([^\p{Han}]*\)", "", ci)

USAGE_DICT = dict(USAGE)
# NEW_USAGE = []
for fname in glob("output/usage_notes.*"):
  with open(fname, "r") as f:
    content = f.read()
    for chunk in content.split(INPUT_DELIM):
      chunk = chunk.strip()
      if not chunk: continue
      lines =  chunk.replace("\t", "").split("\n")
      # if "\t" in chunk:
      #   print("Error[TABS]:", chunk.replace("\t", "<TAB>"), fname)
      #   continue

      ci = lines[0]
      notes = []
      ciparts = ci.split(" - ", maxsplit=1)
      if len(ciparts) > 1:
        lines.insert(1, ciparts[1].strip())
      ci = ciparts[0].strip()

      if len(lines) == 1 and re.search("\p{Han}{1,5} \([^)]{1,20}\) ", lines[0]):
        ci = re.findall("^\p{Han}+", lines[0])[0]
        lines = [ci] + lines

      if len(lines) <= 1 and chunk:
        print("\n", fname)
        print("Error[short]:", chunk)
        continue
      if not re.search(HAN_REGEX_INC, ci):
        print("\n", fname)
        print("Error[ci is not in Hanzi]:", chunk)
        continue

      note = "\n".join(lines[1:]).strip()

      if ci in USAGE_DICT:
        old_notes = USAGE_DICT[ci]
        if note in old_notes:
          continue
        else:
          old_notes.add(note)
          USAGE_DICT[ci] = old_notes
          # print(USAGE_DICT[ci])
          # print("~~~"*30)
          # print(f"new notes for {ci}:")
      else: 
        USAGE_DICT[ci] = {note}

def process_notes(raw_notes):
  raw_notes = list(raw_notes)
  # contains_punt = any([ignore_usage_note(n_i) for n_i in raw_notes])
  notes = [n_i for n_i in raw_notes if n_i and not ignore_usage_note(n_i)]
  out = notes[0] if notes else raw_notes[0]
  for n_i in notes[1:]:
    out = out + "\n" + DUPLICATE_OUTPUT_DELIM + "\n" + n_i
  return out.replace("\n", NEWLINE)

with open(mothership, "w") as f:
  for ci, notes in USAGE_DICT.items():
    note = process_notes(notes)
    line = f"{ci}\t{note}\n"
    f.write(line)



