import json
from glob import glob

# TODO put this in a utils file
# the path of this script
HERE = "/Users/icaswell/Documents/dancing_miao/lexicons"
COLORS = {
    "underline": 4,
    "flashing": 5,
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "pink": 35,
    "teal": 36,
    "grey": 37,
    "white_highlight": 7,
    "black_highlight": 40,
    "red_highlight": 41,
    "green_highlight": 42,
    "yellow_highlight": 43,
    "blue_highlight": 44,
    "pink_highlight": 45,
    "teal_highlight": 46,
    "grey_highlight": 47,
}
COLOR_END =  "\033[0m"


def colorize(s:str, color:str) -> str:
    s = str(s)
    if color not in COLORS: return s
    return f"{COLORS[color]}{s}{COLOR_END}"


test_passes = True
for fname in glob(HERE + "/*json"):
  with open(fname, "r") as f:
    lex = json.load(f)

  #========================================================
  # simple test: make sure everything is nonempty
  for hanzi, pinyin in lex.items():
    if not hanzi:
      print(colorize(f"Warning, empty Hanzi! (pinyin={pinyin}", "red"))
      test_passes = False
    if not pinyin:
      print(colorize(f"Warning, empty pinyin! (hanzi={hanzi}", "red"))
      test_passes = False

  print(f"File {fname} has {colorize(len(lex), 'teal')} terms")

