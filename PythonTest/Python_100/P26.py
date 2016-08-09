#coding:utf-8
'''
题目：利用递归方法求5!
'''

def func(N):
    if N == 1:
        return 1
    else:
        return N * func(N-1)



if __name__ == "__main__":

    N = int(raw_input("Please enter an num: "))
            
    res = func(N)

    print "res is : %r" %res
            
