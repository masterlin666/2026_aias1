"""
Prerequisite Assessment — Python Problem 1: Reverse Bits

Reverse the bits of a given 32-bit unsigned integer.

Example:
    Input:  n = 0b00000010100101000001111010011100 (43261596)
    Output: 0b00111001011110000010100101000000 (964176192)

Constraints:
    - The input must be a 32-bit unsigned integer (0 <= n <= 2^32 - 1)

Instructions:
    - Implement the reverseBits method below
    - Do NOT modify the class name or method signature
    - You may add helper functions if needed
"""


class Solution:
    def reverseBits(self, n: int) -> int:
        res = 0
        for _ in range(32):
            res = (res << 1)
            res = res | (n & 1)
            n >>= 1
        return res
