#coding:utf-8
'''
题目：有5个人坐在一起，问第五个人多少岁？他说比第4个人大2岁。问第4个人岁数，他说比第3个人大2岁。
问第三个人，又说比第2人大两岁。问第2个人，说比第一个人大两岁。最后问第一个人，他说是10岁。请问第五个人多大？
'''

#递归求解
def func(N):
    if N == 1:
        return 10
    else:
        return 2 + func(N-1)

#常规方法
def func_1():

    for i in range(1,6):
        if i == 1:
            age = 10
        else:
            age += 2
    return age



if __name__ == "__main__":

    N = 5
    res = func(N)
    print "res is : %r" %res


    res_1 = func_1()
    print "res_1 is： %r" %res_1
