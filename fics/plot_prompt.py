"""

plot: 4-6 episodes
episode: 4-6 paragraphs
paragraph: generated, uses ci
"""

# Write the plot to an Untamed fanfic. The fic will have four episodes. You will write the episode summary to each one. For example:

import csv
import regex as re
import os
import random
from collections import defaultdict
import argparse
from typing import List, Dict

LEVEL = "hsk5"
FIC_ID = "dumpsteroflove"
fictype="MZDS/Untamed fanfic"
# os.system(f"mkdir fics/{FIC_ID}")

TARGET_CI = []
with open(f"resources/vocab_separate/{LEVEL}.tsv", "r") as f:
  for line in f:
    ci, pinyin, deff = line.strip().split("\t")
    # deff = re.sub("(^/|/$)", "", deff)
    # deff = deff.replace("/", "; ")
    TARGET_CI.append((ci, pinyin, deff))


with open(f"fics/{FIC_ID}/plot.txt", "r") as f:
  plot_str = "".join(f.readlines())


def parse_plot(plot):
  overall = re.findall("Fanfic title: .*\n*Overall summary: [^\n]*\n", plot)
  assert len(overall) == 1
  episodes = re.findall("\nEpisode \d: [^\n]*\n", plot + "\n")
  episodes = [ep.strip() for ep in episodes]
  assert len(episodes) >=4
  return {
      "overall": overall[0].strip(),
      "episodes": episodes,
      }

plot = parse_plot(plot_str)


def get_ci_prompt(k):
  cis = random.choices(TARGET_CI, k=k)
  return "; ".join([ci for ci, _, _ in cis])


os.system(f"mkdir -p fics/readytogo_prompts/{FIC_ID}")
# First, the freeform prompts
for i, ep_i in enumerate(plot['episodes']):
  prompt = f"""Here is the plot of a {fictype}:

{plot['overall']}

There are {len(plot['episodes'])} episodes in this {fictype}. Here is the plot summary of episode #{i+1}:

{ep_i}

You are now going to write this episode. Write at least five paragraphs telling the story described in the summary above. Write in Chinese. 请使用简体字。"""

  with open(f"fics/readytogo_prompts/{FIC_ID}/ep_{i+1}.txt", "w") as f:
    f.write(prompt)


# When writing this episide, make sure to use at least 5 of the following 10 words: {get_ci_prompt(k=10)}



# short_version = """
# 第四集：蓝忘机出发收集四块阴棉花糖。魏无羡偷偷跟着他。他们与一个名叫宋岚的邪恶负鼠修士发生了激烈的战斗，险胜。他们夺得了一块阴棉花糖。
# 
# 清晨的阳光透过树叶洒下，将青青的竹林染上了一层金色。蓝忘机站在庭院中，一袭白衣在微风中飘动。他的眼中透着坚定，手中握着一张地图，上面标注着四块阴棉花糖的位置。
# 
# “为了解开这片土地上的谜团，我必须收集到所有的阴棉花糖。”蓝忘机轻声自语道。
# 
# 就在此时，一道身影悄然出现在他身后。魏无羡迅速躲在一根竹子后面，眼中闪过一丝好奇。他一直对蓝忘机心存疑虑，想要亲眼见证他的行动。
# 
# 蓝忘机没有察觉到魏无羡的存在，他径直向着第一个阴棉花糖的位置走去。然而，当他抵达目的地时，一道身影突然出现在他面前。那是一个身穿黑色长袍的男子，手持一柄长剑，目光冷漠而锐利。"""
# 
# print( f"""
# Here is the plot of an episode of a {fictype}:
# 
# {plot['episodes'][3]}
# 
# Here is the text of a short version of this episode:
# 
# {short_version}
# 
# Rewrite this short version to add more detail and make it longer. You should make it about twice as long. Feel free to add more details add more elements of events to the plot. Write in Chinese.
#       """)
