#coding:utf-8
'''
    题目：打印楼梯，同时在楼梯上方打印两个笑脸
'''

def func():
    for i in range(4):
        print '|'
        if i == 3:
            print '|' +' '*2 +'^ ^'
            print '|' +' '*2 + ' - '

    print '--'*5
   
    lth = len('--'*5)
    for j in range(4):
        print (lth-1) * ' ' + '|'
        if j == 3:
            print (lth-1) * ' ' + '|' +' '*2 +'^ ^'
            print (lth-1) * ' ' +'|' +' '*2 + ' - '
    print ' '*lth + '--'*5
    

if __name__ == "__main__":

    func()
    
