ticket = int(input("Введите шестизначный номер билета: "))
left_tick = 0
right_tick = 0
for i in range(3):
    right_tick += ticket % 10
    ticket //= 10
for i in range(3):
    left_tick += ticket % 10
    ticket //= 10
if right_tick == left_tick:
    print("Билет счастливый")
else:
    print("Билет не счастливый")