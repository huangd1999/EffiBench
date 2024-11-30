import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from tqdm import tqdm
import argparse

ListNode_text = """
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
"""
TreeNode_text = """
class TreeNode:
    def __init__(self, val=0, left=None, right=None, next=None):
        self.val = val
        self.left = left
        self.right = right
        self.next = next
"""

import_pkg = """
from typing import *
from bisect import *
from collections import *
from copy import *
from datetime import *
from heapq import *
from math import *
from re import *
from string import *
from random import *
from itertools import *
from functools import *
from operator import *

import string
import re
import datetime
import collections
import heapq
import bisect
import copy
import math
import random
import itertools
import functools
import operator
"""

def calculate_code_execution_efficiency(data, evaluation_code=False, path="./tmp/", max_execution_time=5):
    problem_idx = data["problem_idx"]
    completion_file, _ = add_string_to_py_file(data, evaluation_code=evaluation_code, path=path)
    script_path = '../scripts/run_code.sh'
    completion_dat_file = f'./{path}/{problem_idx}.dat'
    try:
        subprocess.run([script_path, completion_file, completion_dat_file, str(max_execution_time)], 
                       check=True, capture_output=True, text=True)
    finally:
        return data

def fetch_completion(dataset, model):
    with ThreadPoolExecutor() as executor:
        future_to_entry = {executor.submit(calculate_code_execution_efficiency, entry, False, path=model, max_execution_time=5): entry for entry in tqdm(dataset)}
        for future in tqdm(concurrent.futures.as_completed(future_to_entry)):
            entry = future_to_entry[future]
            try:
                updated_entry = future.result()
                idx = dataset.index(entry)
                dataset[idx] = updated_entry
            except Exception as e:
                pass
    return dataset

def add_string_to_py_file(data, evaluation_code=False, path="./tmp/"):
    if evaluation_code == False:
        test_case = data["test_case"]
    else:
        test_case = data["small_test_cases"]
    if "canonical_solution" in path:
        data["completion"] = data["canonical_solution"]
    problem_idx = data["problem_idx"]
    return_path, full_code = "", ""
    try:
        if "class Solution" in data["completion"]:
            if "```python" in data["completion"]:
                start_idx = data["completion"].find("```python")
                data["completion"] = data["completion"][start_idx+9:]
                if "```" in data["completion"]:
                    end_idx = data["completion"].find("```")
                    data["completion"] = data["completion"][:end_idx]
            full_code =import_pkg + "\n"+TreeNode_text + "\n"+ListNode_text + "\n" +  data["completion"] + "\nsolution=Solution()\n" + test_case
            with open(f"./{path}/{problem_idx}.py", "w") as f:
                f.write(full_code)
            return_path = f"./{path}/{problem_idx}.py"
    except Exception as e:
        # print(e)
        pass
    return return_path, full_code

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', '-m', type=str, default='gpt-3.5-turbo', help='Model to use for evaluation')
    args = parser.parse_args()
    models = ["canonical_solution",args.model]
    for model in models:
        if "/" in model:
            model = model.split("/")[1]
        if model == "canonical_solution":
            with open(f"../results/{models[-1].split('/')[-1]}.json", "r") as f:
                dataset = json.load(f)
        else:
            try:
                with open(f"../results/{model}.json", "r") as f:
                    dataset = json.load(f)
            except Exception as e:
                print(e)
                continue

        dat_path = f"../dat_results/{model}"
        os.makedirs(dat_path, exist_ok=True)
        fetch_completion(dataset, dat_path)