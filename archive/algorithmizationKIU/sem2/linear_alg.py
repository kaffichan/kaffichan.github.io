import time
import random
for mnog in [100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]:
    avg_time = 0
    for spisok in range(100):
        spisok = [random.randint(1, mnog) for x in range(0, mnog)]
        isk = random.randint(1, mnog)
        time_start = time.perf_counter()
        find_index = -1
        for index in range(len(spisok)):
            if spisok[index] == isk:
                find_index = index
        avg_time = avg_time + time.perf_counter() - time_start
    print(mnog,",", avg_time / 100)