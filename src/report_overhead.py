import json
import os
import glob
from tqdm import tqdm

def calculate_memory_usage(dat_file_path):
    with open(dat_file_path, 'r') as file:
        prev_time = 0
        prev_mem_mb = 0
        mem_time_mb_s = 0
        next(file)
        for line in file:
            if "__main__." in line:
                continue
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
            if "__main__." in line:
                continue
            parts = line.split()
            timestamp = float(parts[2])
            start_time = min(start_time, timestamp)
            end_time = max(end_time, timestamp)
        return max(end_time - start_time, 0)

def report_max_memory_usage(dat_file_path):
    max_memory_usage = 0
    with open(dat_file_path, 'r') as file:
        next(file)
        for line in file:
            if "__main__." in line:
                continue
            parts = line.split()
            mem_in_mb = float(parts[1])
            max_memory_usage = max(max_memory_usage, mem_in_mb)
        return max_memory_usage

model_list = ["codellama/CodeLlama-70b-Instruct-hf", "gpt-3.5-turbo-0301"]
canonical_solution_directory = "./dat_results/canonical_solution"
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
    if "/" in model:
        model = model.split("/")[1]
    completion_memory_usage = {}
    execution_time = {}
    max_memory_usage = {}
    task_idx = {}
    dat_directory = f"./dat_results/{model}"
    for dat_file in glob.glob(os.path.join(dat_directory, "*.dat")):
        try:
            problem_idx = os.path.basename(dat_file).split('.')[0]
            completion_memory_usage[int(problem_idx)] = calculate_memory_usage(dat_file)
            execution_time[int(problem_idx)] = calculate_runtime(dat_file)
            max_memory_usage[int(problem_idx)] = report_max_memory_usage(dat_file)
            task_idx[int(problem_idx)] = dat_file
        except Exception as e:
            print(dat_file)
    global_result[model] = {
        "completion_memory_usage": completion_memory_usage,
        "execution_time": execution_time,
        "max_memory_usage": max_memory_usage,
        "task_idx": task_idx
    }

for model in global_result.keys():
    completion_memory_usage = global_result[model]["completion_memory_usage"]
    execution_time = global_result[model]["execution_time"]
    max_memory_usage = global_result[model]["max_memory_usage"]

    total_execution_time = 0
    normalized_execution_time = 0
    total_max_memory_usage = 0
    normalized_max_memory_usage = 0
    total_memory_usage = 0
    total_canonical_solution_max_memory_usage = 0
    total_canonical_solution_execution_time = 0
    total_canonical_solution_memory_usage = 0
    normalized_memory_usage = 0
    total_codes = 0
    normalized_execution_time_list = []
    normalized_max_memory_usage_list = []
    normalized_memory_usage_list = []

    for idx in completion_memory_usage.keys():
        if idx not in canonical_solution_memory_usage.keys():
            continue

        total_memory_usage += completion_memory_usage[idx]
        total_execution_time += execution_time[idx]
        total_max_memory_usage += max_memory_usage[idx]
        total_canonical_solution_max_memory_usage += canonical_solution_max_memory_usage[idx]
        total_canonical_solution_memory_usage += canonical_solution_memory_usage[idx]
        total_canonical_solution_execution_time += canonical_solution_execution_time[idx]

        normalized_execution_time += execution_time[idx] / canonical_solution_execution_time[idx]
        normalized_execution_time_list.append(execution_time[idx] / canonical_solution_execution_time[idx])

        normalized_max_memory_usage += max_memory_usage[idx] / canonical_solution_max_memory_usage[idx]
        normalized_max_memory_usage_list.append(max_memory_usage[idx] / canonical_solution_max_memory_usage[idx])

        normalized_memory_usage += completion_memory_usage[idx] / canonical_solution_memory_usage[idx]
        normalized_memory_usage_list.append(completion_memory_usage[idx] / canonical_solution_memory_usage[idx])

        total_codes += 1

    if len(normalized_execution_time_list) == 0:
        print(model)
        continue

    normalized_execution_time = total_execution_time / total_canonical_solution_execution_time
    normalized_max_memory_usage = total_max_memory_usage / total_canonical_solution_max_memory_usage
    normalized_memory_usage = total_memory_usage / total_canonical_solution_memory_usage
    total_execution_time = total_execution_time / len(normalized_execution_time_list)
    total_memory_usage = total_memory_usage / len(normalized_execution_time_list)
    total_max_memory_usage = total_max_memory_usage / len(normalized_execution_time_list)

    pass1 = len(normalized_execution_time_list) / 1000 * 100

    print(f"{model}&{total_execution_time:.2f}&{normalized_execution_time:.2f}&{total_max_memory_usage:.2f}&{normalized_max_memory_usage:.2f}&{total_memory_usage:.2f}&{normalized_memory_usage:.2f}\\\\")
