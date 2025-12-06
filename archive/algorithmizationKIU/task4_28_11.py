with open("text.txt", mode="r", encoding="utf-8") as f:
    slova = f.read().split()
    slvcnt = len(slova)
    prevslv = []
    uniquecnt = 0
    for i in slova:
        if i in prevslv:
            uniquecnt += 0
        else:
            uniquecnt += 1
            prevslv.append(i)