#coding:utf-8
'''
    求100以内的素数
'''


def func():
    for i in range(2,100):
        flag = 1
        for k in range(2,100):
            if i % k == 0:
                if i / k != 1:
                    flag = 0

        if  flag:
            print i,


if __name__ == "__main__":

    func()