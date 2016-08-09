#coding:utf-8
'''
    xlrd 熟悉excel表格的用法
'''

import xlrd


def open_excel(file = 'file.xlsx'):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception, e:
        print str(e)


if __name__ == "__main__":

    file1 = "test.xlsx"
    file2 = "xrld.xlsx"
    #打开Excel表并读取数据
    data = open_excel(file1)

    #获取一个工作表
    table = data.sheets()[0]     #通过索引顺序获取

    # table = data.sheet_by_index(0) #通过索引顺序获取
    # table = data.sheet_by_name(u'Sheet1')#通过名称获取

    #获取行数，和列数
    nrows = table.nrows
    nclos = table.ncols

    '''
    #获取整行和整列的值（数组）
    table.row_values(1)
    table.col_values(1)
    '''

    '''
        按行来读取EXCEL表格数据
    '''
    print "--------as row output-----------"
    for i in range(nrows):
        print table.row_values(i)

    print "----------as col output-------------"
    #按列读取数据
    for j in range(nclos):
        print table.col_values(j)


    #单元格
    print "----get cell value--------"
    cell_A1 = table.cell(0, 0).value
    cell_A2 = table.cell_value(0, 3)
    cell_A3 = table.cell_value(0, 2)

    print "cell(0,2) is ", unicode(cell_A3)
    # print "cell(0, 2) is %r" % cell_A3.decode("utf-8")
    print "-------cell(0,0) is %d, cell(0, 3) is %r ----------" % (cell_A1, cell_A2)


    #使用行列索引
    cell_A4 = table.row(0)[0].value
    cell_A5 = table.row(1)[0].value

    print "cell_A4 is %d, cell_A5 is %d " % (cell_A4, cell_A5)

    #简单的写入
    row = 10
    col = 10
    #类型 0 empty, 1 string, 2 number, 3 date, 4 boolean, 5 error
    ctype = 2; value = "单元格的值"
    xf = 0 #扩展的格式化
    table.put_cell(row, col, ctype, value, xf)
    table.cell(0,0) #单元格的值
    print table.cell(0,0).value #单元格的值


