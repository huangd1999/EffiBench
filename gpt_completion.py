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
import time

enc = tiktoken.encoding_for_model("gpt-4")

with open("./dataset.json", "r") as f:
    dataset = json.load(f)

print(len(dataset))


# Setting API parameters
openai.api_key = 'API Key Here'

text = """
Please based on the task description write Solution to pass the provided test cases. 
You must follow the following rules:
First, the code should be in ```python\n[Code]\n``` block.
Second, You should not add the provided test cases into your ```\npython[Code]\n``` block.
Third, You are not need to write the test cases, we will provide the test cases for you.
Finally, You should make sure that the provided test cases can pass your solution.

Here is a example:
Example:
# Task description
```python
Given an array of integers, return indices of the two numbers such that they add up to a specific target.
You may assume that each input would have exactly one solution, and you may not use the same element twice.
Example:
Given nums = [2, 7, 11, 15], target = 9,
Because nums[0] + nums[1] = 2 + 7 = 9,
return [0, 1].
```

# Test cases
```python
solution = Solution()
assert solution.twoSum([2, 7, 11, 15], 9) == [[0, 1]
```

# Code
```python
from typing import *
import random

class Solution:
    def twoSum(self, nums, target):
        hashtable = dict()
        for i, num in enumerate(nums):
            if target - num in hashtable:
                return [hashtable[target - num], i]
            hashtable[nums[i]] = i
        return []
```
"""



# Function to fetch completion
def fetch_completion(data_entry, model):
    if "small_test_case" not in data_entry.keys():
        data_entry["completion"] = ""
        return data_entry
    test_case = data_entry["small_test_case"]

    test_case = test_case.split("\n")
    filter_test_cases = []
    for test in test_case:
        if len(enc.encode(test)) < 512:
            filter_test_cases.append(test)

    shortest_test_cases = sorted(filter_test_cases, key=len)[:4]

    input_test_cases = "\n".join(shortest_test_cases)
    try:
        completions = openai.ChatCompletion.create(
            model=model,
            stream=False,
            messages=[
                {"role": "system", "content": "You are a code developer."},
                {"role": "user", "content": text + "\n# Task description:\n```python\n" + data_entry["description"]+"\n```\n# Test case:\n```python\n"+input_test_cases+"\n```"},
            ],
            request_timeout=100,
        )
        data_entry["completion"] = completions.choices[0]["message"]["content"]
    except Exception as e:
        print(repr(e))
        data_entry["completion"] = ""
    return data_entry


model_list = ["gpt-3.5-turbo-0613"]
for model in model_list:
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_entry = {executor.submit(fetch_completion, copy.deepcopy(entry), model): entry for entry in tqdm(dataset)}
        for future in tqdm(concurrent.futures.as_completed(future_to_entry)):
            entry = future_to_entry[future]
            try:
                updated_entry = future.result()
                idx = dataset.index(entry)
                dataset[idx] = updated_entry
            except Exception as e:
                print(repr(e))


    with open(f"./leetcode_{model}.json", "w") as f:
        json.dump(dataset, f, indent=4)