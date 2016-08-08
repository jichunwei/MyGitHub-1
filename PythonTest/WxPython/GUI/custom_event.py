# coding:utf-8

'''
    下例3.5显示了管理窗口部件的代码：
'''

import wx

'''
    关于事件类的构造器声明为wx.PyCommandEvent的一个子类
'''


class TwoButtonEvent(wx.PyCommandEvent):  # 1 定义事件
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)
        self.clickCount = 0

    def GetClickCount(self):
        return self.clickCount

    def SetClickCount(self, count):
        self.clickCount = count


'''
    全局函数wx.NewEventType()的作用类似于wx.NewId()；它返回一个唯一的事件类型ID
    这个唯一的值标识了一个应用于事件处理系统的事件类
'''
myEVT_TWO_BUTTON = wx.NewEventType()  # 创建一个事件类型

'''
    这个绑定器对象的创建使用了这个新事件类型作为一个参数。这第二个
    参数的取值位于[0,2]之间，它代表wxId标识号，该标识号用于
    wx.EvtHandler.Bind()方法去确定哪个对象是事件的源
'''
EVT_TWO_BUTTON = wx.PyEventBinder(myEVT_TWO_BUTTON, 1)  # 创建一个绑定器对象


class TwoButtonPanel(wx.Panel):
    def __init__(self, parent, id=-1, leftText='Left', rightText='Right'):
        wx.Panel.__init__(self, parent, id)
        self.leftButton = wx.Button(self, label=leftText)
        self.rightButton = wx.Button(self, label=rightText, pos=(100, 0))

        self.leftClick = False
        self.rightClick = False
        self.clickCount = 0

        # 下面两行绑定 更低级的事件
        self.leftButton.Bind(wx.EVT_LEFT_DOWN, self.OnLeftClick)
        self.rightButton.Bind(wx.EVT_LEFT_DOWN, self.OnRightClick)

    def OnLeftClick(self, event):
        self.leftClick = True
        self.OnClick()
        event.Skip()  # 5 继续处理

    def OnRightClick(self, event):
        self.rightClick = True
        self.OnClick()
        event.Skip()  # 6 继续处理

    def OnClick(self):
        self.clickCount += 1
        if self.leftClick and self.rightClick:
            self.leftClick = False
            self.rightClick = False
            evt = TwoButtonEvent(myEVT_TWO_BUTTON, self.GetId())  # 7 创建自定义事件
            evt.SetClickCount(self.clickCount)  # 添加数据到事件

            '''
                ProcessEvent()的调用将这个新事件引入到事件处理系统中,
                GetEventHandler()调用返回wx.EvtHandler的一个实例。大多数情况下，返回的实例是窗口部件对象本身，
                但是如果其它的wx.EvtHandler()方法已经被压入了事件处理器堆栈，那么返回的将是堆栈项的项目。
            '''
            self.GetEventHandler().ProcessEvent(evt)  # 8 处理事件


class CustomEventFrame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'Click Count: 0', size=(300, 100))
        panel = TwoButtonPanel(self)
        self.Bind(EVT_TWO_BUTTON, self.OnTwoClick, panel)  # 9 绑定自定义事件

    def OnTwoClick(self, event):  # 10 定义一个事件处理器函数
        self.SetTitle("Click Count: %s" % event.GetClickCount())


if __name__ == '__main__':
    app = wx.App()
    frame = CustomEventFrame(parent=None, id=-1)
    frame.Show()
    app.MainLoop()
