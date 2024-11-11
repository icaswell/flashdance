# Flashdance (单词)

Miao miao meo meowst Meowmst.

## Adding new flashcards

1. add a new set of flashcards in `vocab_separate`
2. generate flashcards by pointing at it:

```
python3 flashcards/make_flashcards.py --mode=iphone --level=stront2
```

3. This will report the missing things that need to be generated with AI. It will write the relevant commands to `missing/api_commands.sh`. You can now run this file to call the API:

```
bash missing/api_commands.sh
```

This will also output the four relevant files, e.g.:

```
output/examples.tsv__gemini-1.5-flash_c25__general_example_prompt_3examples.txt
output/single_defs_for_shared_zi_multici.tsv__gemini-1.5-flash_c80__multizi_prompt.txt
output/zi_defs.tsv__gemini-1.5-flash_c80__singlezi_prompt.txt
```


4. Run `python3 resources/example_sentences/parse_example_outputs.py`. Then see the errors it reports and fix them. Then run it again.

Optional:
  * by default, everything is considered as being at the highest level. If you want the level to be lower (this influences how many same-zi ci are shown) you can modify LEVELS in `make_flashcards.py`.

5. Run `python3 resources/definitions_and_pinyin/add_to_zi_singleword_defs.py` to add the singlezi defs. It may output lines that you need to fix.

6. Run ` python3  resources/definitions_and_pinyin/add_to_multici_singleword_defs.py  `. Sehe oben

7. Run ` python3 resources/pos/parse_pos_outputs.py --inglob=output/pos.txt__gemini-1.5-flash_c80__pos_prompt.txt --outfile=resources/pos/pos.tsv  `. As before.

8. Run `python3 resources/usage_notes/parse_usage_notes.py`

9. Run `python3 flashcards/make_flashcards.py` againnnnn

10. profit

