from typing import *
import random
import string


class TreeNode:
    def __init__(self, val=0, left=None, right=None, next=None):
        self.val = val
        self.left = left
        self.right = right
        self.next = next


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        left = 0
        right = 0
        count = 0
        max_count = 0
        char_set = set()
        while right < len(s):
            if s[right] in char_set:
                char_set.remove(s[left])
                left += 1
                count -= 1
            else:
                char_set.add(s[right])
                right += 1
                count += 1
                max_count = max(max_count, count)
        return max_count

solution=Solution()
assert solution.lengthOfLongestSubstring('') == 0
assert solution.lengthOfLongestSubstring('krLKl6F') == 7
assert solution.lengthOfLongestSubstring('p2Cn3Y6') == 7
assert solution.lengthOfLongestSubstring('jf') == 2
assert solution.lengthOfLongestSubstring('ebl') == 3
assert solution.lengthOfLongestSubstring('7FHbLe') == 6
assert solution.lengthOfLongestSubstring('cUoD0S') == 6
assert solution.lengthOfLongestSubstring('M1kCixrcvS') == 10
assert solution.lengthOfLongestSubstring('V9sGI') == 5
assert solution.lengthOfLongestSubstring('0iTSFPsD5') == 9
assert solution.lengthOfLongestSubstring('D') == 1
assert solution.lengthOfLongestSubstring('ncNp') == 4
assert solution.lengthOfLongestSubstring('FKdZH') == 5
assert solution.lengthOfLongestSubstring('FqhvT67') == 7
assert solution.lengthOfLongestSubstring('D1zyWG0a') == 8
assert solution.lengthOfLongestSubstring('VyOucQ') == 6
assert solution.lengthOfLongestSubstring('SXqMDBVoEN') == 10
assert solution.lengthOfLongestSubstring('mYjdE1QjDm') == 7
assert solution.lengthOfLongestSubstring('4rd2vxkZZR') == 8
assert solution.lengthOfLongestSubstring('qWggGpiX') == 5
assert solution.lengthOfLongestSubstring('yEk') == 3
assert solution.lengthOfLongestSubstring('1SbbkRXgx') == 6
assert solution.lengthOfLongestSubstring('WnLZ') == 4
assert solution.lengthOfLongestSubstring('pEF') == 3
assert solution.lengthOfLongestSubstring('d7OCVynX0') == 9
assert solution.lengthOfLongestSubstring('') == 0
assert solution.lengthOfLongestSubstring('qSPMKL2Pa') == 7
assert solution.lengthOfLongestSubstring('PrYzK1nUJ') == 9
assert solution.lengthOfLongestSubstring('JBu') == 3
assert solution.lengthOfLongestSubstring('IBCg7KcjgY') == 8
assert solution.lengthOfLongestSubstring('T') == 1
assert solution.lengthOfLongestSubstring('Rjy5bwtsK') == 9
assert solution.lengthOfLongestSubstring('Brh') == 3
assert solution.lengthOfLongestSubstring('DPz') == 3
assert solution.lengthOfLongestSubstring('kSu99Brx') == 4
assert solution.lengthOfLongestSubstring('m') == 1
assert solution.lengthOfLongestSubstring('KMa') == 3
assert solution.lengthOfLongestSubstring('VLOg') == 4
assert solution.lengthOfLongestSubstring('UmRlK') == 5
assert solution.lengthOfLongestSubstring('AWw2zq') == 6
assert solution.lengthOfLongestSubstring('VBs2uAH3H') == 8
assert solution.lengthOfLongestSubstring('ufSovl54BW') == 10
assert solution.lengthOfLongestSubstring('vStUY7') == 6
assert solution.lengthOfLongestSubstring('oGF') == 3
assert solution.lengthOfLongestSubstring('0Xj') == 3
assert solution.lengthOfLongestSubstring('4') == 1
assert solution.lengthOfLongestSubstring('aFevv') == 4
assert solution.lengthOfLongestSubstring('Xz') == 2
assert solution.lengthOfLongestSubstring('StG4') == 4
assert solution.lengthOfLongestSubstring('Rie') == 3
assert solution.lengthOfLongestSubstring('8RY3erTER') == 8
assert solution.lengthOfLongestSubstring('BN2n6AoJ0c') == 10
assert solution.lengthOfLongestSubstring('UO') == 2
assert solution.lengthOfLongestSubstring('VmBZvv1') == 5
assert solution.lengthOfLongestSubstring('LMWQ') == 4
assert solution.lengthOfLongestSubstring('') == 0
assert solution.lengthOfLongestSubstring('80') == 2
assert solution.lengthOfLongestSubstring('xvr') == 3
assert solution.lengthOfLongestSubstring('L1sr9dvT') == 8
assert solution.lengthOfLongestSubstring('F') == 1
assert solution.lengthOfLongestSubstring('9mBKJg2RoF') == 10
assert solution.lengthOfLongestSubstring('u3SHz53') == 6
assert solution.lengthOfLongestSubstring('uIxsZwqW2u') == 9
assert solution.lengthOfLongestSubstring('iiJ30w') == 5
assert solution.lengthOfLongestSubstring('LPK5N') == 5
assert solution.lengthOfLongestSubstring('MvYNcL') == 6
assert solution.lengthOfLongestSubstring('PidX') == 4
assert solution.lengthOfLongestSubstring('c0c') == 2
assert solution.lengthOfLongestSubstring('') == 0
assert solution.lengthOfLongestSubstring('UUBXog7At') == 8
assert solution.lengthOfLongestSubstring('uY9RR0') == 4
assert solution.lengthOfLongestSubstring('') == 0
assert solution.lengthOfLongestSubstring('SLWSu53h') == 7
assert solution.lengthOfLongestSubstring('vhsRBcC') == 7
assert solution.lengthOfLongestSubstring('WDkR2G3jSH') == 10
assert solution.lengthOfLongestSubstring('') == 0
assert solution.lengthOfLongestSubstring('Ssid5') == 5
assert solution.lengthOfLongestSubstring('xLZ8IF1FIT') == 7
assert solution.lengthOfLongestSubstring('9day') == 4
assert solution.lengthOfLongestSubstring('uPvh71l') == 7
assert solution.lengthOfLongestSubstring('AICk') == 4
assert solution.lengthOfLongestSubstring('E5D') == 3
assert solution.lengthOfLongestSubstring('eJ5D1gPo') == 8
assert solution.lengthOfLongestSubstring('OdrwR') == 5
assert solution.lengthOfLongestSubstring('ztJjPukfhk') == 9
assert solution.lengthOfLongestSubstring('gE') == 2
assert solution.lengthOfLongestSubstring('Yp0') == 3
assert solution.lengthOfLongestSubstring('Ue9Pqe74k') == 7
assert solution.lengthOfLongestSubstring('5') == 1
assert solution.lengthOfLongestSubstring('BdauxZZFxu') == 6
assert solution.lengthOfLongestSubstring('FZhAzP20n') == 9
assert solution.lengthOfLongestSubstring('iBFKT') == 5
assert solution.lengthOfLongestSubstring('kd') == 2
assert solution.lengthOfLongestSubstring('GzLCgm1lF') == 9
assert solution.lengthOfLongestSubstring('GxkMbFuM') == 7
assert solution.lengthOfLongestSubstring('') == 0
assert solution.lengthOfLongestSubstring('OGa7brYx3e') == 10
assert solution.lengthOfLongestSubstring('743lBZ2upV') == 10
assert solution.lengthOfLongestSubstring('vVj') == 3
assert solution.lengthOfLongestSubstring('') == 0