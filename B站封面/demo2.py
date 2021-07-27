a = 11


def f1():
    a = 22
    print(a)


def f2():
    global a
    print(a)

f1()
f2()