def _is_valid(mat):
    if not isinstance(mat, list) or not mat:
        return False
    
    # Проверка, что первая строка — это список
    if not isinstance(mat[0], list) or not mat[0]:
        return False
        
    cols = len(mat[0])
    for row in mat:
        if not isinstance(row, list) or len(row) != cols:
            return False
        for elem in row:
            # Проверяем, что элемент — число (int или float), но не bool
            if not isinstance(elem, (int, float)) or isinstance(elem, bool):
                return False
    return True

def summa(mat1, mat2):
    if not _is_valid(mat1) or not _is_valid(mat2):
        return 'error'
    if len(mat1) != len(mat2) or len(mat1[0]) != len(mat2[0]):
        return 'error'
    
    res = []
    for i in range(len(mat1)):
        row = [mat1[i][j] + mat2[i][j] for j in range(len(mat1[0]))]
        res.append(row)
    return res

def mul(mat1, mat2):
    if not _is_valid(mat1) or not _is_valid(mat2):
        return 'error'
    if len(mat1[0]) != len(mat2):
        return 'error'
    
    rows_a, cols_a = len(mat1), len(mat1[0])
    cols_b = len(mat2[0])
    
    res = [[0 for _ in range(cols_b)] for _ in range(rows_a)]
    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                res[i][j] += mat1[i][k] * mat2[k][j]
    return res

def transp(mat1):
    if not _is_valid(mat1):
        return 'error'
    return [[mat1[j][i] for j in range(len(mat1))] for i in range(len(mat1[0]))]

def det(mat1):
    if not _is_valid(mat1) or len(mat1) != len(mat1[0]):
        return 'error'
    
    # Копия для работы (метод Гаусса)
    n = len(mat1)
    a = [row[:] for row in mat1]
    res = 1.0
    
    for i in range(n):
        pivot = i
        for j in range(i + 1, n):
            if abs(a[j][i]) > abs(a[pivot][i]):
                pivot = j
        a[i], a[pivot] = a[pivot], a[i]
        if pivot != i:
            res *= -1
            
        if abs(a[i][i]) < 1e-12:
            return 0.0
            
        res *= a[i][i]
        for j in range(i + 1, n):
            factor = a[j][i] / a[i][i]
            for k in range(i + 1, n):
                a[j][k] -= factor * a[i][k]
    return round(res, 10) # Округление для избавления от шума float

def _get_inverse(matrix):
    n = len(matrix)
    # Создаем расширенную матрицу [A | I]
    aug = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(matrix)]
    
    for i in range(n):
        pivot = i
        for j in range(i + 1, n):
            if abs(aug[j][i]) > abs(aug[pivot][i]):
                pivot = j
        aug[i], aug[pivot] = aug[pivot], aug[i]
        
        if abs(aug[i][i]) < 1e-12:
            return None # Матрица вырожденная
            
        div = aug[i][i]
        for j in range(i, 2 * n):
            aug[i][j] /= div
            
        for j in range(n):
            if i != j:
                factor = aug[j][i]
                for k in range(i, 2 * n):
                    aug[j][k] -= factor * aug[i][k]
                    
    return [row[n:] for row in aug]

def diff(mat1, mat2):
    if not _is_valid(mat1) or not _is_valid(mat2):
        return 'error'
    if len(mat2) != len(mat2[0]): # Делитель должен быть квадратным
        return 'error'
    
    inv_mat2 = _get_inverse(mat2)
    if inv_mat2 is None:
        return 'error'
    
    res = mul(mat1, inv_mat2)
    if res == 'error':
        return 'error'
        
    # Округление результата до 2 знаков
    return [[round(elem, 2) for elem in row] for row in res]

def rank(mat1):
    if not _is_valid(mat1):
        return 'error'
    
    n = len(mat1)
    m = len(mat1[0])
    a = [row[:] for row in mat1]
    rank_val = 0
    
    selected_row = [False] * n
    for j in range(m):
        pivot = -1
        for i in range(n):
            if not selected_row[i] and abs(a[i][j]) > 1e-12:
                pivot = i
                break
        
        if pivot != -1:
            rank_val += 1
            selected_row[pivot] = True
            for i in range(n):
                if i != pivot:
                    factor = a[i][j] / a[pivot][j]
                    for k in range(j, m):
                        a[i][k] -= factor * a[pivot][k]
    return rank_val

def L1(mat1):
    if not _is_valid(mat1):
        return 'error'
    
    max_sum = 0
    for row in mat1:
        current_row_sum = sum(abs(elem) for elem in row)
        if current_row_sum > max_sum:
            max_sum = current_row_sum
            
    return max_sum

def L0(mat1):
    if not _is_valid(mat1):
        return 'error'
    
    count = 0
    for row in mat1:
        for elem in row:
            if elem != 0:
                count += 1
    return count