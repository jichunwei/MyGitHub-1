#coding:utf-8

'''
    题目：利用递归函数调用方式，将所输入的5个字符，以相反顺序打印出来
'''


def output(N,l):
    if l == 0:
        return
    else:
        print N[l-1]
        return output(N,l-1)


if __name__ == "__main__":

    s = raw_input("Please enter a string: ")

    lth = len(s)
    output(s,lth)