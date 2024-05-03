import json
import openai
import argparse
import os
import json
from tqdm import tqdm
import copy
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import time

# Setting API parameters
openai.api_key = 'API Key'

with open("../prompts/prompt.txt", "r") as f:
    text = f.read()

# Function to fetch completion
def fetch_completion(data_entry, model):
    global text
    test_case = data_entry["small_test_cases"]
    while True:
        try:
            completions = openai.ChatCompletion.create(
                model=model,
                stream=False,
                messages=[
                    {"role": "system", "content": "You are a code developer."},
                    {
                        "role": "user",
                        "content": (
                            f"{text}\n"
                            f"# Task description:\n```python\n{data_entry['markdown_description']}\n```\n"
                            f"# Test case:\n```python\n{test_case}\n```"
                        )
                    },
                ],
                request_timeout=100,
            )
            data_entry["completion"] = completions.choices[0]["message"]["content"]
        except Exception as e:
            print(repr(e))
            time.sleep(10)
            data_entry["completion"] = ""
        if data_entry["completion"] != "":
            break
    return data_entry

if __name__ == "__main__":
    model = "gpt-3.5-turbo-0301"
    with open("./data/dataset.json", "r") as f:
        dataset = json.load(f)

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_entry = {
            executor.submit(fetch_completion, copy.deepcopy(entry), model): entry
            for entry in tqdm(dataset)
        }
        for future in tqdm(concurrent.futures.as_completed(future_to_entry)):
            entry = future_to_entry[future]
            try:
                updated_entry = future.result()
                idx = dataset.index(entry)
                dataset[idx] = updated_entry
            except Exception as e:
                print(repr(e))

    with open(f"./results/{model}.json", "w") as f:
        json.dump(dataset, f, indent=4)