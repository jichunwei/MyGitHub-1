#coding:utf-8
'''
题目：输入一行字符，分别统计出其中英文字母、空格、数字和其它字符的个数。
'''

import string

#最科学的方法
def func(s):
    d_list =[]
    al_list = []
    els_list = []
    w_list = []
    for i in s:
        if i in string.digits:
            d_list.append(i)
        elif i in string.letters:
            al_list.append(i)
        elif i in string.whitespace:
            w_list.append(i)
        else:
            els_list.append(i)
            

    print d_list
    print al_list
    print w_list
    print els_list

    return len(d_list), len(al_list),len(w_list),len(els_list)



#比较笨的方法
def func_1(s):
    d_list = list('abcdefghijklmnoqprstuvwxyzABCDEFHIJKLMNOPQRSTUVWXYZ')
    n_list = list('0123456789')
    w_list = list(' ', '    ', '\n')

    lst_1 = []; lst_2 = []; lst_3 = []; lst_4 = []
    for i in s:
        if i in d_list:
            lst_1.append(i)
        elif i in n_list:
            lst_2.append(i)
        elif i in w_list:
            lst_3.append(i)
        else:
            lst_4.append(i)

        print lst_1
        print lst_2
        print lst_3
        print lst_4

        return len(lst_1), len(lst_2), len(lst_3), len(lst_4)




if __name__ == "__main__":

    s = 'abc4d135f fahg@@%%)()_%%'

##    import pdb
##    pdb.set_trace()
    a,b,c,d = func(s)
    print a , b ,c ,d


    print ' ---------------- '
    f1,f2,f3,f4 = func(s)
    print f1,f2,f3,f4
    
