# coding:utf-8

import wx
from lib import abstractModel


class SimpleName(abstractModel.AbstractModel):
    def __init__(self, first='', last=''):
        abstractModel.AbstractModel.__init__(self)
        self.set(first, last)

    def set(self, first, last):
        self.first = first
        self.last = last
        self.update()  # 1 更新


class ModelExample(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'Flintstone', size=(360, 200))
        panel = wx.Panel(self)
        panel.SetBackgroundColour('White')
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.textFields = {}
        self.createTextFields(panel)

        # -------------------------------
        # 2 创建模型
        self.model = SimpleName()
        self.model.addListener(self.OnUpdate)
        # -------------------------------
        self.createButtonBar(panel)

    def buttonData(self):
        data = (('Fredify', self.OnFred),
                ('Wilmafy', self.OnWilma),
                ('Barnify', self.OnBarney),
                ('Bettify', self.OnBetty))
        return data

    def createButtonBar(self, panel, yPos=0):
        xPos = 0
        for eachLabel, eachHandler in self.buttonData():
            pos = (xPos, yPos)

            button = self.buildOneButton(panel, eachLabel, eachHandler, pos)
            xPos += button.GetSize().width

    def buildOneButton(self, parent, label, handler, pos=(0, 0)):
        button = wx.Button(parent, -1, label, pos)
        self.Bind(wx.EVT_BUTTON, handler, button)
        return button

    def textFieldData(self):
        data = (('FirstName', (10, 50)),
                ('LastName', (10, 80)))
        return data

    def createTextFields(self, panel):
        for eachLabel, eachPos in self.textFieldData():
            self.createCaptionedText(panel, eachLabel, eachPos)

    def createCaptionedText(self, panel, label, pos):
        static = wx.StaticText(panel, wx.NewId(), label, pos)
        static.SetBackgroundColour('White')
        textPos = (pos[0] + 75, pos[1])
        self.textFields[label] = wx.TextCtrl(panel, wx.NewId(), '', size=(100, -1), pos=textPos, style=wx.TE_READONLY)

    def OnUpdate(self, model):  # 3 设置文本域
        self.textFields['FirstName'].SetValue(model.first)
        self.textFields['LastName'].SetValue(model.last)

    # -------------------------------------------
    # 4 响应按钮敲击的处理器
    def OnFred(self, event):
        self.model.set('Fred', 'Flintston')

    def OnBarney(self, event):
        self.model.set('Barney', 'Rubble')

    def OnWilma(self, event):
        self.model.set('Wilma', 'Flintstone')

    def OnBetty(self, event):
        self.model.set('Betty', 'Rubble')

    # ---------------------------------------------
    def OnCloseWindow(self, event):
        self.Destroy()


if __name__ == '__main__':
    app = wx.App(False)
    frame = ModelExample(parent=None, id=-1)
    frame.Show()
    app.MainLoop()
