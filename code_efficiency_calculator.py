import json
import os
import glob
import copy
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import subprocess
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

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

def calculate_memory_usage(dat_file_path):
    with open(dat_file_path, 'r') as file:
        prev_time = 0
        prev_mem_mb = 0
        mem_time_mb_s = 0
        next(file)
        for line in file:
            if not line.startswith('MEM'):
                continue  # Skip any line that does not start with 'MEM'
            parts = line.split()
            mem_in_mb = float(parts[1])
            timestamp = float(parts[2])
            if prev_time > 0:
                time_interval_s = timestamp - prev_time
                mem_time_mb_s += (prev_mem_mb + mem_in_mb) / 2 * time_interval_s
            prev_time = timestamp
            prev_mem_mb = mem_in_mb
        return mem_time_mb_s


def calculate_runtime(dat_file_path):
    with open(dat_file_path, 'r') as file:
        start_time = float("inf")
        end_time = float("-inf")
        next(file)
        for line in file:
            if not line.startswith('MEM'):
                continue  # Skip any line that does not start with 'MEM'
            parts = line.split()
            timestamp = float(parts[2])
            start_time = min(start_time, timestamp)
            end_time = max(end_time, timestamp)
        return max(end_time - start_time,0)

def report_max_memory_usage(dat_file_path):
    max_memory_usage = 0
    with open(dat_file_path, 'r') as file:
        prev_time = 0
        prev_mem_mb = 0
        mem_time_mb_s = 0
        next(file)
        for line in file:
            if not line.startswith('MEM'):
                continue  # Skip any line that does not start with 'MEM'
            parts = line.split()
            mem_in_mb = float(parts[1])
            max_memory_usage = max(max_memory_usage, mem_in_mb)
        return max_memory_usage

def add_string_to_py_file(data,evaluation_code=False, path="./tmp/"):
    if path == "canonical_solution":
        data["completion"] = data["canonical_solution"]
    code = data["completion"]
    if evaluation_code==False:
        test_case = data["full_test_case"]
    else: 
        test_case = data["small_test_cases"]
    problem_idx = data["problem_idx"]
    try:
        if "class Solution" in data["completion"]:
            if "```python" in data["completion"]:
                start_idx = data["completion"].find("```python")
                data["completion"] = data["completion"][start_idx+9:]
                if "```" in data["completion"]:
                    end_idx = data["completion"].find("```")
                    data["completion"] = data["completion"][:end_idx]
            test_case = test_case.split("\n")[:100]
            test_case = "\n".join(test_case)
            # import_pkg
            full_code = "from typing import *\nimport random\nimport string\n" + "\n"+TreeNode_text + "\n"+ListNode_text + "\n" + data["completion"] + "\nsolution=Solution()\n" + test_case
            with open(f"./{path}/{problem_idx}.py", "w") as f:
                f.write(full_code)
    except Exception as e:
        # print(repr(e))
        pass

def calculate_code_execution_efficiency(data,evaluation_code=False,path="./tmp/"):
    problem_idx = data["problem_idx"]
    add_string_to_py_file(data,evaluation_code=evaluation_code, path=path)
    script_path = './run_code.sh'
    completion_file = f'./{path}/{problem_idx}.py'
    completion_dat_file = f'./{path}/{problem_idx}.dat'
    try:
        result = subprocess.run([script_path, completion_file, completion_dat_file], 
                            check=True, capture_output=True, text=True)
        # # 打印输出结果
        # print("STDOUT:", result.stdout)
        # print("STDERR:", result.stderr)

        canonical_solution_memory_usage = calculate_memory_usage(completion_dat_file)
        canonical_solution_execution_time = calculate_runtime(completion_dat_file)
        canonical_solution_max_memory_usage = report_max_memory_usage(completion_dat_file)
        # print("Memory usage: ", canonical_solution_memory_usage, "MB*s")
        # print("Execution time: ", canonical_solution_execution_time, "s")
        # print("Max memory peak requirement: ", canonical_solution_max_memory_usage, "MB")
        executable = True
        overhead = f"""
The total memory usage during the code execution is: {canonical_solution_memory_usage} MB*s.
The total execution time is: {canonical_solution_execution_time} s.
The maximum memory peak requirement is: {canonical_solution_max_memory_usage} MB.
"""
    except Exception as e:
        # print(repr(e))
        overhead = f"""
The code execution failed.
"""
        canonical_solution_memory_usage = 0
        canonical_solution_execution_time = 0
        canonical_solution_max_memory_usage = 0
        executable = False
    return overhead, canonical_solution_memory_usage, canonical_solution_execution_time, canonical_solution_max_memory_usage, executable
    
    
def fetch_completion(dataset,model):
    with ThreadPoolExecutor() as executor:
            future_to_entry = {executor.submit(calculate_code_execution_efficiency, copy.deepcopy(entry),False, path=model): entry for entry in tqdm(dataset)}
            for future in tqdm(concurrent.futures.as_completed(future_to_entry)):
                entry = future_to_entry[future]
                try:
                    updated_entry = future.result()
                    idx = dataset.index(entry)
                    dataset[idx] = updated_entry
                except Exception as e:
                    # print(repr(e))
                    pass
    return dataset

if __name__ == "__main__":
    execution_times = {}
    import time
    models = ["incoder-1B","incoder-6B","starcoder","codegen-2B-mono","codegen-6B-mono","Magicoder-S-CL-7B","Magicoder-S-DS-6.7B","WizardCoder-15B-V1.0","instructcodet5p-16b","Mistral-7B-Instruct-v0.2","Mistral-7B-v0.1", "CodeLlama-7b-Python-hf", "CodeLlama-13b-Python-hf","gpt-3.5-turbo-0301","gpt-3.5-turbo-0613","gpt-3.5-turbo-1106","gpt-4-1106-preview","gpt-4", "palm-2-chat-bison","claude-instant-1","gemini-pro"]
    for model in models:
        start = time.time()
        with open(f"./code_generation_results/leetcode_{model}.json", "r") as f:
            dataset = json.load(f)
        import os
        with open(f"./dataset_full_test_case.json", "r") as f:
            leetcode = json.load(f)

        if not os.path.exists(f'./{model}'):
            os.makedirs(f'./{model}')
        files = glob.glob(f'./{model}/*')
        for f in files:
            os.remove(f)
        fetch_completion(dataset,model)
        execution_times[model] = time.time() - start
    print(execution_times)

