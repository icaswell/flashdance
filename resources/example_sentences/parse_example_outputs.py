import regex as re
from glob import glob


HAN_REGEX = "[《\p{Han}]"
HAN_REGEX_INC = "[《\p{Han}0-9““<>]"

def process_line(line):
  if not re.match(HAN_REGEX_INC, line[0]):
    return False, []
  parts = line.strip().split("\t")
  if len(parts) < 2: 
    return False, parts

  # the second field may optionally be a definition; if so we ignore it
  if not re.match(HAN_REGEX, parts[1][0]):
    parts = [parts[0]] + parts[2:]
  parts = [part for part in parts if not part == 'golden sentence']

  for i, part in enumerate(parts[1:]):
    # even fields should be Chinese
    if i%2 == 0 and not re.match(HAN_REGEX_INC, part):
      return False, ["a"] + parts
    # odd fields should not be Chinese
    if i%2 != 0 and re.match(HAN_REGEX, part):
      return False, ["b"] + parts
  return True, parts



def parse_glob(inglob, outfile):
  with open(outfile, "w") as outf:
    for infile in glob(inglob):
      print("\n\n" + '-'*80 + f"\nREADING {infile}")
      with open(infile, "r") as f:
        for i, line in enumerate(f):
          is_ok, parts = process_line(line)
          if is_ok:
            outf.write("\t".join(parts) + "\n")
          elif re.match(HAN_REGEX, line):
            print(i+1, line.strip())
  print(outfile)
  

parse_glob("output/*cql*", "resources/example_sentences/cql.tsv")
parse_glob("output/*general*", "resources/example_sentences/general2.tsv")
