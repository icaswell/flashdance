python3 api_main_gembini.py --chunk_size=40 --input=missing/usage_notes.tsv --system_prompt=prompts/usage_notes_prompt.txt --model=gemini-1.5-pro  --start=2120
# python3 api_main_gembini.py --chunk_size=40 --input=missing/examples.tsv --system_prompt=prompts/general_example_prompt_3examples.txt
# python3 api_main_gembini.py --chunk_size=100 --input=missing/single_defs_for_shared_zi_multici.tsv --system_prompt=prompts/multizi_prompt.txt
python3 api_main_gembini.py --chunk_size=100 --input=missing/pos.tsv --system_prompt=prompts/pos_prompt.txt
# python3 api_main_gembini.py --chunk_size=100 --input=missing/zi_defs.tsv --system_prompt=prompts/singlezi_prompt.txt
tail -n 5 output/LOG.tsv | cut -f 1

