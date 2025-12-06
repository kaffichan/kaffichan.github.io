with open("lines.txt", mode="r", encoding="utf-8") as f:
    stroki = f.read().split('\n')
    strnum = len(stroki)
    strmax = max(stroki, key=len)
    pysearch = "python".lower()
    pytcnt = sum(pysearch in s.lower() for s in stroki)
    print(f"Всего строк: {strnum}\nСамая длинная: {strmax}\nСтрок с 'python': {pytcnt}")