def _validate_input(data):
    # Вспомогательная функция для проверки входных данных.
    # Проверяет, что:
    # 1. data является списком.
    # 2. Длина списка равна 4.
    # 3. Все элементы списка являются числами (int или float).
    if not isinstance(data, list):
        return False
    
    if len(data) != 4:
        return False
    
    for item in data:
        # Эта проверка гарантирует, что элементы - это числа,
        # а не строки (даже если они выглядят как числа, '1.5')
        if not isinstance(item, (int, float)):
            return False
            
    return True

def summa(data):
    # Вычисляет сумму двух комплексных чисел.
    # Вход: [a, b, c, d] для (a + bi) + (c + di)
    # Возвращает: [real_sum, imag_sum] или "error"
    if not _validate_input(data):
        return "error"
    
    try:
        a, b, c, d = data
        
        # (a + bi) + (c + di) = (a + c) + (b + d)i
        real_sum = a + c
        imag_sum = b + d
        
        # Возвращаем float, как того требуют тесты
        return [float(real_sum), float(imag_sum)]
    except Exception:
        return "error"

def raznost(data):
    # Вычисляет разность двух комплексных чисел.
    # Вход: [a, b, c, d] для (a + bi) - (c + di)
    # Возвращает: [real_diff, imag_diff] или "error"
    if not _validate_input(data):
        return "error"
    
    try:
        a, b, c, d = data
        
        # (a + bi) - (c + di) = (a - c) + (b - d)i
        real_diff = a - c
        imag_diff = b - d
        
        return [float(real_diff), float(imag_diff)]
    except Exception:
        return "error"

def multi(data):
    # Вычисляет произведение двух комплексных чисел.
    # Вход: [a, b, c, d] для (a + bi) * (c + di)
    # Возвращает: [real_mult, imag_mult] или "error"
    if not _validate_input(data):
        return "error"
    
    try:
        a, b, c, d = data
        
        # (a + bi) * (c + di) = (ac - bd) + (ad + bc)i
        real_mult = (a * c) - (b * d)
        imag_mult = (a * d) + (b * c)
        
        return [float(real_mult), float(imag_mult)]
    except Exception:
        return "error"

def divide(data):
    # Вычисляет частное двух комплексных чисел.
    # Вход: [a, b, c, d] для (a + bi) / (c + di)
    # Возвращает: [real_div, imag_div] или "error"
    if not _validate_input(data):
        return "error"
    
    try:
        a, b, c, d = data
        
        # Знаменатель: c^2 + d^2
        denominator = (c**2) + (d**2)
        
        # Проверка деления на ноль (когда c=0 и d=0)
        if denominator == 0:
            return "error"
        
        # (a + bi) / (c + di) = (ac + bd)/(c^2 + d^2) + (bc - ad)/(c^2 + d^2)i
        real_div = ((a * c) + (b * d)) / denominator
        imag_div = ((b * c) - (a * d)) / denominator
        
        return [round(real_div, 4), round(imag_div, 4)]
    except Exception:
        return "error"