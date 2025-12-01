import regex as re
import csv

input_fname = "resources/chengyu/combined_sources_hanzi_only_twoplusreferenceonline.txt"
e2e_output_fname = "output_e2e/chengyu.2p.gemini2.5thinking.csv"

with open(input_fname, "r") as f:
  to_cover = [line.strip() for line in f]

ci_to_csv_lines = {}
with open(e2e_output_fname, "r") as f:
  csv_reader = csv.reader(f, delimiter=';', quotechar='"')
  for row in csv_reader:
    if not row: continue
    ci_to_csv_lines[row[0]] = row

missing = set(to_cover) - ci_to_csv_lines.keys()
extra = ci_to_csv_lines.keys() - set(to_cover) 
shared = ci_to_csv_lines.keys() & set(to_cover) 

print(f"missing {len(missing)}: {missing}")
print(f"extra {len(extra)}: {extra}")
print(f"shared {len(shared)}: {shared}")
print('-'*80)


# "画地成图";"huà dì chéng tú";"To make detailed but impractical plans; to have elaborate but unrealistic designs by sketching directly on the ground.";"Chengyu Story";"This idiom literally translates to 'drawing on the ground to make a map.' It evokes the image of quickly sketching plans or maps directly onto the earth, suggesting a lack of proper tools, careful thought, or detailed consideration. While it can sometimes refer neutrally to sketching out ideas quickly, it more often implies that the plans are superficial, impractical, or unrealistic for the actual situation, similar to building castles in the air.";"画 (draw)";"Other words using this character: 画家 (huàjiā - painter); 绘画 (huìhuà - painting); 动画 (dònghuà - animation); 图画 (túhuà - picture); 画画 (huàhuà - to draw); 计划 (jìhuà - plan); 漫画 (mànhuà - manga/comics)";"地 (ground)";"Other words using this character: 地图 (dìtú - map); 地球 (dìqiú - Earth); 地点 (dìdiǎn - location); 地板 (dìbǎn - floor); 当地 (dāngdì - local); 地方 (dìfang - place); 地铁 (dìtiě - subway)";"成 (become)";"Other words using this character: 成功 (chénggōng - success); 成为 (chéngwéi - become); 完成 (wánchéng - complete); 成语 (chéngyǔ - idiom); 成熟 (chéngshú - mature); 成绩 (chéngjì - result/score); 组成 (zǔchéng - compose)";"图 (map/plan)";"Other words using this character: 图书馆 (túshūguǎn - library); 地图 (dìtú - map); 图片 (túpiàn - picture); 试图 (shìtú - attempt); 意图 (yìtú - intention); 图案 (tú'àn - pattern); 蓝图 (lántú - blueprint)";"他只是画地成图，并没有真正可行的计划。";"【Tā zhǐ shì huà dì chéng tú, bìng méiyǒu zhēnzhèng kěxíng de jìhuà.】 &lt;NEWLINE> He is just drawing maps on the ground (making impractical plans) and doesn't have a truly feasible plan.";"别在那儿画地成图了，我们得赶紧行动起来解决问题。";"【Bié zài nàr huà dì chéng tú le, wǒmen děi gǎnjǐn xíngdòng qǐlái jiějué wèntí.】 &lt;NEWLINE> Stop just drawing maps on the ground (making idle plans) there; we need to take action quickly to solve the problem.";"他们的战略部署看似宏大，实则不过是画地成图，缺乏细节支撑和实际操作性。";"【Tāmen de zhànlüè bùshǔ kànsì hóngdà, shízé bùguò shì huà dì chéng tú, quēfá xìjié zhīchēng hé shíjì cāozuò xìng.】 &lt;NEWLINE> Their strategic deployment looks grand, but in reality, it's just drawing maps on the ground (impractical planning), lacking detailed support and practical operability.";"online source";"Gemini 2.5 Chengyu"


HANRE = re.compile("\p{Han}")
def verify(row):
  ci = row[0]
  assert HANRE.search(ci)
  assert not HANRE.search(row[1])  # pinyin
  assert not HANRE.search(row[2])  # short def
  assert row[3] == "Chengyu Story"
  assert len(row[4]) > 200 # main definition
  for i, zi in enumerate(ci):
    if not re.match(zi + " \(.*\)", row[5 + 2*i]):
      raise ValueError(f"[{ci}] Expected: '{zi} (shortdef)'" + "\n" + f"[{ci}] Actual: '{row[5+i]}'")
      # DELIM = "\n\t"
      # print(f"[{ci}] Line:   {DELIM.join([str(j) + ':' + field for j, field in enumerate(row)])}")
    if zi not in row[6 + 2*i]:
      raise ValueErrorprint(f"[{ci}] Expected: '{zi}' in related characters line" + "\n" + f"[{ci}] Actual:   '{row[6+i]}'")
      # DELIM = "\n\t"
      # print(f"[{ci}] Line:   {DELIM.join([str(j) + ':' + field for j, field in enumerate(row)])}")

  example1_i = 7 + 2*i
  for ex_i in range(3):  # there are three examples
    ex =      row[example1_i + 2*ex_i].replace("，", "")  # sometimes longer chengyu are broken by commas; remove them
    ex_trpy = row[example1_i + 2*ex_i + 1]  # translation, pinyin
    assert HANRE.search(ex)
    if ci not in ex:
      raise ValueError(f"[{ci}] Expected: '{ci}' in example" + "\n" + f"[{ci}] Actual:   '{ex}'")
      
    if HANRE.search(ex_trpy):
      raise ValueError(f"[{ci}] Expected: No Chinese characters in pinyin/translation field." + "\n" + f"[{ci}] Actual:   {ex_trpy}")

    assert "【" in ex_trpy
  assert row[example1_i + 2*ex_i + 2] == "online source"
  assert row[example1_i + 2*ex_i + 3] == "Gemini 2.5 Chengyu"



  



for ci in shared:
  verify(ci_to_csv_lines[ci])
  try:
    verify(ci_to_csv_lines[ci])
    # print(f"succeeded: {ci}")
  except Exception as e:
    print(f"failed: {ci}: {e}")

# fname_out = f"flashcards/{args.mode}/{levels_name}.flashcards.{args.mode}.{part_i + 1}-of-{BREAK_INTO_N_CHUNKS}.csv"
# with open(fname_out, 'w') as csvfile:
#   csvwriter = csv.writer(csvfile, delimiter =';', quoting=csv.QUOTE_ALL)
#   csvwriter.writerows(out_lines_i)
# print(f"Wrote {fname_out}")

