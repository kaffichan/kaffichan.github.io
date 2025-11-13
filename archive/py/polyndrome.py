stroka = str(input("Введите слово или словосочетание: "))
stroka_lowr = stroka.lower().replace(' ', '')
if stroka_lowr[::-1] == stroka_lowr:
    print(f"{stroka} - является палиндромом.")
else:
    print(f"{stroka} - не является палиндромом.")