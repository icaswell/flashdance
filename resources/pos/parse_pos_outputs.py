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
POS_REGEX = "^[a-z/]*$"

def process_line(line):
  """

  Args:
    line: some TSV line that a LLM produced. Supposed to be of the format:
    <chinese>  <slash-separated POS>

  Returns:
    is_ok [bool]: False if there was a problem with input
    parts [List[str]]: line with ci and then pos

  """
  if not re.match(HAN_REGEX_INC, line[0]):
    return False, ["doesn't start Han"]
  parts = line.strip().split("\t")
  if len(parts) < 2: 
    return False, ["too short"]
  if len(parts) > 2: 
    return False, ["too long"]
  if not re.match(POS_REGEX, parts[1]):
    return False, ["pos is wonky"]

  return True, parts


def hash_string(line):
  return re.sub("\s", "", line)

def parse_glob(inglob, outfile, overwrite):
  print(overwrite)
  already_seen = set()
  if not overwrite:
    with open(outfile, "r") as f:
      old_lines = [line for line in f]
    # don't acidentally keep appending to same file
    already_seen = {hash_string(line) for line in old_lines}
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
            outf.write(outline)
          elif re.match(HAN_REGEX, line):
            print(i + 1, line.strip())
            for j, p_i in enumerate(parts):
              print(f"    {j}: {p_i}")
      print(f"^^ {infile}")
  print(outfile)
  

parse_glob(args.inglob, args.outfile, args.overwrite)
