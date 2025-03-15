
out = []

seen = set()

for i in [3, 2, 1]:
  with open(f"stront{i}.tsv", "r") as f:
    for line in f:
      h = line.split("\t")[0]
      if h in seen: continue
      seen.add(h)
      out.append(line)

  
with open(f"stront123.tsv", "w") as f:
  for line in out:
    f.write(line)
  



