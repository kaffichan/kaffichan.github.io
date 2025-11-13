s_lenght = int(input("Расстояние в км: "))
oil_lost = int(input("Расход топлива в литрах на 100 км: "))
oil_cost = int(input("Стоимость 1 литра топлива: "))
oil_final = oil_lost * s_lenght // 100
print(f"Расстояние: {s_lenght} км\nКол-во топлива туда и обратно: {oil_final * 2} литров\nСтоимость поездки: {oil_final * 2 * oil_cost}")