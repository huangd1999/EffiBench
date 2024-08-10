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

with open("./dataset/dataset.json", "r") as f:
    dataset = json.load(f)



# Setting API parameters
openai.api_base = "https://api.aiohub.org/v1"
openai.api_key = 'API_KEY'

text = """Please based on the task description and the provided code to write test case generator to generate test cases for the following task. 
You should must follow the following rules:
First, the code should be in ```python[Code]``` block.
Second, The test case generator should generate 100 test cases.
Third, the generated test cases should be save in a list named ```test_case_generator_results```.
Fourth, the saved test cases should follow the following format:
assert solution.function_name(input1, input2, ...) == expected_result
Fifth, the input1, input2, ... parameters should follow the task description constraints.
Sixth, the expected_result should be calculated using the provided Solution class.
Seventh, considering the tokens requirement, we are focus on small test cases, so the input1, input2, ... parameters should be small numbers~(e.g., the length of each input parameters should lower than 10 if it is a list).
Finally, You should not add the provided code into your ```python[Code]``` block.

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

# Code
```python
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
# Test case generator
```python
def generate_test_case():
    solution = Solution()
    
    # Generate random numbers list
    nums = random.sample(range(1, 101), random.randint(2, 10))
    
    # Generate a random target sum
    target = random.randint(1, 201)

    # Calculate the expected result using the provided Solution class
    expected_result = solution.twoSum(nums, target)

    return nums, target, expected_result

def test_generated_test_cases(num_tests):
    test_case_generator_results = []
    for i in range(num_tests):
        nums, target, expected_result = generate_test_case()
        solution = Solution()
        assert solution.twoSum(nums, target) == expected_result
        if len(expected_result) != 0:
            print(f"assert solution.twoSum({nums}, {target}) == {expected_result}")
            test_case_generator_results.append(f"assert solution.twoSum({nums}, {target}) == {expected_result}") # You can find that we construct the test case in the same format as the example
    return test_case_generator_results

if __name__ == "__main__":
    num_tests = 100  # You can change this to generate more test cases
    test_case_generator_results = test_generated_test_cases(num_tests)
```
"""


# Function to fetch completion
def fetch_completion(data_entry, model):
    try:
        completions = openai.ChatCompletion.create(
            model=model,
            stream=False,
            messages=[
                {"role": "system", "content": "You are a code developer."},
                {"role": "user", "content": text + "\n# Task description:\n```python\n" + data_entry["description"]+"\n```\n# Code:\n```python\n"+data_entry["canonical_solution"]+"\n```"},
            ],
            request_timeout=100,
        )
        data_entry["small_test_case_generator"] = completions.choices[0]["message"]["content"]
    except Exception as e:
        print(repr(e))
        data_entry["small_test_case_generator"] = ""
    return data_entry

if __name__ == "__main__":
    model = "gpt-3.5-turbo"
    with ThreadPoolExecutor(max_workers=100) as executor:
        future_to_entry = {executor.submit(fetch_completion, copy.deepcopy(entry), model): entry for entry in tqdm(dataset)}
        for future in tqdm(concurrent.futures.as_completed(future_to_entry)):
            entry = future_to_entry[future]
            try:
                updated_entry = future.result()
                idx = dataset.index(entry)
                dataset[idx] = updated_entry
            except Exception as e:
                print(repr(e))
    with open("./dataset/leetcode_with_test_generator.json", "w") as f:
        json.dump(dataset, f, indent=4)
