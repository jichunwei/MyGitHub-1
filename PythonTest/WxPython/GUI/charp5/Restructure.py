# coding:utf-8
'''
    Optimize of "Refactor.py"
   一个公用的改进了的按钮栏方法, 对Refactor.py的重构
    "功能有待完善"
'''

import wx

# #优化一
# def createButtonBar(self, panel):
#     self.buildOneButton(panel, 'First', self.OnFirst)
#     self.buildOneButton(panel, '<< PREV', self.OnPrev, (80, 0))
#     self.buildOneButton(panel, 'NEXT >>', self.OnNext, (160, 0))
#     self.buildOneButton(panel, 'Last', self.OnLast, (240, 0))

'''
    第二优化方案，分离数据
'''


class RefactorExample(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'RefactorExample', size=(360, 200))
        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour('White')
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.createMenuBar()  # 简化的init方法
        self.createButtonBar(panel)
        self.createTextFields(panel)

    # 菜单数据
    def menuData(self):
        return (('&File',
                 ('&Open', 'Open in status bar', self.OnOpen),
                 ('&Quit', 'Quit', self.OnCloseWindow)),
                ('&Edit',
                 ('&Copy', 'Copy', self.OnCopy),
                 ('C&ut', 'Cut', self.OnCut),
                 ('&Paste', 'Paste', self.OnPaste),
                 ('', '', ''),
                 ('&Options...', 'DisplayOptions', self.OnOptions)))

    # 创建菜单栏
    def createMenuBar(self):
        menuBar = wx.MenuBar()
        for eachMenuData in self.menuData():
            menuLabel = eachMenuData[0]
            menuItems = eachMenuData[1:]
            menuBar.Append(self.createMenu(menuItems), menuLabel)
            self.SetMenuBar(menuBar)

    # 创建菜单并添加菜单选项
    def createMenu(self, menuData):
        menu = wx.Menu()
        for eachLabel, eachStatus, eachHandler in menuData:
            if not eachLabel:
                menu.AppendSeparator()
                continue
            menuItem = menu.Append(-1, eachLabel, eachStatus)
            self.Bind(wx.EVT_MENU, eachHandler, menuItem)
        return menu

    def buttonData(self):  # 按钮栏数据
        return (('First', self.OnFirst),
                ('<< PREV', self.OnPrev),
                ('NEXT >>', self.OnNext),
                ('Last', self.OnLast))

    # 创建按钮
    def createButtonBar(self, panel, yPos=0):  # 创建按钮
        xPos = 0
        for eachLabel, eachHandler in self.buttonData():
            pos = (xPos, yPos)
            button = self.buildOneButton(panel, eachLabel, eachHandler, pos)
            xPos += button.GetSize().width  # 获取按钮的宽度

    def buildOneButton(self, parent, label, handler, pos=(0, 0)):
        button = wx.Button(parent, -1, label, pos)
        self.Bind(wx.EVT_BUTTON, handler, button)
        return button

    def textFieldData(self):  # 文本数据
        return (('First Name', (10, 50)), ('Last Name', (10, 80)))

    # 创建文本
    def createTextFields(self, panel):
        for eachLabel, eachPos in self.textFieldData():
            self.createCaptionedText(panel, eachLabel, eachPos)

    def createCaptionedText(self, panel, label, pos):
        static = wx.StaticText(panel, wx.NewId(), label, pos)
        static.SetBackgroundColour('wihte')
        textPos = (pos[0] + 75, pos[1])
        wx.TextCtrl(panel, wx.NewId(), '', size=(100, -1), pos=textPos)

    # 空的事件处理器放在一起
    def OnPrev(self, event):
        pass

    def OnNext(self, event):
        pass

    def OnLast(self, event):
        pass

    def OnFirst(self, event):
        pass

    def OnOpen(self, event):
        pass

    def OnCopy(self, event):
        pass

    def OnCut(self, event):
        pass

    def OnPaste(self, event):
        pass

    def OnOptions(self, event):
        pass

    def OnCloseWindow(self, event):
        self.Destroy()


if __name__ == '__main__':
    app = wx.App()
    frame = RefactorExample(None, -1)
    frame.Show()
    app.MainLoop()
