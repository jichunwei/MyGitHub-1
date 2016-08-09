#coding:utf-8
'''
    它创建了一个有一个文本框的窗口用来显示鼠标的位置。
'''
import wx


class MyFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, "My Frame", size=(300,300))

        pannel = wx.Panel(self, -1)
        pannel.Bind(wx.EVT_MOTION, self.OnMove)
        wx.StaticText(pannel, -1, "Pos:", pos=(10,12))
        self.posCtrl = wx.TextCtrl(pannel, -1, "", pos=(40,10))


    def OnMove(self, event):
        pos = event.GetPosition()
        self.posCtrl.SetValue("%s, %s" %(pos.x, pos.y))







if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame()
    frame.Show(True)
    app.MainLoop()

