data = [5, 2, 9, 1, 5, 6]
for i in data in range(5):
    if i[i] > i[i + 1]:
        i[i], i[i + 1] = i[i + 1], i[i]
print(data)