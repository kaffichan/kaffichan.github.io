students_data = []
with open('attendance.txt', mode='r', encoding='utf-8') as file:
    for line in file:
        parts = line.strip().split(';')
        name = parts[0]
        marks = parts[1:]
        total = len(marks)
        absences = marks.count('н')
        presences = marks.count('пр')
        percent = round((presences / total) * 100, 1)
        students_data.append({
            'Имя': name,
            'Всего занятий': total,
            'Пропуски': absences,
            'Процент': percent
        })

worst_student = students_data[0]
for student in students_data:
    if student['Процент'] < worst_student['Процент']:
        worst_student = student

with open('report.txt', mode='w', encoding='utf-8') as f:
    f.write("Студент с худшей посещаемостью:\n")
    f.write(f"{worst_student['Имя']} - {worst_student['Процент']}%"
            f"({worst_student['Пропуски']} пропуск(а) из {worst_student['Всего занятий']})\n")
    f.write('\n')
    f.write("Посещаемость по студентам:\n")
    for student in students_data:
        pct_val = student['Процент']
        if pct_val.is_integer():
            pct_str = str(int(pct_val))
        else:
            pct_str = str(pct_val)
        f.write(f"{student['Имя']} - {pct_str}%\n")