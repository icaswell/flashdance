# Flashdance (单词)

Miao miao meo meowst Meowmst.


## Workflow

1. make various text files in the `resources/` directory from online resources. Usually, if these are for feeding into `api_main.py/`, they will have 'input` in the name somewhere.
2. use `api_main.py` and a prompt from `prompts/' to make AI-generated files. These are put in the `output/` directory.
3. Parse the AI-generated outputs into new resources, putting them back in the `resources/` folder. Generally, for some particular irectory in `resources/`, there will be a python script in that directory that parses the outputs into a well-behaved file.
4. Generate flashcards with `flashcards/make_flashcards.py`

## TODO

 - get singleword defs for missing multici (from weeb or stront?_ )
 - get full pinyin list from CEDict (after converting from their format to normal pinyin format)
   - add pinyin from slang and strontium to it!!
 - fix the choosing of words that use the same zi by:
   - define an order of files in resources/wordlists_single
   - read those in order and map s.t. MAP[zi][level] gives everything at same level and b4
  - fix the "CL" annotations from CEDict
    - I: "CL:個|个[ge4],條|条[tiao2]"
    - O: "CL:个[gè],条[tiáo]"
  - Hopefully figure out how to do both and italics because it would be really nice if pinyin were an italics?
