
with open("resources/vocab_combined/all_ci.tsv", "r") as f:
  with open("resources/vocab_combined/all_multici.tsv", "w") as outf:
    for line in f:
      ci, deff = line.strip().split("\t")
      if len(ci) > 1:
        outf.write(line)

