n = 10
a = 0
b = 1

for i in range(1, n):
    c = a + b
    a = b
    b = c

print(c)