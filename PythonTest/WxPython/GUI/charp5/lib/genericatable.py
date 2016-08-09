# coding:utf-8
'''
    一个关于二维列表的通用的表
    Func: 模板文件
'''
import wx
import wx.grid


class GenericTable(wx.grid.PyGridTableBase):
    def __init__(self, data, rowLabels=None, colLabels=None):
        wx.grid.PyGridTableBase.__init__(self)
        self.data = data
        self.rowLabels = rowLabels
        self.colLabels = colLabels

    #设置行数，并填充
    def GetNumberRows(self):
        return len(self.data)
    #设置列数，并填充
    def GetNumberCols(self):
        return len(self.data[0])
    #给每列设置label
    def GetColLabelValue(self, col):
        if self.colLabels:
            return self.colLabels[col]
    #设置行号
    def GetRowLabelValue(self, row):
        if self.rowLabels:
            return self.rowLabels[row]

    def IsEmptyCell(self, row, col):
        return False
    #填充单元格
    def GetValue(self, row, col):
        return self.data[row][col]

    def SetValue(self, row, col, value):
        pass
