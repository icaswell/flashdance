
def load(fname):
  out = {}
  with open(fname, "r") as f:
    for line in f:
      try:
        a, b = line.split(": ")
      except:
        print(line)
      b = "/".join(sorted(b.split("/")))
      out[a] = b
  return out

def get_acc(out, golden):
  if out.keys() != golden.keys():
    raise ValueError(f"keys don't match.\n  Missing: {golden.keys() - out.keys()}\n  Extra: {out.keys() - golden.keys()}")
  n1, c1 = 0, 0
  tp, fp, fn = 0, 0, 0
  for k, pos in out.items():
    n1 += 1
    if pos == golden[k]:
      c1 += 1
    gold_pos = set(golden[k].split("/"))
    for pos_i in pos.split("/"):
      if pos_i in gold_pos:
        tp += 1
      else:
        fp += 1
    for pos_i in gold_pos:
      if pos_i not in pos.split("/"):
        fn = 1
  p = tp/(tp + fp)
  r = tp/(tp + fn)
  return c1/n1, p, r



golden = load("golden.eval")

print("model\tacc\tp\tr")
for fname in ["gpt3p5.eval", "gemini_advanced.eval"]:
  out = load(fname)
  acc, p, r = get_acc(out, golden)
  print(f"{fname[0:6]}\t{acc:.1%}\t{p:.1%}\t{r:.1%}")
