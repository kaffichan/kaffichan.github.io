# class Students:
#     univer = 'KIU'
#     def __init__(self, fio, group, marks):
#         self.fio = fio
#         self.group = group
#         self.marks = marks
    
#     def print_info(self):
#         print(f"Студент {self.fio}, группа {self.group}, успеваемость {self.marks}")

# ivanov = Students("Иванов Иван Иванович", "1051", "4")
# petrov = Students("Петров Петр Петрович", "955", "5")

# ivanov.print_info()
# petrov.print_info()

# Создать справочник автомобилей. Для каждого авто хранить: название, год выпуска, 
# максимальная скорость. Реализовать метод print_info(), который выводит информацию 
# о каком-либо авто, и реализовать метод max_speed(), который находит автомобиль с макс. 
# скоростью из списка.

# class Car:
#     def __init__(self, name, year, speed):
#         self.name = name
#         self.year = year
#         self.speed = speed

#     def print_info(self):
#         print(f"Модель: {self.name:15} | Год: {self.year} | Макс. скорость: {self.speed} км/ч.")

# def find_mspeed(car_list):
#     if not car_list:
#         return None
#     return max(car_list, key=lambda car: car.speed)

# catalog = [
#     Car("Toyota Supra", 2020, 250),
#     Car("Bugatti Chiron", 2022, 420),
#     Car("Lada Vesta", 2023, 180),
#     Car("Ferrari F8", 2021, 340)
# ]

# print("Справочник авто")
# for car in catalog:
#     car.print_info()

# print("\nПоиск самого быстрого авто")
# fastest_car = find_mspeed(catalog)

# if fastest_car:
#     print("Самая быстрая машина:")
#     fastest_car.print_info()


# class Transport:
#     def __init__(self, cartype, max_speed, dist):
#         self.cartype = cartype
#         self.max_speed = max_speed
#         self.dist = dist

#     def print_info(self):
#         print(f"Тип: {self.cartype}\nМакс. скорость: {self.max_speed}\nЗапас хода: {self.dist}\n--- --- --- --- ---")

# class Ecar(Transport):
#     def __init__(self, cartype, max_speed, dist, battery):
#         super().__init__(cartype, max_speed, dist)
#         self.battery = battery

# car = Transport('Легковая', 200, 600)
# ecar = Ecar('Электричка', 300, 400, '70кВч')
# car.print_info()
# ecar.print_info()

class Animal:
    def __init__(self, name, sound):
        self.name = name
        self.sound = sound

    def speak(self):
        return print(f"{self.name} говорит {self.sound}")
    
class Dog(Animal):
    def __init__(self, name):
        super().__init__(name, sound="гав")

class Cat(Animal):
    def __init__(self, name):
        super().__init__(name, sound="мяу")

cat1 = Cat("Маруся")
cat2 = Cat("Кот")
dog1 = Dog("Тоби")
dog2 = Dog("Фокс")

cat1.speak()
cat2.speak()
dog1.speak()
dog2.speak()