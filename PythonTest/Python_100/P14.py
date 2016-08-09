#coding:utf-8
'''
题目：将一个正整数分解质因数。例如：输入90,打印出90=2*3*3*5。
'''

import math

#费脑了
def func(var):
    while var != 1:
        for i in range(2,var+1):
            if var % i == 0:
                var = var / i
                if var == 1:
                    print '%d' %i
                    break
                else:
                    print '%d *'%i,
                    continue
                 


if __name__ == "__main__":

    lst = []
    var = int(raw_input("Please enter an num: "))
    print "%d =" %var,
    res = func(var)
    
    print "res is %r:" %res
    
