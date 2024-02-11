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
import sys
import datetime

LOG_FILE = "output/LOG.tsv"

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

  completion = client.chat.completions.create(
  model=model_name,
  messages=[
      {
        "role": "system",
        "content": system_prompt,
      },
      {
        "role": "user",
        "content": input_data
      }
    ],
    temperature=temp,
    max_tokens=max_tokens,
    top_p=1
  )

  output = completion.choices[0].message.content

  return output

  
def split_to_chunks(entries_list, chunk_size:int):
  chunks = [entries_list[i:i+chunk_size] for i in range(0, len(entries_list), chunk_size)]
  return chunks

def main():
  
  parser = argparse.ArgumentParser(description='Process input file and save the result to an output file.')
  parser.add_argument('--system_prompt', required=True, help='System prompt file name')
  parser.add_argument('--input', dest='input_file', required=True, help='Input file name')
  parser.add_argument('--temp', type=float, default=0.0, help='Temperature for sampling')
  parser.add_argument('--model_name', default='gpt-3.5-turbo-1106', help='Input file name')
  parser.add_argument('--chunk_size', type=int, default=5, help='How many words to batch together for one generation.')
  parser.add_argument('--start', type=int, default=0, help='the first line to read from the input (inclusive)')
  parser.add_argument('--end', type=int, default=None, help='the last line to read from the input (inclusive)')
  args = parser.parse_args()
  
  client = OpenAI()

  with open(args.system_prompt, 'r', encoding='utf-8') as infile:
    system_prompt = infile.read()
  print(f'System prompt:\n{system_prompt}')

  input_data_rows = []
  with open(args.input_file, 'r', encoding='utf-8') as infile:
    for i, row in enumerate(infile):
      if i < args.start: continue
      if args.end and i > args.end: break
      input_data_rows.append(row)

  chunked_input = split_to_chunks(input_data_rows, chunk_size=args.chunk_size)

  output_fname = f"output/{args.input_file.split('/')[-1]}"
  prompt_name = args.system_prompt.split("/")[-1].replace(".txt", "")
  bounds_name = f"__lines{args.start}-{args.end if args.end else 'end'}" if (args.start or args.end) else ""
  output_fname = output_fname + f"__{args.model_name}_t{args.temp}_c{args.chunk_size}__{prompt_name}{bounds_name}.txt"
  output_file = open(output_fname, 'a', encoding='utf-8')

  for i, inp_chunk in enumerate(chunked_input):
    # Concatenate the rows in the chunk into a single string
    inp_chunk_str = ''.join(inp_chunk)

    print(f'chunk {i}: \n{inp_chunk_str}')

    output = generate(client, model_name=args.model_name, system_prompt=system_prompt, input_data=inp_chunk_str, temp=args.temp)

    print(output)

    output_file.write(output + '\n')
    output_file.flush()

  output_file.close()
  print("\n\n#================================================#")
  print(f"Wrote to file {output_fname}")

  with open(LOG_FILE, "a") as f:
    f.write(output_fname + "\t")
    f.write(" ".join(sys.argv) + "\t")
    f.write(datetime.datetime.now().strftime("%Y/%m/%d %H:%M") + "\n")


if __name__ == '__main__':
  main()
