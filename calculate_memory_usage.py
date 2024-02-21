import json
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
# 计算内存使用的函数
def calculate_memory_usage(dat_file_path):
    with open(dat_file_path, 'r') as file:
        prev_time = 0
        prev_mem_mb = 0
        mem_time_mb_s = 0
        next(file)  # 跳过第一行（如果有表头的话）
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
        next(file)  # 跳过第一行（如果有表头的话）
        for line in file:
            parts = line.split()
            mem_in_mb = float(parts[1])
            max_memory_usage = max(max_memory_usage, mem_in_mb)
        return max_memory_usage

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# 设置 Seaborn 的风格
sns.set(style="whitegrid")


import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_value_distribution(values, num_buckets, title_suffix, model_name):
    # 计算值的范围
    value_min = np.min(values)
    value_max = np.max(values)
    value_range = value_max - value_min

    # 计算每个桶的大小
    bucket_edges = np.linspace(value_min, value_max, num_buckets + 1)

    # 使用 np.histogram 直接计算桶
    bucket_counts, _ = np.histogram(values, bins=bucket_edges)

    # 生成桶标签
    bucket_labels = [f"{(edge_left + edge_right) / 2:.2f}" for edge_left, edge_right in zip(bucket_edges[:-1], bucket_edges[1:])]

    # 设置图表大小
    plt.figure(figsize=(12, 6))

    # 使用 Seaborn 绘制条形图，并获取条形对象
    barplot = sns.barplot(x=bucket_labels, y=bucket_counts, palette="viridis")

    # 在每个柱形上添加 y 轴数值
    for bar in barplot.patches:
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{int(bar.get_height())}', 
                 ha='center', va='bottom')

    # 仅显示特定的 x 轴坐标
    selected_indices = [0, num_buckets-1]  # 对应于第 1, 5, 10, 15, 20 个坐标
    selected_labels = [bucket_labels[i] for i in selected_indices]
    plt.xticks(selected_indices, selected_labels)

    # 设置 y 轴为对数刻度
    plt.yscale('log')

    # 标注轴
    plt.ylabel('Count')

    # 图表标题
    plt.title(f'{title_suffix}')

    # 使用紧凑布局来适应标签
    plt.tight_layout()

    # 保存图表为文件
    plt.savefig(f"figures/{model_name}_{title_suffix.replace(' ', '_').lower()}_distribution.pdf")
    plt.close()




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

# model_list = ["incoder-1B","incoder-6B","starcoder","codegen-2B-mono","codegen-6B-mono","Magicoder-S-CL-7B","Magicoder-S-DS-6.7B","WizardCoder-15B-V1.0","instructcodet5p-16b","Mistral-7B-Instruct-v0.2","Mistral-7B-v0.1", "CodeLlama-7b-Python-hf", "CodeLlama-13b-Python-hf","gpt-3.5-turbo-0301","gpt-3.5-turbo-0613","gpt-3.5-turbo-1106","gpt-4-1106-preview","gpt-4", "palm-2-chat-bison","claude-instant-1","gemini-pro"]
model_list = ["gpt-3.5-turbo-0301"]
# tests_number = [10,"100_1",1000]
# model_list = ["incoder-1B","incoder-6B","starcoder","codegen-2B-mono","codegen-6B-mono","Magicoder-S-CL-7B","Magicoder-S-DS-6.7B","WizardCoder-15B-V1.0","instructcodet5p-16b","Mistral-7B-Instruct-v0.2","Mistral-7B-v0.1", "CodeLlama-7b-Python-hf", "CodeLlama-13b-Python-hf"]
# model_list = ["gpt-3.5-turbo-0301"]
# model_list = [f"{model}_{test}" for model in model_list for test in tests_number]
canonical_solution_directory = "./canonical_solution_dat"
canonical_solution_memory_usage = {}
canonical_solution_execution_time = {}
canonical_solution_max_memory_usage = {}
for dat_file in glob.glob(os.path.join(canonical_solution_directory, "*.dat")):
    problem_idx = os.path.basename(dat_file).split('.')[0]
    canonical_solution_memory_usage[int(problem_idx)] = calculate_memory_usage(dat_file)
    canonical_solution_execution_time[int(problem_idx)] = calculate_runtime(dat_file)
    canonical_solution_max_memory_usage[int(problem_idx)] = report_max_memory_usage(dat_file)

global_result = {}

for model in model_list:
    completion_memory_usage = {}
    execution_time = {}
    max_memory_usage = {}
    task_idx = {}
    dat_directory = f"./{model}_dat"
    for dat_file in glob.glob(os.path.join(dat_directory, "*.dat")):
        problem_idx = os.path.basename(dat_file).split('.')[0]
        completion_memory_usage[int(problem_idx)] = calculate_memory_usage(dat_file)
        execution_time[int(problem_idx)] = calculate_runtime(dat_file)
        max_memory_usage[int(problem_idx)] = report_max_memory_usage(dat_file)
        task_idx[int(problem_idx)] = dat_file

    global_result[model] = {"completion_memory_usage":completion_memory_usage,"execution_time":execution_time,"max_memory_usage":max_memory_usage,"task_idx":task_idx}

    # total_memory_usage = 0
    # total_execution_time = 0
    # total_max_memory_usage = 0

    # for key in completion_memory_usage:
    #     total_memory_usage += completion_memory_usage[key]
    #     total_execution_time += execution_time[key]
    #     total_max_memory_usage += max_memory_usage[key]

    # print(f"Total Memory Usage of {model}: {total_memory_usage} MB*seconds")
    # print(f"Total Execution Time of {model}: {total_execution_time} seconds")
    # print(f"Total Max Memory Usage of {model}: {total_max_memory_usage} MB")



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
    for idx in completion_memory_usage.keys():
        if idx not in canonical_solution_memory_usage.keys():
            continue
        total_memory_usage += completion_memory_usage[idx]
        total_execution_time += execution_time[idx]
        total_max_memory_usage += max_memory_usage[idx]
        if execution_time[idx]<canonical_solution_execution_time[idx]:
            print(f"{model}&Execution Time of {idx} is {execution_time[idx]} seconds, while canonical solution is {canonical_solution_execution_time[idx]} seconds&{execution_time[idx]/canonical_solution_execution_time[idx]:.2f}")
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

        # if max_memory_usage[idx]/canonical_solution_max_memory_usage[idx]>10:
        #     print(f"Max Memory Usage of {idx} is {max_memory_usage[idx]} MB, while canonical solution is {canonical_solution_max_memory_usage[idx]} MB")
        # if max_memory_usage[idx]/canonical_solution_max_memory_usage[idx]<0.95:
        #     total_95+=1
        # if max_memory_usage[idx]/canonical_solution_max_memory_usage[idx]<0.97:
        #     total_97+=1
        # if max_memory_usage[idx]/canonical_solution_max_memory_usage[idx]<0.99:
        #     total_99+=1
        # if max_memory_usage[idx]/canonical_solution_max_memory_usage[idx]<1:
        #     total_100+=1
        # if max_memory_usage[idx]/canonical_solution_max_memory_usage[idx]>1:
        #     total_101+=1
        # if max_memory_usage[idx]/canonical_solution_max_memory_usage[idx]>5:
        #     total_500+=1
        # if max_memory_usage[idx]/canonical_solution_max_memory_usage[idx]>10:
        #     total_1000+=1
        # if max_memory_usage[idx]/canonical_solution_max_memory_usage[idx]>100:
        #     total_10000+=1
        # if min_net>max_memory_usage[idx]/canonical_solution_max_memory_usage[idx]:
        #     min_net = max_memory_usage[idx]/canonical_solution_max_memory_usage[idx]
        # if max_net<max_memory_usage[idx]/canonical_solution_max_memory_usage[idx]:
        #     max_net = max_memory_usage[idx]/canonical_solution_max_memory_usage[idx]
        normalized_max_memory_usage += max_memory_usage[idx]/canonical_solution_max_memory_usage[idx]
        normalized_max_memory_usage_list.append(max_memory_usage[idx]/canonical_solution_max_memory_usage[idx])
        # if completion_memory_usage[idx]/canonical_solution_memory_usage[idx]>5:
        #     print(f"Memory Usage of {idx} is {completion_memory_usage[idx]} MB*seconds, while canonical solution is {canonical_solution_memory_usage[idx]} MB*seconds")

        # if completion_memory_usage[idx]/canonical_solution_memory_usage[idx]<0.95:
        #     total_95+=1
        # if completion_memory_usage[idx]/canonical_solution_memory_usage[idx]<0.97:
        #     total_97+=1
        # if completion_memory_usage[idx]/canonical_solution_memory_usage[idx]<0.99:
        #     total_99+=1
        # if completion_memory_usage[idx]/canonical_solution_memory_usage[idx]<1:
        #     total_100+=1
        # if completion_memory_usage[idx]/canonical_solution_memory_usage[idx]>1:
        #     total_101+=1
        # if completion_memory_usage[idx]/canonical_solution_memory_usage[idx]>5:
        #     total_500+=1
        # if completion_memory_usage[idx]/canonical_solution_memory_usage[idx]>10:
        #     total_1000+=1
        # if completion_memory_usage[idx]/canonical_solution_memory_usage[idx]>100:
        #     total_10000+=1
        # if min_net>completion_memory_usage[idx]/canonical_solution_memory_usage[idx]:
        #     min_net = completion_memory_usage[idx]/canonical_solution_memory_usage[idx]
        

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
    # print(f"{model}&"+"&".join([str(total_95),str(total_96),str(total_97),str(total_98),str(total_99),str(total_100),str(total_codes)])+"\\\\")
    print(f"{model}&{min_net:.2f}&{total_95:.2f}&{total_97:.2f}&{total_99:.2f}&{total_100:.2f}&{total_101:.2f}&{total_500:.2f}&{total_1000:.2f}&{total_10000:.2f}&{max_net:.2f}\\\\")
    # print(len(completion_memory_usage), normalized_execution_time,normalized_max_memory_usage,normalized_memory_usage)
    if len(normalized_execution_time_list)==0:
        # print(f"[0,0,0,0,0,0,0]")
        print(model)
        continue
    total_execution_time = total_execution_time/len(normalized_execution_time_list)
    total_memory_usage = total_memory_usage/len(normalized_execution_time_list)
    total_max_memory_usage = total_max_memory_usage/len(normalized_execution_time_list)
    normalized_execution_time /= len(normalized_execution_time_list)
    normalized_max_memory_usage /= len(normalized_execution_time_list)
    normalized_memory_usage /= len(normalized_execution_time_list)
    pass1 = len(normalized_execution_time_list)/1000*100


    # ranges = 100
    # analyze_value_distribution(list(completion_memory_usage.values()), ranges, 'Completion Memory Usage',model)
    # analyze_value_distribution(list(execution_time.values()), ranges, 'Execution Time',model)
    # analyze_value_distribution(list(max_memory_usage.values()), ranges, 'Max Memory Usage',model)
    # analyze_value_distribution(normalized_execution_time_list, ranges, 'Normalized Execution Time',model)
    # analyze_value_distribution(normalized_max_memory_usage_list, ranges, 'Normalized Max Memory Usage',model)
    # analyze_value_distribution(normalized_memory_usage_list, ranges, 'Normalized Memory Usage',model)


    # print(f"Total Execution Time of {model}: {total_execution_time:.1f} seconds")
    # print(f"Normalized Execution Time of {model}: {normalized_execution_time:.1f}")
    # print(f"Total Max Memory Usage of {model}: {total_max_memory_usage:.1f} MB")
    # print(f"Normalized Max Memory Usage of {model}: {normalized_max_memory_usage:.1f}")
    # print(f"Total Memory Usage of {model}: {total_memory_usage:.1f} MB*seconds")
    # print(f"Normalized Memory Usage of {model}: {normalized_memory_usage:.1f}")
    # print(f"Model:{model}")
    # print(len(completion_memory_usage), normalized_execution_time,normalized_max_memory_usage,normalized_memory_usage)
    total_1000_net = total_1000_net/len(normalized_execution_time_list)*100
    total_1000_nmu = total_1000_nmu/len(normalized_execution_time_list)*100
    total_1000_tmu = total_1000_tmu/len(normalized_execution_time_list)*100
    # print(f"{model}&{total_execution_time:.2f}&{normalized_execution_time:.2f}&{max_net:.2f}&{total_1000_net:.1f}&{total_max_memory_usage:.2f}&{normalized_max_memory_usage:.2f}&{max_nmu:.2f}&{total_1000_nmu:.1f}&{total_memory_usage:.2f}&{normalized_memory_usage:.2f}&{max_tmu:.2f}&{total_1000_tmu:.1f}&{pass1:.1f}\\\\")
    # print(model,max_task_idx)
    # print(f"[{total_execution_time:.2f},{normalized_execution_time:.2f},{total_max_memory_usage:.2f},{normalized_max_memory_usage:.2f},{total_memory_usage:.2f},{normalized_memory_usage:.2f},{pass1:.1f}],")
    # print("=========================================")

    category_tmp = {}

    for task in global_task_idx:
        task_memory_usage = 0
        canonical_solution_task_memory_usage = 0
        task_total_execution_time = 0
        task_total_max_memory_usage = 0
        task_total_memory_usage = 0
        task_normalized_execution_time = 0
        task_normalized_max_memory_usage = 0
        task_normalized_memory_usage = 0
        total = 0
        max_net = float("-inf")
        max_nmu = float("-inf")
        max_tmu = float("-inf")
        total_1000_net = 0
        total_1000_nmu = 0
        total_1000_tmu = 0
        for idx in task["task_ids"]:
            if idx in completion_memory_usage:
                if idx not in canonical_solution_memory_usage.keys():
                    continue
                task_memory_usage += completion_memory_usage[idx]
                task_total_execution_time += execution_time[idx]
                task_total_max_memory_usage += max_memory_usage[idx]
                task_total_memory_usage += completion_memory_usage[idx]
                task_normalized_execution_time += execution_time[idx]/canonical_solution_execution_time[idx]
                task_normalized_max_memory_usage += max_memory_usage[idx]/canonical_solution_max_memory_usage[idx]
                task_normalized_memory_usage += completion_memory_usage[idx]/canonical_solution_memory_usage[idx]
                if execution_time[idx]/canonical_solution_execution_time[idx]>5:
                    total_1000_net+=1
                max_net = max(max_net,execution_time[idx]/canonical_solution_execution_time[idx])
                if max_memory_usage[idx]/canonical_solution_max_memory_usage[idx]>5:
                    total_1000_nmu+=1
                max_nmu = max(max_nmu,max_memory_usage[idx]/canonical_solution_max_memory_usage[idx])
                if completion_memory_usage[idx]/canonical_solution_memory_usage[idx]>5:
                    total_1000_tmu+=1
                max_tmu = max(max_tmu,completion_memory_usage[idx]/canonical_solution_memory_usage[idx])
                total+=1
        if total == 0:
            pass1 = 0
            task_normalized_execution_time = 0
            task_normalized_max_memory_usage = 0
            task_normalized_memory_usage = 0
            task_total_execution_time = 0
            task_total_max_memory_usage = 0
            task_total_memory_usage = 0
        else:
            pass1 = total/total_dict[task["task"]]*100
            task_normalized_execution_time = task_normalized_execution_time/total
            task_normalized_max_memory_usage = task_normalized_max_memory_usage/total
            task_normalized_memory_usage = task_normalized_memory_usage/total
            task_total_execution_time = task_total_execution_time/total
            task_total_max_memory_usage = task_total_max_memory_usage/total
            task_total_memory_usage = task_total_memory_usage/total
            total_1000_net = total_1000_net/total*100
            total_1000_nmu = total_1000_nmu/total*100
            total_1000_tmu = total_1000_tmu/total*100

        # category_tmp[task["task"]] = {"task_memory_usage":task_memory_usage,"task_total_execution_time":task_total_execution_time,"task_total_max_memory_usage":task_total_max_memory_usage,"task_total_memory_usage":task_total_memory_usage,"task_normalized_execution_time":task_normalized_execution_time,"task_normalized_max_memory_usage":task_normalized_max_memory_usage,"task_normalized_memory_usage":task_normalized_memory_usage,"total":total,"pass":pass1}
        task_escaped = task["task"].replace('_', '\_')
        print(f"{task_escaped}&{task_total_execution_time:.2f}&{task_normalized_execution_time:.2f}&{max_net:.2f}&{total_1000_net:.1f}&{task_total_max_memory_usage:.2f}&{task_normalized_max_memory_usage:.2f}&{max_nmu:.2f}&{total_1000_nmu:.1f}&{task_total_memory_usage:.2f}&{task_normalized_memory_usage:.2f}&{max_tmu:.2f}&{total_1000_tmu:.1f}&{pass1:.1f}\\\\")

    # with open(f"./task_tmp/{model}.json", "w") as f:
    #     json.dump(category_tmp, f, indent=4)

    # for task in category_tmp.keys():
    #     # print(f"{model}:The total memory usage of {task} is {category_tmp[task]['task_memory_usage']:.1f} MB*seconds")
    #     # print(f"{model}:The normalized memory usage of {task} is {category_tmp[task]['task_normalized_memory_usage']:.1f}")
    #     # print(f"{model}:The total execution time of {task} is {category_tmp[task]['task_total_execution_time']:.1f} seconds")
    #     # print(f"{model}:The normalized execution time of {task} is {category_tmp[task]['task_normalized_execution_time']:.1f}")
    #     # print(f"{model}:The total max memory usage of {task} is {category_tmp[task]['task_total_max_memory_usage']:.1f} MB")
    #     # print(f"{model}:The normalized max memory usage of {task} is {category_tmp[task]['task_normalized_max_memory_usage']:.1f}")

    #     task_escaped = task.replace('_', '\_')

    #     print(f"{task_escaped}&{category_tmp[task]['task_total_execution_time']:.2f}&{category_tmp[task]['task_normalized_execution_time']:.2f}&{category_tmp[task]['task_total_max_memory_usage']:.2f}&{category_tmp[task]['task_normalized_max_memory_usage']:.2f}&{category_tmp[task]['task_total_memory_usage']:.2f}&{category_tmp[task]['task_normalized_memory_usage']:.2f}&{category_tmp[task]['pass']:.1f}\\\\")

    #     # print(f"{task}&{category_tmp[task]['task_total_execution_time']:.1f}&{category_tmp[task]['task_normalized_execution_time']:.1f}&{category_tmp[task]['task_total_max_memory_usage']:.1f}&{category_tmp[task]['task_normalized_max_memory_usage']:.1f}&{category_tmp[task]['task_total_memory_usage']:.1f}&{category_tmp[task]['task_normalized_memory_usage']:.1f}&{category_tmp[task]['pass']:.1f}\\\\")
    #     # print("=========================================")


