import regex as re

infile="lexicons/all_ci_shorter.out.tsv"

HAN_REGEX = "[《\p{Han}]"

def process_line(line):
  if not re.match(HAN_REGEX, line[0]):
    return False, []
  parts = line.strip().split("\t")
  if len(parts) < 2: 
    return False, parts

  if not re.match(HAN_REGEX, parts[1][0]):
    parts = [parts[0]] + parts[2:]
  parts = [part for part in parts if not part == 'golden sentence']

  for i, part in enumerate(parts[1:]):
    # even fields should be Chinese
    if i%2 == 0 and not re.match(HAN_REGEX, part):
      return False, ["a"] + parts
    # odd fields should not be Chinese
    if i%2 != 0 and re.match(HAN_REGEX, part):
        return False, ["b"] + parts
  return True, parts

out = []
with open(infile, "r") as f:
  for line in f:
    is_ok, parts = process_line(line)
    if not is_ok and parts:
      print("\n    ".join(parts))

