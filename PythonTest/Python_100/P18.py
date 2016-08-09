#coding:utf-8
'''
题目：求s=a + aa + aaa + aaaa + aa...a的值，其中a是一个数字。
例如2+22+222+2222+22222(此时，共有5个数相加)，几个数相加有键盘控制。
'''

#最佳方法
def func(a,n):
    if n == 1:
        return int(a)
    else:
        #连续个相同的数可以用int(a*n)来表示，如连续3个2,就用int(2,3)
        return int(a*n) + func(a,n-1)
    

if __name__ == "__main__":


    a , b =  raw_input("Please enter an num:　").split(',')

    n = int(b)
    import pdb
    pdb.set_trace()
    res = func(a,n)

    print "res is %r" %res
    
    
    
    
