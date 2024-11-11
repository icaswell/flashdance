import regex as re
from glob import glob
import argparse

parser = argparse.ArgumentParser(description='Process input file and save the result to an output file.')
parser.add_argument('--inglob', dest='inglob', required=True, help='Input file glob')
parser.add_argument('--outfile', dest='outfile', required=True, help='File in resources/ to write the parsed outputs to')
parser.add_argument('--overwrite', action='store_true', help='')
args = parser.parse_args()



HAN_REGEX = "[《\p{Han}]"
HAN_REGEX_INC = "[《\p{Han}0-9““<>]"

def process_line(line):
  """

  Args:
    line: some TSV line that a LLM produced. Supposed to be of the format:
    <chinese>  [<pinyin that we ignore>] <Chinese example sentence 1> <def thereof> ....

  Returns:
    is_ok [bool]: False if there was a problem with input
    parts [List[str]]: line with fields:
      0. Hanzi
      [1:]. pairs of [zh, en] examples

  """
  if not re.match(HAN_REGEX_INC, line[0]):
    return False, ["doesn't start Han"]
  parts = line.strip().split("\t")
  if len(parts) < 2: 
    return False, ["too short"]

  if len(parts) == 2 and re.search(HAN_REGEX, parts[0]) and not re.search(HAN_REGEX, parts[1]):
    # special case where the input is a simple TSV with [Hanzi, example] (?)
    # TODO (Isaac) how "NA" a valid Hanzi ?? Must be for example sentences that a are
    # from some source but not associated with a specific Hanzi on purpose.
    return True, ['NA'] + parts

  # the second field may optionally be a definition (or empty); if so we ignore it
  # AKA we require it have at least one Hanzi
  field_is_definition =  " CL:" in parts[1] or "abbr. for" in parts[1] or "|" in parts[1]
  field_is_definition |= bool(re.search(HAN_REGEX, parts[1]))
  if not parts[1] or field_is_definition:
    parts = [parts[0]] + parts[2:]

  # the second field may optionally be a pinyin; if so we ignore it
  # AKA we require it have at least one Hanzi
  if not parts[1] or not re.search(HAN_REGEX, parts[1]):
    parts = [parts[0]] + parts[2:]

  if len(parts) < 2: 
    return False, ["too short B"]

  parts = [part for part in parts if not part == 'golden sentence']

  for i, part in enumerate(parts[1:]):
    # (note we are looping only over examples so these are actually odd fields in `parts`)
    # even fields should be Chinese
    if i%2 == 0 and not re.search(HAN_REGEX_INC, part):
      return False, [f"zh field {i} not Han: {part}"] + parts
    # odd fields should not be Chinese. OK if they have a few characters.
    if i%2 != 0 and len(re.findall(HAN_REGEX, part)) > 4:
      return False, [f"en field {i} Han: {part}"] + parts
  return True, parts


def hash_string(line):
  return re.sub("\s", "", line)


def parse_glob(inglob, outfile, overwrite):
  already_seen = set()
  if not overwrite:
    with open(outfile, "r") as f:
      old_lines = [line for line in f]
    # don't acidentally keep appending to same file
    already_seen = {hash_string(line) for line in old_lines}
  n_errors = 0
  n_good = 0
  with open(outfile, "w" if args.overwrite else "a") as outf:
    for infile in glob(inglob):
      print("\n\n" + '-'*80 + f"\nREADING {infile}")
      with open(infile, "r") as f:
        for i, line in enumerate(f):
          is_ok, parts = process_line(line)
          outline = "\t".join(parts) + "\n"
          if hash_string(outline) in already_seen:
            continue
          if is_ok:
            n_good += 1
            outf.write(outline)
          elif re.match(HAN_REGEX, line):
            n_errors += 1
            print("\nError: ", parts[0])
            print(i + 1, line.strip().replace("\t", "<   TAB   >"))
            for j, p_i in enumerate(parts[1:]):
              print(f"    {j}: {p_i}")
      print(f"^^ {n_errors} errors of {n_good + n_errors} lines")
      print(f"^^ {infile}")
  print(outfile)
  

parse_glob(args.inglob, args.outfile, args.overwrite)
# parse_glob("output/*4o*multicoverage*", "resources/example_sentences/multicoverage_4o.tsv")
# parse_glob("output/*cql*", "resources/example_sentences/cql.tsv")
# parse_glob("output/*general*", "resources/example_sentences/general2.tsv")
# parse_glob("output/*raccoon*", "resources/example_sentences/raccoon.tsv")
