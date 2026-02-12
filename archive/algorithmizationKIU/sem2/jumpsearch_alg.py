import time
import random
import math

def JumpSearch(lys, val):
    length = len(lys)
    jump = int(math.sqrt(length))
    left, right = 0, 0
    while left < length and lys[left] <= val:
        right = min(length - 1, left + jump)
        if lys[left] <= val and lys[right] >= val:
            break
        left += jump
    if left >= length or lys[left] > val:
        return -1
    right = min(length - 1, right)
    i = left
    while i <= right and lys[i] <= val:
        if lys[i] == val:
            return i
        i += 1
    return -1

massive = [100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]
itrs = 100

for mnog in massive:
    total_time = 0
    
    for _ in range(itrs):
        spisok = [random.randint(1, mnog) for x in range(mnog)]
        isk = random.randint(1, mnog)
        
        start_bench = time.perf_counter()
        
        spisok.sort()
        JumpSearch(spisok, isk)
        
        end_bench = time.perf_counter()
        
        total_time += (end_bench - start_bench)
    
    avg_time = total_time / itrs
    print(f"{mnog}, {avg_time:.10f}")