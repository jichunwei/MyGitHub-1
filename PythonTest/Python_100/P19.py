#coding:utf-8
'''
题目：一个数如果恰好等于它的因子之和，这个数就称为“完数”。
例如6=1＋2＋3。编程找出1000以内的所有完数
'''

import math

#
def func():
    lst = []
    lst_1 = []
    for i in range(2,1000):
        for k in range(2, i+1):
            if  i % k == 0:
                if i != k:
                    lst.append(k)
                #遍历完整个因子列表后，对其求和
                else:
                    if i == sum(lst) + 1:
                        lst_1.append(i)
                    lst = []
                    break
                continue

    return lst_1
      
       
  
if __name__ == "__main__":

##    import pdb
##    pdb.set_trace()

    Nst = func()
    print "All the numbers are: %r" %Nst
