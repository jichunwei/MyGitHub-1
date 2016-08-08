# coding:utf-8
'''
    Name: Grid02.py
    Func: Optimize of Grid.py
'''

import wx
import wx.grid


class SimpleGrid(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1)
        self.SetTable(LineupTable())  # 设置表


class TestFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'A Grid',
                          size=(275, 275))
        grid = SimpleGrid(self)


if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = wx.Frame(None)
    frame.Show(True)
    app.MainLoop()
