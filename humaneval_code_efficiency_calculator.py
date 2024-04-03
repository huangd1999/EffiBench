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

def add_profile_decorator_to_python_file(file_path):
    """给Python文件中的函数自动添加@profile装饰器。"""
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        with open(file_path, 'w') as file:
            inside_class = False
            class_indent = 0
            for line in lines:
                stripped_line = line.lstrip()
                if stripped_line.startswith("class Solution"):
                    inside_class = True
                    class_indent = len(line) - len(stripped_line)
                    file.write(line)
                    continue
                if inside_class:
                    if stripped_line and not line[class_indent].isspace():
                        inside_class = False
                    elif stripped_line.startswith("def "):
                        file.write(' ' * class_indent + '    @profile\n')
                file.write(line)
    except Exception as e:
        # print(f"Error during the file processing: {e}")
        pass

def calculate_line_efficiency(completion_file):
    try:
        path, filename = os.path.split(completion_file)
        tmp_py_script_filename = f"{filename.split('.')[0]}_tmp.py"
        tmp_py_script = os.path.join(path, tmp_py_script_filename)
        tmp_lprof_filename = f"{tmp_py_script_filename}.lprof"  # 期望的lprof文件名
        
        # 复制原始脚本到临时文件，并添加@profile装饰器
        subprocess.run(['cp', completion_file, tmp_py_script],check=True, capture_output=True, text=True)
        add_profile_decorator_to_python_file(tmp_py_script)
        
        # 设置最大执行时间，单位为秒
        MAX_EXECUTION_TIME = "5"

        subprocess.run(['timeout', MAX_EXECUTION_TIME, 'kernprof', '-l', tmp_py_script_filename], cwd=path, capture_output=True, text=True, check=True)
        # 生成性能报告
        overhead_dir = os.path.join(path, "../overhead")
        os.makedirs(overhead_dir, exist_ok=True)
        report_file = os.path.join(overhead_dir, tmp_py_script_filename.replace('.py', '.txt'))
        with open(report_file, 'w') as f:
            subprocess.run(['python', '-m', 'line_profiler', tmp_lprof_filename], cwd=path, stdout=f)
        with open(report_file, 'r') as f:
            report_content = f.read()
            # print(report_content)

    except subprocess.CalledProcessError as e:
        # print(f"Error during the execution: {e}")
        report_content = f"Error during the execution: {e}"

    # # 清理临时文件
    if os.path.exists(tmp_py_script):
        os.remove(tmp_py_script)
    if os.path.exists(f"{tmp_py_script}.lprof"):
        os.remove(f"{tmp_py_script}.lprof")

    return report_content



def add_string_to_py_file(data,evaluation_code=False, path="./tmp/",lg="python"):
    lg_files = {
        "python":"py",
        "cpp":"cpp",
        "java":"java",
        "js":"js",
        "go":"go",
    }
    file_end = lg_files[lg]
    if path == "canonical_solution":
        data["completion"] = data["canonical_solution"]
    code = data["completion"]
    test_case = data["test"]
    task_idx = data["task_id"] # CPP/0
    split_task_idx = task_idx.split("/")[1]
    try:
        if f"```{lg}" in data["completion"]:
            start_idx = data["completion"].find(f"```{lg}")
            data["completion"] = data["completion"][start_idx+len(f"```{lg}"):]
            if "```" in data["completion"]:
                end_idx = data["completion"].find("```")
                data["completion"] = data["completion"][:end_idx]
        full_code = data["completion"] + test_case
        if lg =="java":
            with open(f"./{path}/Main.java", "w") as f:
                f.write(full_code)
        else:
            with open(f"./{path}/{split_task_idx}.{file_end}", "w") as f:
                f.write(full_code)
        
    except Exception as e:
        pass

def calculate_code_execution_efficiency(data,evaluation_code=False,path="./tmp/",lg="python"):
    lg_files = {
        "python":"py",
        "cpp":"cpp",
        "java":"java",
        "js":"js",
        "go":"go",
    }
    file_end = lg_files[lg]
    task_idx = data["task_id"]
    problem_idx = task_idx.split("/")[1]
    add_string_to_py_file(data,evaluation_code=evaluation_code, path=path,lg=lg)
    script_path = './run_code.sh'
    completion_file = f'./{path}/{problem_idx}.{file_end}'
    completion_dat_file = f'./{path}/{problem_idx}.dat'
    # line_profiler_results = calculate_line_efficiency(completion_file)
    # print(script_path, completion_file, completion_dat_file)
    try:
        if lg == "cpp":
            subprocess.run(['g++', completion_file, '-o', f'./{path}/{problem_idx}'])
            result = subprocess.run([script_path, f'./{path}/{problem_idx}', completion_dat_file], 
                            check=True, capture_output=True, text=True)

        elif lg == "java":
            completion_file = f'./{path}/Main.java'
            subprocess.run(['javac', completion_file], check=True)
            result = subprocess.run(['javac', "Main.java", completion_dat_file], 
                                    check=True, capture_output=True, text=True)
        elif lg == "js":
            result = subprocess.run([script_path, completion_file, completion_dat_file], 
                                    check=True, capture_output=True, text=True)
        elif lg == "go":
            subprocess.run(['go', 'build', '-o', f'./{path}/{problem_idx}', completion_file], check=True)
            result = subprocess.run([script_path, f'./{path}/{problem_idx}', completion_dat_file], 
                                    check=True, capture_output=True, text=True)

        elif lg == "python":
            result = subprocess.run([script_path, completion_file, completion_dat_file], 
                            check=True, capture_output=True, text=True)


        canonical_solution_memory_usage = calculate_memory_usage(completion_dat_file)
        canonical_solution_execution_time = calculate_runtime(completion_dat_file)
        canonical_solution_max_memory_usage = report_max_memory_usage(completion_dat_file)

        executable = True

        overhead = f"""
The total memory usage during the code execution is: {canonical_solution_memory_usage} MB*s.
The total execution time is: {canonical_solution_execution_time} s.
The maximum memory peak requirement is: {canonical_solution_max_memory_usage} MB.
"""
    except Exception as e:
        print(e)
        overhead = f"""
The code execution failed.
"""
        canonical_solution_memory_usage = 0
        canonical_solution_execution_time = 0
        canonical_solution_max_memory_usage = 0
        executable = False

    return overhead, canonical_solution_memory_usage, canonical_solution_execution_time, canonical_solution_max_memory_usage, executable
    
    
def fetch_completion(dataset,model,lg):
    with ThreadPoolExecutor(max_workers=1) as executor:
            future_to_entry = {executor.submit(calculate_code_execution_efficiency, copy.deepcopy(entry),False, path=model,lg=lg): entry for entry in tqdm(dataset)}
            for future in tqdm(concurrent.futures.as_completed(future_to_entry)):
                entry = future_to_entry[future]
                try:
                    updated_entry = future.result()
                    idx = dataset.index(entry)
                    dataset[idx] = updated_entry
                except Exception as e:
                    # pass
                    print(e)
    return dataset

if __name__ == "__main__":
    models = ["canonical_solution","gpt-3.5-turbo-0301","gpt-3.5-turbo-0613","gpt-3.5-turbo-1106","gpt-4-turbo-preview","gpt-4"]
    language = ["cpp", "python"] # "go","java","js",
    for model in models:
        for lg in language:
            if model == "canonical_solution": # for canonical solution, we use the canonical_slo
                with open(f"./results/humaneval_gpt-3.5-turbo-0301_{lg}.json", "r") as f:
                    dataset = json.load(f)
            else:
                with open(f"./results/humaneval_{model}_{lg}.json", "r") as f:
                    dataset = json.load(f)
            if not os.path.exists(f'./{model}_{lg}'):
                os.makedirs(f'./{model}_{lg}')
            files = glob.glob(f'./{model}_{lg}/*')
            for f in files:
                os.remove(f)
            fetch_completion(dataset,f"{model}_{lg}",lg)
