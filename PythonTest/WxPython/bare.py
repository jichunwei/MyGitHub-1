#coding:utf-8

import wx

'''
    创建最小的空的wxpython程序
'''

import wx

class App(wx.App):

    def OnInit(self):
        frame = wx.Frame(parent=None, title='Bare')#创建了一个wx.Frame类的实例
        frame.Show()
        return True


app = App()
app.MainLoop()