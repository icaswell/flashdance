import regex as re
from glob import glob


HAN_REGEX = "[《\p{Han}]"
HAN_REGEX_INC = "[《\p{Han}0-9““<>]"

def process_line(line):
  """

  Args:
    line: some TSV line that a LLM produced. Supposed to be of the format:
    <chinese>  [<pinyin that we ignore>] <Chinese example sentence 1> <def thereof> ....
  """
  if not re.match(HAN_REGEX_INC, line[0]):
    return False, ["doesn't start Han"]
  parts = line.strip().split("\t")
  if len(parts) < 2: 
    return False, ["too short"]

  if len(parts) == 2 and re.search(HAN_REGEX, parts[0]) and not re.search(HAN_REGEX, parts[1]):
    # special case where the input is a simple TSV 
    return True, ['NA'] + parts

  # the second field may optionally be a definition (or empty); if so we ignore it
  # AKA we require it have at least one Hanzi
  if not parts[1] or not re.search(HAN_REGEX, parts[1][0]):
    parts = [parts[0]] + parts[2:]


  if len(parts) < 2: 
    return False, ["too short B"]

  # the second field may optionally be a pinyin; if so we ignore it
  if not parts[1] or not re.match(HAN_REGEX, parts[1][0]):
    parts = [parts[0]] + parts[2:]
  parts = [part for part in parts if not part == 'golden sentence']

  for i, part in enumerate(parts[1:]):
    # even fields should be Chinese
    if i%2 == 0 and not re.search(HAN_REGEX_INC, part):
      return False, [f"zh field {i} not Han: {part}"] + parts
    # odd fields should not be Chinese. OK if they have a few characters.
    if i%2 != 0 and len(re.findall(HAN_REGEX, part)) > 4:
      return False, [f"en field {i} Han: {part}"] + parts
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
            print(i + 1, line.strip())
            for j, p_i in enumerate(parts):
              print(f"    {j}: {p_i}")
      print(f"^^ {infile}")
  print(outfile)
  

parse_glob("output/*4o*multicoverage*", "resources/example_sentences/multicoverage_4o.tsv")

# parse_glob("output/*cql*", "resources/example_sentences/cql.tsv")
# parse_glob("output/*general*", "resources/example_sentences/general2.tsv")
# parse_glob("output/*raccoon*", "resources/example_sentences/raccoon.tsv")
