#coding:utf-8
'''
    题目：求1+2!+3!+...+20!的和
'''

def func(N):
    if N == 1:
        return 1
    else:
        return N * func(N-1)



def func_1(M):
    S = 0
    for i in range(1,M):
        S += func(M)

    return S


if __name__ == "__main__":
    N = int(raw_input("Please enter an num: "))
            
    res = func_1(N)
    print "res is : %r" %res
