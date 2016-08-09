#coding:utf-8

'''
求一个3*3矩阵对角线元素之和
'''


lst = [[1,2,3],[4,5,6],[7,8,9]]

def func(lst):
    s1 = 0
    s2 = 0

    for k in range(len(lst)):
        for i in lst[k:]:
            s1 += i[k]
            break

    for k in range(len(lst)):
        for e in lst[-k:]:
            s2 += e[-k]
            break



    return s1 + s2


if __name__ == "__main__":

    res = func(lst)

    print "res is %r " %res





