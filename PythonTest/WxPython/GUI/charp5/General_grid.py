# coding:utf-8
'''
   使用lib下的genericatable来显示阵容
'''


import wx
import wx.grid
from lib import genericatable

data = (("Bob", "Dernier"), ("Ryne", "Sandberg"),
        ("Gary", "Matthews"), ("Leon", "Durham"),
        ("Keith", "Moreland"), ("Ron", "Cey"),
        ("Jody", "Davis"), ("Larry", "Bowa"),
        ("Rick", "Sutcliffe"))

colLables = ('Last', 'First')
rowLables = ('CF', '2B', 'LF', '1B', 'RF', '3B', 'C', 'SS', 'P')


class SimpleGrid(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1)
        Tabel = genericatable.GenericTable(data, rowLables, colLables)
        self.SetTable(Tabel)  # 设置表


class TestFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'A Grid', size=(300, 275))
        grid = SimpleGrid(self)


if __name__ == '__main__':
    app = wx.App(False)
    frame = TestFrame(None)
    frame.Show(True)
    app.MainLoop()
