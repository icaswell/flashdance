# Flashdance (单词)

Miao miao meo meowst Meowmst.


## Workflow

1. make various text files in the `resources/` directory from online resources. Usually, if these are for feeding into `api_main.py/`, they will have 'input` in the name somewhere.
2. use `api_main.py` and a prompt from `prompts/' to make AI-generated files. These are put in the `output/` directory.
3. Parse the AI-generated outputs into new resources, putting them back in the `resources/` folder. Generally, for some particular directory in `resources/`, there will be a python script in that directory that parses the outputs into a well-behaved file.
4. Generate flashcards with `flashcards/make_flashcards.py`


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

This will also output the four relevant files.


4. Run `python3 resources/example_sentences/parse_example_outputs.py`. Then see the errors it reports and fix them. Then run it again.

Optional:
  * by default, everything is considered as being at the highest level. If you want the level to be lower (this influences how many same-zi ci are shown) you can modify LEVELS in `make_flashcards.py`.

5. Run `python3 resources/definitions_and_pinyin/add_to_zi_singleword_defs.py` to add the singlezi defs. It may output lines that you need to fix.

6. Run ` python3  resources/definitions_and_pinyin/add_to_multici_singleword_defs.py  `. Sehe oben

7. Run `python3 flashcards/make_flashcards.py` againnnnn

8. profit

