def summa(data):
    # проверяем длину списка, если несоотвествие возвращаем "error"
    if len(data) != 4:
        return "error"
    
    # если возникнет исключение, код прерывается и передаётся блоку except
    try:
        # присваиваем элементы списка переменным
        a, b, c, d = data
        
        # вычисление формулы (a + bi) + (c + di) = (a + c) + (b + d)i
        return [float(a + c), float(b + d)]
    except Exception:
        # если возникла ошибка, возвращаем строку "error"
        return "error"

def raznost(data):
    if len(data) != 4:
        return "error"
    
    try:
        a, b, c, d = data
        
        # вычисление формулы (a + bi) - (c + di) = (a - c) + (b - d)i
        return [float(a - c), float(b - d)]
    except Exception:
        return "error"

def multi(data):
    if len(data) != 4:
        return "error"
    
    try:
        a, b, c, d = data
        
        # происходит вычисление действительного и мнимого числа по формуле
        # (a + bi) * (c + di) = (ac - bd) + (ad + bc)i
        real_mult = (a * c) - (b * d)
        imag_mult = (a * d) + (b * c)
        
        return [float(real_mult), float(imag_mult)]
    except Exception:
        return "error"

def divide(data):
    if len(data) != 4:
        return "error"
    
    try:
        a, b, c, d = data
        
        # делитель
        denominator = (c**2) + (d**2)
        
        # на 0 делить нельзя
        if denominator == 0:
            return "error"
        
        # вычисление деления по формуле
        # (a + bi) / (c + di)
        real_div = ((a * c) + (b * d)) / denominator
        imag_div = ((b * c) - (a * d)) / denominator
        
        return [round(real_div, 4), round(imag_div, 4)]
    except Exception:
        return "error"