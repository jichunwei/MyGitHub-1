import wx

class App(wx.App):

    def OnInit(self):
        frame = wx.Frame(parent=None, id=-1, title='Bare')
        frame.Show()
        return True


app = App()
app.MainLoop()
