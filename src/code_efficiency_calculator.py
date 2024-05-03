import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from tqdm import tqdm

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
            full_code = data["completion"] + "\nsolution=Solution()\n" + test_case
            with open(f"./{path}/{problem_idx}.py", "w") as f:
                f.write(full_code)
            return_path = f"./{path}/{problem_idx}.py"
    except Exception as e:
        pass
    return return_path, full_code

if __name__ == "__main__":
    models = ["codellama/CodeLlama-70b-Instruct-hf", "gpt-3.5-turbo-0301"]
    for model in models:
        if "/" in model:
            model = model.split("/")[1]
        try:
            with open(f"./results/{model}.json", "r") as f:
                dataset = json.load(f)
        except Exception as e:
            print(e)
            continue

        dat_path = f"./dat_results/{model}"
        if os.path.exists(dat_path):
            os.makedirs(dat_path, exist_ok=True)

        fetch_completion(dataset, dat_path)