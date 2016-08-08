# coding:utf-8
'''
    一个较差的能够读任何二维Python列表的表
'''
import wx
import wx.grid


class LineupTable(wx.grid.PyGridTableBase):
    data = (("Bob", "Dernier"), ("Ryne", "Sandberg"),
            ("Gary", "Matthews"), ("Leon", "Durham"),
            ("Keith", "Moreland"), ("Ron", "Cey"),
            ("Jody", "Davis"), ("Larry", "Bowa"),
            ("Rick", "Sutcliffe"))

    colLabels = ('Last', 'First')

    def __init__(self):
        wx.grid.PyGridTableBase.__init__(self)

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.data[0]) - 1

    def GetColLabelValue(self, col):
        val = self.colLabels[col]
        print val
        return val

    def GetRowLabelValue(self, row):
        dat = self.data[row][0]
        print dat
        return dat

    def IsEmptyCell(self, row, col):
        return False

    def GetValue(self, row, col):
        return self.data[row][col + 1]

    def SetValue(self, row, col, value):
        pass


class SimpleGrid(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1)
        Table = LineupTable()
        self.SetTable(Table)  # 设置表


class TestFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'A Grid', size=(300, 275))
        grid = SimpleGrid(self)


if __name__ == '__main__':
    app = wx.App(False)
    frame = TestFrame(None)
    frame.Show(True)
    app.MainLoop()
