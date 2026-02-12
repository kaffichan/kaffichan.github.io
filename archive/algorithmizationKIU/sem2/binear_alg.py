import time
import random

itrs = 100

for mnog in [100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]:
    total_time_size = 0
    
    for _ in range(itrs):
        spisok = [random.randint(1, mnog) for x in range(mnog)]
        isk = random.randint(1, mnog)
        
        t_sort_start = time.perf_counter()
        spisok.sort()
        t_sort_end = time.perf_counter()
        sort_dur = t_sort_end - t_sort_start
        
        t_search_start = time.perf_counter()
        first = 0
        last = len(spisok) - 1
        index = -1
        while (first <= last) and (index == -1):
            mid = (first + last) // 2
            if spisok[mid] == isk:
                index = mid
            else:
                if isk < spisok[mid]:
                    last = mid - 1
                else:
                    first = mid + 1
        t_search_end = time.perf_counter()
        search_dur = t_search_end - t_search_start
    
        total_time_size += (sort_dur + search_dur)

    avg_time = total_time_size / itrs
    
    print(f"{mnog} , {avg_time:.8f}")