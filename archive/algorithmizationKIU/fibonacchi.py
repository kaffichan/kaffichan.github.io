fib = int(input("Введите N: "))
prev = 0
curr = 1
while curr < fib:
    print(curr)
    prev, curr = curr, curr + prev