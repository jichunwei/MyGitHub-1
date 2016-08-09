#coding:utf-8
'''
题目：打印出所有的“水仙花数”，所谓“水仙花数”是指一个三位数，
其各位数字立方和等于该数本身。
例如：153是一个“水仙花数”，因为153=1的三次方＋5的三次方＋3的三次方。
'''

import math

def func():
    for i in range(100,1000):
        a = i / 100
        b = int(i / 10) % 10
        c = i % 10
        
        if pow(a,3) + pow(b,3) + pow(c,3) == i:
            return i




if __name__ == "__main__":
    res = func()
    print "res is: %r" %res
        
