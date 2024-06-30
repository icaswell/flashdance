import regex as re
from collections import defaultdict
from glob import glob



with open("resources/definitions_and_pinyin/list_of_singlezi_needing_defs.txt", "r") as f:
  all_ci = {line.strip() for line in f}

done = set()
ofname = "resources/definitions_and_pinyin/list_of_singlezi_needing_defs.out.tsv"
with open(ofname, "w") as outf:
  with open("resources/vocab_combined/all_ci_and_zi_defs.tsv", "r") as f:
    for line in f:
      zi, unused_pinyin, deff = line.replace("\n", "").split("\t")
      if zi in all_ci:
        outf.write(f"{zi}\t{deff}\n")
        done.add(zi)

print(all_ci - done)
print(ofname)



