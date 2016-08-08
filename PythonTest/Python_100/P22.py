#coding:utf-8
'''
    题目：两个乒乓球队进行比赛，各出三人。甲队为a,b,c三人，
    乙队为x,y,z三人。已抽签决定比赛名单。
    有人向队员打听比赛的名单。a说他不和x比，c说他不和x,z比，
    请编程序找出三队赛手的名单
'''

#牛叉比对
'''
将3个数进行无重复排序组合，过滤掉条件后得到的顺序（第一位不是'x',最后一位不是'x','z'
'''
for i in range(ord('x'),ord('z')+1):
    for j in range(ord('x'),ord('z')+1):
        if i != j:
            for k in range(ord('x'),ord('z') + 1):
                if (i != k) and j != k:
                    if i != ord('x') and k!=ord('x') and k!=ord('z'):
                        print 'ord is:\n a ---%s\t b ---- %s\t c---- %s\t'\
                              %(chr(i),chr(j),chr(k))
                   
