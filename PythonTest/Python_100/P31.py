#coding:utf-8

'''
    题目：请输入星期几的第一个字母来判断一下是星期几，如果第一个字母一样，则继续判断第二个字母
'''



lst = ['Monday', 'Tuseday', 'Wensday','Thursday','Friday','Saturday', 'Sunday']

def Verify_week(c):
    count = 0
    Nst = []
    lst_1 = []
    lst_2 = []
    for i in lst:
        lst_1.append(i[0])
        lst_2 = set(lst_1)

    print lst_2

    if c not in lst_2:
        print "Please enter another num in '%r' " %lst_2
        c = raw_input("Please enter a right char: ")

    for i in lst:
        if i.startswith(c):
            count += 1
            Nst.append(i)


    if  count == 1:
            print "Today is %r" %Nst
            Nst = []
    else:
        ch = raw_input("Plesae enter the seconde char: ")
        for i in Nst:
            if ch == i[1]:
                print "Today is %r" %i


if __name__ == "__main__":

    c = raw_input("Please enter a char: ")


    # import pdb
    # pdb.set_trace()
    Verify_week(c)

