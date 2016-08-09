#coding:utf-8

'''
    题目：一个5位数，判断它是不是回文数。即12321是回文数，个位与万位相同，十位与千位相同
'''

def Verify_f(N):
    for i in (0,3):
        if N[i] == N[-1]:
            print "%r is Palindrome number" %N
            return
        else:
            print "%r is not Palindrome number" %N
            break

if __name__ == "__main__":
    num = raw_input("Please enter a 5 position num: ")
    Verify_f(num)