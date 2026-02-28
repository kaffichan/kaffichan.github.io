# matrix = [
#     [1, 2, 3],
#     [4, 5, 6],
#     [7, 8, 9]
# ]
# for line in matrix:
#     for elem in line:
#         print(elem, end=' ')
#     print()

N = int(input())
M = int(input())
matrix = [[0 for _ in range(M)] for _ in range(N)]
for line in matrix:
    for elem in line:
        print(elem, end=' ')
    print()
try:
    i = int(input())
    j = int(input())
    x = int(input())
    matrix[i][j] = x
    for line in matrix:
        print(*line)
except:
    print("Index out of range")