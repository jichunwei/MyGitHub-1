# coding:utf-8
'''
    绑定多个鼠标事件
'''

import wx


class MouseEventFrame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'Frame with Button', size=(300, 100))

        self.pannel = wx.Panel(self)
        self.button = wx.Button(self.pannel, label="Not over", pos=(100, 15))

        self.Bind(wx.EVT_BUTTON, self.OnButtonClick, self.button)  # 绑定按钮事件
        self.button.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)  # 绑定鼠标位于其上事件
        self.button.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)  # 绑定鼠标离开事件

    def OnButtonClick(self, event):
        self.pannel.SetBackgroundColour('Green')
        self.pannel.Refresh()

    def OnEnterWindow(self, event):
        self.button.SetLabel("Over Me!")
        event.Skip()

    def OnLeaveWindow(self, event):
        self.button.SetLabel("Not Over")
        event.Skip()


if __name__ == '__main__':
    app = wx.App()
    win = MouseEventFrame(parent=None, id=-1)
    win.Show()
    app.MainLoop()
