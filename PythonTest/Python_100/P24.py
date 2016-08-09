#coding:utf-8
'''
    题目：有一分数序列：2/1，3/2，5/3，8/5，13/8，21/13...求出这个数列的前20项之和。
'''

def func(a,b,N):
    if N == 1:
        return float(a) / b
    else:
        a = a + b
        b = a - b
        return float(a) / b  + func(a ,b ,N-1)

    
if __name__ == "__main__":

    global a
    global b
    a = 2
    b = 1
    v = int(raw_input("Please enter an num:　"))
    # import pdb
    # pdb.set_trace()
    res = func(a,b,v)

    print "res is %r" %res

    
