#coding:utf-8
'''
题目：输出9*9口诀表。
'''



def Print_table():
    for i in range(1,10):
        for j in range(1,i+1):
            v = i * j
            print i,
            print '*',
            print "%-1d" %j,
            print '=',
            print "%-4d" % v,   
            if i == j:
                print '\n'



if __name__ == "__main__":

    Print_table()
    
