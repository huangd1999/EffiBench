import json
import re
import sys
import multiprocessing
from typing import List, Dict, Any, Optional, Tuple, Union, Callable
import time
import random
import json
from typing import Optional, Callable, Dict
import ast
import doctest
import io
from concurrent.futures import ThreadPoolExecutor, as_completed
import inspect
import numpy as np
import sys
import contextlib
import faulthandler
import io
import os
import multiprocessing
import platform
import signal
from tqdm import tqdm
import threading
import tempfile

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

def extract_function_name(code_snippet):
    """
    Extract the function name from a Python function definition.

    :param code_snippet: The code snippet containing the function definition
    :return: The extracted function name
    """
    # Find the start of the function definition
    def_start = code_snippet.find("def ")
    if def_start == -1:
        return "No function definition found."

    # Find the start of the function parameters
    params_start = code_snippet.find("(", def_start)

    # Extract the function name
    function_name = code_snippet[def_start + 4:params_start].strip()
    return function_name

def comment_out_print_statements(code):

    commented_code = re.sub(r'print\s*\([^)]*\)', '# \g<0>', code)
    return commented_code


def replace_test_case_function_name(test_cases, new_function_name):
    """
    Replace the function name in a series of test cases with a new function name.

    :param test_cases: String containing multiple test cases
    :param new_function_name: The new function name to replace with in test cases
    :return: String with the modified test cases
    """
    # Splitting the test cases into lines for easier processing
    lines = test_cases.split('\n')
    
    # Process each line to replace the function name
    modified_lines = []
    for line in lines:
        if line.startswith("assert "):
            # Find the start and end of the function call
            start_index = line.find("assert ") + len("assert ")
            end_index = line.find("(")

            # Replace the function name
            modified_line = "assert " + new_function_name + line[end_index:]
            modified_lines.append(modified_line)
        else:
            modified_lines.append(line)

    # Join the lines back into a single string
    modified_test_cases = '\n'.join(modified_lines)
    return modified_test_cases

def execute_code(code, i):

    context = {'List': List, 'Dict': Dict, 'Any': Any, 'Optional': Optional, 'Tuple': Tuple, 'Union': Union, 'Callable': Callable}
    timeout = 3
    try:
        with swallow_io():
            with time_limit(timeout):
                exec(code, context)
    except Exception as e:
        print(repr(e))
        print("task id: ", i)


model_list = ["gpt-3.5-turbo-0301"]
for model in model_list:
    with open(f"./dataset.json", "r") as f:
        dataset = json.load(f)
    path = f"./{model}_tmp/"
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        os.system(f"rm -rf {path}*")
        # os.makedirs(path)
    with open(f"./leetcode_{model}.json", "r") as f:
        leetcode = json.load(f)
    for i in tqdm(range(len(leetcode))):
        problem_idx = leetcode[i]["problem_idx"]
        try:
            if "class Solution" in leetcode[i]["completion"]:
                if "```python" in leetcode[i]["completion"]:
                    start_idx = leetcode[i]["completion"].find("```python")
                    leetcode[i]["completion"] = leetcode[i]["completion"][start_idx+9:]
                    if "```" in leetcode[i]["completion"]:
                        end_idx = leetcode[i]["completion"].find("```")
                        leetcode[i]["completion"] = leetcode[i]["completion"][:end_idx]
                test_cases = dataset[i]["test_case"].split("\n")
                dataset[i]["test_case"] = "\n".join(test_cases)
                full_code = "from typing import *\nimport random\nimport string\n" + import_pkg + "\n"+TreeNode_text + "\n"+ListNode_text + "\n" + leetcode[i]["completion"] + "\nsolution=Solution()\n" + dataset[i]["test_case"]
                with open(f"./{path}/{problem_idx}.py", "w") as f:
                    f.write(full_code)
            else:
                if "```python" in leetcode[i]["completion"]:
                    start_idx = leetcode[i]["completion"].find("```python")
                    leetcode[i]["completion"] = leetcode[i]["completion"][start_idx+9:]
                    if "```" in leetcode[i]["completion"]:
                        end_idx = leetcode[i]["completion"].find("```")
                        leetcode[i]["completion"] = leetcode[i]["completion"][:end_idx]
                function_name = extract_function_name(leetcode[i]["completion"])
                if function_name == "No function definition found.":
                    continue
                dataset[i]["test_case"] = replace_test_case_function_name(dataset[i]["test_case"], function_name)
                test_cases = dataset[i]["test_case"].split("\n")
                dataset[i]["test_case"] = "\n".join(test_cases)
                full_code = "from typing import *\nimport random\nimport string\n" + import_pkg + "\n"+TreeNode_text + "\n"+ListNode_text + "\n" + leetcode[i]["completion"] + "\n" + dataset[i]["test_case"]
                with open(f"./{path}/{problem_idx}.py", "w") as f:
                    f.write(full_code)
        except Exception as e:
            print(repr(e))


with open("./dataset.json", "r") as f:
    leetcode = json.load(f)


path = f"./canonical_solution_tmp/"
if not os.path.exists(path):
    os.makedirs(path)
else:
    os.system(f"rm -rf {path}*")
    # os.makedirs(path)
for i in tqdm(range(len(leetcode))):
    problem_idx = leetcode[i]["problem_idx"]
    if "```python" in leetcode[i]["canonical_solution"]:
        start_idx = leetcode[i]["canonical_solution"].find("```python")
        leetcode[i]["canonical_solution"] = leetcode[i]["canonical_solution"][start_idx+9:]
        if "```" in leetcode[i]["canonical_solution"]:
            end_idx = leetcode[i]["canonical_solution"].find("```")
            leetcode[i]["canonical_solution"] = leetcode[i]["canonical_solution"][:end_idx]
    try:
        full_code = "from typing import *\nimport random\nimport string\n" + import_pkg + "\n"+TreeNode_text + "\n"+ListNode_text + "\n" + leetcode[i]["canonical_solution"] + "\nsolution=Solution()\n" + dataset[i]["test_case"]
        with open(f"{path}/{problem_idx}.py", "w") as f:
            f.write(full_code)
    except Exception as e:
        pass
