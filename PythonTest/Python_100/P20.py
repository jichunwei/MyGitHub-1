#coding:utf-8
'''
  题目：一球从100米高度自由落下，每次落地后反跳回原高度的一半；
  再落下，求它在第10次落地时，共经过多少米？第10次反弹多高？  
'''

import math

#计算总路程
def func(N):
    res = 0
    if N == 1:
        return 100
    else:
        return 100 + func(N-1)* 0.5 


#计算每次反弹的距离
def Dis(N, St = 0.5):
    if N == 1:
        return 100
    else:
        return 100 * pow(St,N)


    
if __name__ == "__main__":
    
    
    N = 10

    result = func(N)
    dis= Dis(N)
    print "Result distance is: %r" %result
    print "The  times 10 has rebound: %r " %dis
    
    
