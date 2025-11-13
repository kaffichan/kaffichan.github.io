name = input("Название товара: ")
cost = int(input("Введите цену: "))
quantity = int(input("Введите количество: "))
print(f"Вы купили {quantity} шт. \"{name}\" на сумму {cost + quantity} рублей.")