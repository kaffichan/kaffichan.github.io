sentence = str(input("Введите предложение: "))
for i in sentence:
    sentence.find(i)
    if i == " ":
        position = i
        sentence.replace(" ", "", 1)