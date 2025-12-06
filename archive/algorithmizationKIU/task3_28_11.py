with open("data.txt", mode="r", encoding="utf-8") as f:
    adult = []
    minors = []
    for line in f:
        name, agestr = line.strip().split()
        age = int(agestr)
        if age >= 18:
            adult.append(f"{name} {age}")
        else:
            minors.append(f"{name} {age}")
with open("minors.txt", mode="w", encoding="utf-8") as f:
    for minor in minors:
        f.write(minor + "\n")