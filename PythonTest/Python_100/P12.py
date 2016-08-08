#coding:utf-8
'''
题目：古典问题：有一对兔子，从出生后第3个月起每个月都生一对兔子，
小兔子长到第三个月后每个月又生一对兔子，
假如兔子都不死，问每个月的兔子总数为多少？
'''

#递归
def fab(Month):   
    if Month <= 2:
        return 1
    else:
        return fab(Month-1) + fab(Month-2)

    
if __name__ == "__main__":
    

    value = int(raw_input("Please enter an num: "))
    print 2*fab(value)
