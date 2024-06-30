"""
Example usage:

python3 api_main.py \
--system_prompt prompts/example_sentences_prompt1.txt \
--input test_input.tsv \
--output test_output.tsv


see prompts/ dir for available prompts.
"""

from openai import OpenAI
import random
import csv
import argparse
import sys, os
from glob import glob
import datetime

def read_tsv(file_path):
    data = []
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            data.append(row)
    return data

def write_tsv(file_path, data):
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        for row in data:
            writer.writerow(row)


def generate(client,  model_name: str, system_prompt: str, input_data: str, temp: float, max_tokens: int = 4096) -> str:

  print(f'Generating with model {model_name}')
  print(f'Using sampling temperature {temp}')

  messages = [{ 
        "role": "user",
        "content": input_data
      }]
  if system_prompt:
    messages = [{ 
        "role": "system",
        "content": system_prompt,
      }] + messages
  completion = client.chat.completions.create(
  model=model_name,
  messages=messages,
    temperature=temp,
    max_tokens=max_tokens,
    top_p=1
  )

  output = completion.choices[0].message.content

  return output

  
def main():
  
  parser = argparse.ArgumentParser(description='Process input file and save the result to an output file.')
  parser.add_argument('--input_glob', default="fics/readytogo_prompts/dumpsteroflove/ep_*.txt", dest='input_glob', help='Input file name')
  parser.add_argument('--temp', type=float, default=0.0, help='Temperature for sampling')
  parser.add_argument('--model_name', default='gpt-3.5-turbo-1106', help='Input file name')
  args = parser.parse_args()
  
  client = OpenAI()

  outdir = "/".join(args.input_glob.split("/")[0:-1])  # Hack alert!!!
  os.system(f"mkdir -p {outdir}")

  system_prompt = ""
  for fname in glob(args.input_glob):
    outfname = fname.replace("readytogo_prompts", "output")
    with open(fname, "r") as f:
      prompt = "".join(f.readlines())
    output = generate(client, model_name=args.model_name, system_prompt=system_prompt, input_data=prompt, temp=args.temp)
    # output = generate(client, model_name=args.model_name, system_prompt=system_prompt, input_data=prompt, temp=args.temp)
    print("="*80)
    print(output)
    with open(outfname, "w") as f:
      f.write(output)


if __name__ == '__main__':
  main()
