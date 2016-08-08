#coding:utf-8
'''
    wxFrameTest.py is using  for stduy wx.Frame
'''

import wx

class Frame(wx.Frame):

    def __init__(self, parent, id, title, pos, size, style):
        '''

        :param parent: 框架的父窗口。对于顶级窗口，这个值是None。框架随其父窗口的销毁而
                        销毁。取决于平台，框架可被限制只出现在父窗口的顶部。在多文档界面的情况下，
                        子窗口被限制为只能在父窗口中移动和缩放
        :param id:关于新窗口的wxPython ID号。你可以明确地传递一个。或传递-1，这将导致
                    wxPython自动生成一个新的ID
        :param title:窗口的标题
        :param pos:一个wx.Point对象，它指定这个新窗口的左上角在屏幕中的位置。在图形用户
                     界面程序中，通常(0,0)是显示器的左上角。这个默认的(-1,-1)将让系统决定窗口的位置。
        :param size:一个wx.Size对象，它指定这个窗口的初始尺寸。这个默认的(-1,-1)将让系统决定窗口的初始尺寸。
        :param style:指定窗口的类型的常量。你可以使用或运算来组合它们。
        :param name:框架的内在的名字。以后你可以使用它来寻找这个窗口。
        :return:
        '''

        print "Frame __init__"
        wx.Frame.__init__(self, parent, id, title, pos, size,style)

# class Frame(wx.Frame):
#
#     def __init__(self, parent, id, title):
#         print "Frame __init__"
#         wx.Frame.__init__(self, parent, id, title)


if __name__ == '__main__':
    app = wx.App()
    ID = Frame.NewControlId()
    print ID

    ID1 = wx.Frame.NewControlId()
    print ID1
    # frame = Frame(parent=None, id=ID, title="My Friendly Window", pos=(200, 200), size=(400, 300),
    #               style=wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_SHAPED|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|
    #               wx.RESIZE_BORDER)
    frame = Frame(parent=None, id=ID, title="My Friendly Window", pos=(200, 200), size=(400, 300),
                  style=wx.DEFAULT_FRAME_STYLE | wx.SYSTEM_MENU ^ (wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.CLOSE_BOX))

    # frame = Frame(parent=None, id=ID, title="My Friendly Window", pos=(200, 200), size=(400, 300),
    #               style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER | wx.MINIMIZE_BOX|wx.MAXIMIZE_BOX)) #固定 窗口大小
    win = frame
    print win.GetId(), frame.GetId()
    win.Show()
    app.MainLoop()


