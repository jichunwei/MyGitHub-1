#coding:utf-8

import wx

class  win(wx.Frame):

    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'Frame With Button', size=(350,100))

        #创建画板
        panel = wx.Panel(self)
        panel.SetBackgroundColour('yellow')
        #将按钮添加到画板
        button = wx.Button(panel, label='Close', pos=(125,10), size=(50,50))
        button.SetBackgroundColour("green")
        #绑定按钮的单击事件
        self.Bind(wx.EVT_BUTTON, self.OnCloseMe, button)
        #绑定窗口的关闭事件
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)


    def OnCloseMe(self, event):
        self.Close(True)

    def OnCloseWindow(self,event):
        self.Destroy()


if __name__ == '__main__':
    app = wx.App()
    frame = win(parent=None, id=-1)
    frame.Show()
    app.MainLoop()
