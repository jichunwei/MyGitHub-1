# coding:utf-8
from  calculator import count

#测试俩个数相加

class TestCount():

    def test_add(self):
        try:
            C = count(2, 3)
            num  = C.add()
            assert(num == 5 ), 'Integer addition result error!'
        except AssertionError as msg:             
            print msg
        else:
            print 'Test pass'

# 执行测试类的测试方法
mytest = TestCount()
mytest.test_add()