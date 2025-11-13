stroka = input("Введите строку: ")
glas = "ауеыоэяиёю"
soglas = "йцкнгшщзхъфвпрлджчсмтьб"
cnt_glas = 0
cnt_soglas = 0
if stroka.isalpha():
    print("Имеются цифры")
else:
    for i in stroka:
        if i in glas:
            cnt_soglas += 1
        if i in soglas:
            cnt_glas += 1
print(f"Кол-во гласных: {cnt_glas}, кол-во согласных: {cnt_soglas}. Строка: {stroka}.")