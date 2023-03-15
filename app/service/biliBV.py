#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
# @Time    : 2023/1/4 2:30
# @Author  : Small tred
# @FileName: biliBV.py
# @Software: PyCharm
# @Blog    : https://www.hecady.com
table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
tr = {}
for i in range(58):
    tr[table[i]] = i
s = [11, 10, 3, 8, 4, 6]
xor = 177451812
add = 8728348608


def decode(x):
    if len(x) == 11:
        x = "BV1" + x[2:]
    r = 0
    for i in range(6):
        r += tr[x[s[i]]] * 58**i
    return (r - add) ^ xor


def encode(x):
    y = int(x)
    y = (y ^ xor) + add
    r = list('BV1  4 1 7  ')
    for i in range(6):
        r[s[i]] = table[y // 58**i % 58]
    return ''.join(r)

