f = open('input.txt', mode='r', encoding='utf-8')
names = f.read()
r = open('output.txt', mode='a', encoding='utf-8')
lst = names.split('\n')
cnt = 0
for i in lst:
    cnt += 1
    if i[-1].lower() in 'ая':
        r.write(str(cnt) + '\n')
f.close()
r.close()