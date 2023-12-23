import random

class Solution:
    def twoSum(self, nums, target):
        hashtable = dict()
        for i, num in enumerate(nums):
            if target - num in hashtable:
                return [hashtable[target - num], i]
            hashtable[nums[i]] = i
        return []

def generate_test_case():
    solution = Solution()
    
    # Generate random numbers list
    nums = random.sample(range(1, 1001), random.randint(2, 100))
    
    # Generate a random target sum
    target = random.randint(1, 2001)

    # Calculate the expected result using the provided Solution class
    expected_result = solution.twoSum(nums, target)

    return nums, target, expected_result

def test_generated_test_cases(num_tests):
    for i in range(num_tests):
        nums, target, expected_result = generate_test_case()
        solution = Solution()
        assert solution.twoSum(nums, target) == expected_result
        if len(expected_result) != 0:
            # print(f"nums = {nums}")
            # print(f"target = {target}")
            # print(f"expected_result = {expected_result}"
            print(f"assert solution.twoSum({nums}, {target}) == {expected_result}")
    print(f"All {num_tests} generated test cases passed!")

if __name__ == "__main__":
    num_tests = 100000  # You can change this to generate more test cases
    test_generated_test_cases(num_tests)
