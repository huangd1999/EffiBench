import json
import openai
import argparse
import os
import json
from tqdm import tqdm
import copy
import openai
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import tiktoken
from datasets import load_dataset
import time

enc = tiktoken.encoding_for_model("gpt-4")


# Setting API parameters
openai.api_base = "https://api.aiohub.org/v1"
openai.api_key = 'e8d20ad67ba241228469ae8c37877f41'

text = """
Please based on the task description complete the function.
"""


# Function to fetch completion
def fetch_completion(data_entry, model):
    try:
        completions = openai.ChatCompletion.create(
            model=model,
            stream=False,
            messages=[
                {"role": "system", "content": "You are a code developer."},
                {"role": "user", "content": text + "\n# Task description:\n```python\n" + data_entry["prompt"]+"\n```"},
            ],
            request_timeout=100,
        )
        data_entry["completion"] = completions.choices[0]["message"]["content"]
    except Exception as e:
        print(repr(e))
        data_entry["completion"] = ""
        time.sleep(5)
    return data_entry


model_list = ["gpt-3.5-turbo-1106","gpt-4-turbo-preview"]
language = ["cpp","go","java","js","python"]
for model in model_list:
    for lg in language:
        dataset = load_dataset("THUDM/humaneval-x", lg, split="test")
        dataset = [entry for entry in dataset]
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_entry = {executor.submit(fetch_completion, copy.deepcopy(entry), model): entry for entry in tqdm(dataset)}
            for future in tqdm(concurrent.futures.as_completed(future_to_entry)):
                entry = future_to_entry[future]
                try:
                    updated_entry = future.result()
                    idx = dataset.index(entry)
                    dataset[idx] = updated_entry
                except Exception as e:
                    print(repr(e))


        with open(f"./results/humaneval_{model}_{lg}.json", "w") as f:
            json.dump(dataset, f, indent=4)