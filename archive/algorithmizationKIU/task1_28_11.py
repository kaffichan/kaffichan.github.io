with open("numbers.txt", mode="r", encoding="utf-8") as f:
    stroka = f.read().split()
    intstr = [int(x) for x in stroka]
    total = sum(intstr)
    print(total)