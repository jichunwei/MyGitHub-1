# coding:utf-8
'''
    Spare.py is a starting point for a wxPython program.
'''
import wx


class Frame(wx.Frame):
    pass


class App(wx.App):
    def OnPreInit(self):
        self.frame = Frame(parent=None, title='Spare')
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True


if __name__ == "__main__":
    app = App()
    app.MainLoop()
