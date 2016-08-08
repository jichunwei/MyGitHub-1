# coding:utf-8
'''
    Name: grid.py
    Func: Create grid
'''

import wx
import wx.grid


class SimpleGrid(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1)
        self.CreateGrid(9, 2)
        self.SetColLabelValue(0, 'First')
        self.SetColLabelValue(1, 'Last')
        self.SetRowLabelValue(0, 'CF')
        self.SetCellValue(0, 0, "Bob")
        self.SetCellValue(0, 1, 'Dernier')
        self.SetRowLabelValue(1, '2B')
        self.SetCellValue(1, 0, 'xxx')
        self.SetCellValue(1, 1, 'yyy')
        self.SetRowLabelValue(2, '3c')
        self.SetCellValue(2, 0, 'aaa')
        self.SetCellValue(2, 1, 'bbb')






class TestFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'A Grid', size=(275, 275))
        grid = SimpleGrid(self)


if __name__ == '__main__':
    app = wx.App()
    win = TestFrame(None)
    win.Show()
    app.MainLoop()
