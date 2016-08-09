#coding:utf-8
'''
题目：用*号输出字母C的图案。
'''

def Output():

    s = ' '
    for i in range(8,-1,-2):
        print s*i + '*'
    print '*'
    for i in range(1,8,2):
        print s*i + '*'

if __name__ == "__main__":

    Output()
