import json
import os
import glob
import numpy as np
import matplotlib.pyplot as plt


def calculate_memory_usage(dat_file_path):
    with open(dat_file_path, 'r') as file:
        prev_time = 0
        prev_mem_mb = 0
        mem_time_mb_s = 0
        next(file)
        for line in file:
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
            parts = line.split()
            mem_in_mb = float(parts[1])
            max_memory_usage = max(max_memory_usage, mem_in_mb)
        return max_memory_usage

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

sns.set(style="whitegrid")


import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns





with open("./algorithm_task_idx.json", "r") as f:
    global_task_idx = json.load(f)

with open("./dataset.json", "r") as f:
    dataset = json.load(f)


problem_idxs = {entry["problem_idx"]: i for i, entry in enumerate(dataset)}

total_dict = {}
for task in global_task_idx:
    total_dict[task["task"]] = 0
    for idx in task["task_ids"]:
        if idx in problem_idxs:
            total_dict[task["task"]] += 1


model_list = ["gpt-3.5-turbo-0301","gpt-3.5-turbo-0613","gpt-3.5-turbo-1106","gpt-4-turbo-preview","gpt-4"]
canonical_solution_directory = "./canonical_solution_cpp"
canonical_solution_memory_usage = {}
canonical_solution_execution_time = {}
canonical_solution_max_memory_usage = {}
for dat_file in glob.glob(os.path.join(canonical_solution_directory, "*.dat")):
    try:
        problem_idx = os.path.basename(dat_file).split('.')[0]
        canonical_solution_memory_usage[int(problem_idx)] = calculate_memory_usage(dat_file)
        canonical_solution_execution_time[int(problem_idx)] = calculate_runtime(dat_file)
        canonical_solution_max_memory_usage[int(problem_idx)] = report_max_memory_usage(dat_file)
    except:
        pass


global_result = {}

for model in model_list:
    completion_memory_usage = {}
    execution_time = {}
    max_memory_usage = {}
    task_idx = {}
    dat_directory = f"./{model}_cpp"
    for dat_file in glob.glob(os.path.join(dat_directory, "*.dat")):
        problem_idx = os.path.basename(dat_file).split('.')[0]
        completion_memory_usage[int(problem_idx)] = calculate_memory_usage(dat_file)
        execution_time[int(problem_idx)] = calculate_runtime(dat_file)
        max_memory_usage[int(problem_idx)] = report_max_memory_usage(dat_file)
        task_idx[int(problem_idx)] = dat_file

    global_result[model] = {"completion_memory_usage":completion_memory_usage,"execution_time":execution_time,"max_memory_usage":max_memory_usage,"task_idx":task_idx}




for model in global_result.keys():
    completion_memory_usage = global_result[model]["completion_memory_usage"]
    execution_time = global_result[model]["execution_time"]
    max_memory_usage = global_result[model]["max_memory_usage"]

    # report execution time
    total_execution_time = 0

    # report normalized execution time
    normalized_execution_time = 0

    # report max memory usage
    total_max_memory_usage = 0

    # report normalized max memory usage
    normalized_max_memory_usage = 0

    # report memory usage
    total_memory_usage = 0

    # report normalized memory usage
    normalized_memory_usage = 0
    total_codes = 0
    normalized_execution_time_list = []
    normalized_max_memory_usage_list = []
    normalized_memory_usage_list = []
    total_fast = 0
    total_95 = 0
    total_97=0
    total_99=0
    total_100=0
    total_101=0
    total_1000=0
    total_500=0
    total_10000=0
    max_net = float("-inf")
    max_nmu = float("-inf")
    max_tmu = float("-inf")
    min_net = float("inf")

    total_1000_net = 0
    total_1000_nmu = 0
    total_1000_tmu = 0
    # print(len(completion_memory_usage))
    for idx in completion_memory_usage.keys():
        if idx not in canonical_solution_memory_usage.keys():
            continue
        total_memory_usage += completion_memory_usage[idx]
        total_execution_time += execution_time[idx]
        total_max_memory_usage += max_memory_usage[idx]
        # if execution_time[idx]<canonical_solution_execution_time[idx]:
        #     print(f"{model}&Execution Time of {idx} is {execution_time[idx]} seconds, while canonical solution is {canonical_solution_execution_time[idx]} seconds&{execution_time[idx]/canonical_solution_execution_time[idx]:.2f}")
        if execution_time[idx]/canonical_solution_execution_time[idx]<0.95:
            total_95+=1
        if execution_time[idx]/canonical_solution_execution_time[idx]<0.97:
            total_97+=1
        if execution_time[idx]/canonical_solution_execution_time[idx]<0.99:
            total_99+=1
        if execution_time[idx]/canonical_solution_execution_time[idx]<1:
            total_100+=1
        if execution_time[idx]/canonical_solution_execution_time[idx]>1:
            total_101+=1
        if execution_time[idx]/canonical_solution_execution_time[idx]>5:
            total_500+=1
        if execution_time[idx]/canonical_solution_execution_time[idx]>10:
            total_1000+=1
        if execution_time[idx]/canonical_solution_execution_time[idx]>100:
            total_10000+=1
        if min_net>execution_time[idx]/canonical_solution_execution_time[idx]:
            min_net = execution_time[idx]/canonical_solution_execution_time[idx]
        if max_net<execution_time[idx]/canonical_solution_execution_time[idx]:
            max_net = execution_time[idx]/canonical_solution_execution_time[idx]
        normalized_execution_time += execution_time[idx]/canonical_solution_execution_time[idx]
        normalized_execution_time_list.append(execution_time[idx]/canonical_solution_execution_time[idx])

        normalized_max_memory_usage += max_memory_usage[idx]/canonical_solution_max_memory_usage[idx]
        normalized_max_memory_usage_list.append(max_memory_usage[idx]/canonical_solution_max_memory_usage[idx])


        normalized_memory_usage += completion_memory_usage[idx]/canonical_solution_memory_usage[idx]
        normalized_memory_usage_list.append(completion_memory_usage[idx]/canonical_solution_memory_usage[idx])
        if execution_time[idx]/canonical_solution_execution_time[idx]>5:
            total_1000_net+=1
        max_net = max(max_net,execution_time[idx]/canonical_solution_execution_time[idx])
        if max_memory_usage[idx]/canonical_solution_max_memory_usage[idx]>5:
            total_1000_nmu+=1
        max_nmu = max(max_nmu,max_memory_usage[idx]/canonical_solution_max_memory_usage[idx])
        if completion_memory_usage[idx]/canonical_solution_memory_usage[idx]>5:
            total_1000_tmu+=1
        max_tmu = max(max_tmu,completion_memory_usage[idx]/canonical_solution_memory_usage[idx])
        total_codes+=1
    total_95 = total_95/total_codes*100
    total_97 = total_97/total_codes*100
    total_99 = total_99/total_codes*100
    total_100 = total_100/total_codes*100
    total_101 = total_101/total_codes*100
    total_500 = total_500/total_codes*100
    total_1000 = total_1000/total_codes*100
    total_10000 = total_10000/total_codes*100

    total_execution_time = total_execution_time/len(normalized_execution_time_list)
    total_memory_usage = total_memory_usage/len(normalized_execution_time_list)
    total_max_memory_usage = total_max_memory_usage/len(normalized_execution_time_list)
    normalized_execution_time /= len(normalized_execution_time_list)
    normalized_max_memory_usage /= len(normalized_execution_time_list)
    normalized_memory_usage /= len(normalized_execution_time_list)
    pass1 = len(normalized_execution_time_list)/1000*100

    total_1000_net = total_1000_net/len(normalized_execution_time_list)*100
    total_1000_nmu = total_1000_nmu/len(normalized_execution_time_list)*100
    total_1000_tmu = total_1000_tmu/len(normalized_execution_time_list)*100
    # print(f"{model}&{total_execution_time:.2f}&{normalized_execution_time:.2f}&{max_net:.2f}&{total_1000_net:.1f}&{total_max_memory_usage:.2f}&{normalized_max_memory_usage:.2f}&{max_nmu:.2f}&{total_1000_nmu:.1f}&{total_memory_usage:.2f}&{normalized_memory_usage:.2f}&{max_tmu:.2f}&{total_1000_tmu:.1f}&{pass1:.1f}\\\\")
    print(f"{model}&{total_execution_time:.2f}&{normalized_execution_time:.2f}&{total_max_memory_usage:.2f}&{normalized_max_memory_usage:.2f}&{total_memory_usage:.2f}&{normalized_memory_usage:.2f}&{pass1:.1f}\\\\")
