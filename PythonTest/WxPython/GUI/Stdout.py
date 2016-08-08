#coding:utf-8

'''
    重定向输出到 wxPython 框架
'''

import wx
import sys

#自定义框架
class Frame(wx.Frame):

    def __init__(self, parent, id, title):
        print "Frame __init__"
        wx.Frame.__init__(self, parent, id, title)

#应用程序
class App(wx.App):

    def __init__(self, redirect=True, filename=None):
        print "App __init__"
        wx.App.__init__(self, redirect, filename)

    def OnInit(self): #wxPython自动调用
        print "OnInit" #输出到stdout
        self.frame = Frame(parent=None, id=-1, title='Startup') #创建框架
        self.frame.Show()
        self.SetTopWindow(self.frame)
        print  >>sys.stderr, "A pretend error message"  #输出到stderr

        self.func()

        return True
    def func(self):
        print "Hello Tan!"

    def  OnExit(self):
        print "OnExit"

def  main():
    #Application object created
    app  = App(redirect=True) #文本重定向从这开始
    # app = App(False) #消息在控制台输出
    # app = App(True, "output.txt") #消息重定向到output.txt中
    print "before MainLoop"
    app.MainLoop() #进入主事件循环
    print "after MainLoop"


if __name__ == "__main__":
    main()
