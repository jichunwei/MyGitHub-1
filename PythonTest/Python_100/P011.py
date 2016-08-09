#coding:utf-8
'''
题目：判断101-200之间有多少个素数，并输出所有素数
'''

import math

'''
    先求非素数，再求其补集（即素数）
'''
#常规方法一
def Verify_prime():
    lst = []
    Nst = []
    for i in range(101,200):
        for j in range(2, int(math.sqrt(i))):
            if  i%j == 0:
                lst.append(i)
                break
            else:
                continue

    for i in range(101,200):
        if not i in lst:
            Nst.append(i)
             

    return Nst , len(Nst)


#常规方法二，利用标记直接输出
def func():
    count = 0
    for i in range(101,200):
        flag = 1
        for j in range(2, int(math.sqrt(i))):
            if i % j == 0:
                flag = 0
                break
            else:
                continue
        if flag == 1:
            print i,
            count += 1
        
    return count

if __name__ == "__main__":

##    import pdb
##    pdb.set_trace()
    res , count = Verify_prime()

    print  "res is \n %r " %res
    print " count is: ", count

    ct = func()
    
    print '\nct is:',ct
