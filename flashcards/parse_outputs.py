import regex as re

infile="output/all_ci_shorter__gpt-3.5-turbo-1106_t=0.0_c=10__cql3.txt"
outfile="resources/example_sentences/cql.tsv"


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
  with open(outfile, "w") as outf:
    for line in f:
      is_ok, parts = process_line(line)
      if is_ok:
        outf.write("\t".join(parts) + "\n")

print(outfile)
  
