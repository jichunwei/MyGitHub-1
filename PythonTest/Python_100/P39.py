#coding:utf-8
'''
题目：有一个已经排好序的数组。现输入一个数，要求按原来的规律将它插入数组中
'''


def func(st, N):
    st.append(N)
    if st[0] <= st[1]:
        return sorted(st)
    else:
        return sorted(st).reverse()


if __name__ == "__main__":

    lst = [1,2,5,3,5,1,0]
    Nst = sorted(lst)

    v  = int(raw_input("Please input an num: "))
    res = func(Nst,v)

    print "res is %r" %res





