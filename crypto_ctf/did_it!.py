from pwn import *

n = 127
l = 20

def sortFunction(v):
    return v['pain']
sqrs = sorted([{'num': x, 'pain':pow(x, 2, n)} for x in range(n-1)], key=sortFunction)
norm = [x['num'] for x in sqrs]
mods = [x['pain'] for x in sqrs]
print(norm)
print(mods)

c = remote('00.cr.yp.toc.tf', 11337)
c.recv()

def pain(num, lis):
    li = []
    for x in lis:
        if num == x or num + 1 == x:
            li.append(x)
        if x > num + 1:
            break
    return li


A = [x for x in range(l)]
known = []
poss = []
while True:
    c.sendline((str(A)[1:-1]).encode())
    rec = c.recvline().decode()
    print(rec)
    lis = [int(al) for al in rec.split('=')[-1].strip().strip('][').split(', ')]
    Asqrs = [pow(x, 2, n) for x in A]
    for x in Asqrs:
        if x not in lis or x + 1 not in lis:
            known.append(x)
        else:
            poss.append(pain(x, lis))