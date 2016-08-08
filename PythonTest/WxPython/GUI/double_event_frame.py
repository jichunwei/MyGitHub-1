# coding:utf-8
'''
    同时响应鼠标按下和按钮敲击
'''

import wx


class DoubleEventFrame(wx.Frame):
    def __init__(self, parent, id):
        print "DoubleEventFrame __init__:"
        wx.Frame.__init__(self, parent, id, 'Frame With Button', size=(300, 100))

        self.pannel = wx.Panel(self, -1)
        self.button = wx.Button(self.pannel, -1, 'Click Me', pos=(100, 15))
        self.Bind(wx.EVT_BUTTON, self.OnButtonClick, self.button)  # 绑定按钮敲击事件
        self.button.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDwon)  # 绑定鼠标左键按下事件

    def OnButtonClick(self, event):
        self.pannel.SetBackgroundColour('Green')
        self.button.SetBackgroundColour('red')
        self.pannel.Refresh()

    def OnMouseDwon(self, event):
        self.button.SetLabel('Again!')
        event.Skip()


if __name__ == '__main__':
    app = wx.App(redirect=False)
    win = DoubleEventFrame(parent=None, id=-1)
    win.Show()
    app.MainLoop()
