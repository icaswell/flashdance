python3 api_main.py --input=missing/examples.tsv --system_prompt=prompts/cql_example_prompt3_3examples.txt
python3 api_main.py --input=missing/examples.tsv --system_prompt=prompts/general_example_prompt_3examples.txt
python3 api_main.py --input=missing/single_defs_for_shared_zi_multici.tsv --system_prompt=prompts/multizi_prompt.txt
python3 api_main.py --input=missing/zi_defs.tsv --system_prompt=prompts/singlezi_prompt.txt
tail -n 4 output/LOG.tsv | cut -f 1
