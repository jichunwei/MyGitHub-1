#coding:utf-8
'''
题目：利用条件运算符的嵌套来完成此题：
学习成绩>=90分的同学用A表示，60-89分之间的用B表示，60分以下的用C表示
'''

def func(grade):
    
    if grade >=90:
        flag = 'A'
    if 60 <= grade <=89:
        flag = 'B'
    if grade < 60:
        flag = 'C'

    return flag


if __name__ == "__main__":

    value = int(raw_input("Please enter the grade:(0-100) "))

    res = func(value)

    print "res is %r:" %res
    
