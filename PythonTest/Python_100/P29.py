#coding:utf-8
'''
    题目：给一个不多于5位的正整数，要求：一、求它是几位数，二、逆序打印出各位数
'''

def func(N):
    lth = len(str(N))

    for i in str(N)[::-1]:
        print int(i)



if __name__ == "__main__":

    v = raw_input("Please give an interget: ")
    lth  = len(v)
    print "It's a %r position num" %lth
    func(int(v))
