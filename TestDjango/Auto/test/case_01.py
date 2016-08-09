# coding:utf-8
import xlrd
import os
import copy
from Auto.common import Env  # 必须放前面
from Auto.models import *

'''
    从表格中特定列取数据传入数据库,从RuckusAutoTest_testbed.xlsx取第2列作为Testbed表的name,
    取第8列作为conf
'''


file = 'RuckusAutoTest_testbed.xlsx'

print Testbed.objects.all()


# file_path = os.getcwd()

def open_table(file):
    data = xlrd.open_workbook(file) #get data
    table = data.sheet_by_name(u'Sheet1') #open table

    nrows = table.nrows
    nclos = table.ncols

    print nrows, nclos
    _dict = dict(
            name='',
            location='odc',
            owner='x@sina.com',
            resultdist='x@sina.com',
            config='',
            tbtype='',
    )

    _dict['tbtype'] = TestbedType.objects.get(name='ZD_Stations')

    lst = []

    for i in range(nrows):
        c1 = table.col(1)[i].value
        c7 = table.col(7)[i].value
        tbi = c7.replace('\n', '').replace('\r', '')
        _dict.update(name=c1),
        _dict.update(config=eval(tbi))
        cf = copy.deepcopy(_dict)
        lst.append(cf)

    return lst


def Insert_to_database(file=None):
    conf = open_table(file)
    for e in conf:
        rq = e['name']
        if Testbed.objects.filter(name=rq):  #如果有数据库里有这条记录
            continue
        else:
            tb = Testbed(**e)
            tb.save()


if __name__ == '__main__':
    Insert_to_database(file)
