#coding:utf-8

import wx

'''
   Spare.py is a starting point for a wxPython program
'''

import wx

class Frame(wx.Frame):#定义一个wx.Frame的子类Frame
    pass

class App(wx.App):

    def OnInit(self):
        self.frame = Frame(parent=None, title='Spare')
        self.frame.Show()

        '''
            SetTopWindow()方法是一个可选的方法，它让wxPython方法知道哪个框架或对话框将被认为是主要的。
            一个wxPython程序可以有几个框架，其中有一个是被设计为应用程序的顶级窗口的
        '''

        self.SetTopWindow(self.frame)

        return True


'''
    # 这个是Python中通常用来测试该模块是作为程序独立运行还是被另一模块所导入。
    # 我们通过检查该模块的__name__属性来实现：
'''
if __name__ == "__main__":
    app = App()
    app.MainLoop()
