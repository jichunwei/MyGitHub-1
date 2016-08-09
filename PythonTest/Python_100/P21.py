#coding:utf-8
'''
题目：猴子吃桃问题：猴子第一天摘下若干个桃子，当即吃了一半，还不过瘾，又多吃
了一个第二天早上又将剩下的桃子吃掉一半，又多吃了一个。
以后每天早上都吃了前一天剩下的一半多一个。
到第10天早上想再吃时，见只剩下一个桃子了。求第一天共摘了多少
'''

#最佳方法
def Calc_peach(N):
    if N == 1:
        return 1
    else:
        return (1 + Calc_peach(N-1)) * 2


#常规方法
def func(day):
    S = 1
    for i in range(1,day):
        S = (S + 1)*2
        
    print S


if __name__ == "__main__":

    
    N = 10

    All = Calc_peach(N)

    print "All peach: %r" %All

    day = 0
    D = 10-day
    
    func(D)
