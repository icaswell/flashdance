import regex as re
# hsk1.txt
# hsk2.txt
# hsk3.txt
# hsk4.txt
# hsk5.txt
# hsk6.txt
# nhsk1.txt
# nhsk2.txt
# nhsk3.txt
# nhsk4.txt
# nhsk5.txt
# nhsk6.txt
# stront1.txt
# weeb1.txt

HERE = "/Users/icaswell/Documents/dancing_miao/lexicons"
levels="hsk1 hsk2 hsk3 hsk4 hsk5 hsk6 stront1 weeb1".split()
# levels="nhsk1 nhsk2 nhsk3 nhsk4 nhsk5 nhsk6 stront1 weeb1".split()

levels="hsk1 hsk2 hsk3 hsk4 hsk5 hsk6 nhsk1 nhsk2 nhsk3 nhsk4 nhsk5 nhsk6 stront1 weeb1".split()


for level in levels:
  if not level: continue
  with open(HERE + "/" + level + ".txt", "r") as f:
    for line in f:
      zi = re.findall("\p{Han}", line)
      zi = [z for i, z in enumerate(zi) if z not in zi[0:i]]
      print(line.strip() + "\t" + "\t".join(zi))




# def get_level_dict():
#   return {}
# 
# 
# ZI = {}
# # {
# #  zi: [
# #       idx,
# #       first_occurrence,
# #       {
# #            "hsk1": ["z1", "z2", "z3"]
# #            "hsk2": ["z1", "z2", "z3"]
# #            .....
# #            }
# # }
# 
# 
# 
# for level in levels:
#   if not level: continue
#   with open(HERE + "/" + level + ".txt", "r") as f:
#     for line in f:
#       ci = re.split("[（…( ]", line.strip())[0]
#       for zi in set(re.findall("\p{Han}", line)):
#         if zi not in ZI:
#           ZI[zi] = [len(ZI), level, {lev_i:[] for lev_i in levels}]
#         ZI[zi][2][level].append(ci)
# 
# ZI_SORTED = sorted([(i, zi, first_level, level_dict) for zi, (i, first_level, level_dict) in ZI.items()])
# 
# print("i\tzi\tfirst_occurence\t" + "\t".join(levels))
# for (i, zi, first_level, level_dict) in ZI_SORTED:
#   print(f"{i}\t{zi}\t{first_level}", end="")
#   for level in levels:
#     # if not level_dict[level]: continue
#     print("\t" + "; ".join(level_dict[level]), end="")
#   print()
# 
