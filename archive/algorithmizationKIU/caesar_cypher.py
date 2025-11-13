n_int = int(input("Введите n: "))
word = input("Введите слово: ")
alpha = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
for i in word:
    position = alpha.find(i)
    position = position + n_int
    position = position % 33
    print(alpha[position % 33], end = "")
    