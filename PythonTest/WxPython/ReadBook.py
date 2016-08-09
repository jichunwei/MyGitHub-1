# coding:utf-8

'''
    模拟记事本功能实现
'''

import wx


class Frame(wx.Frame):
    def __init__(self, *args, **kwargs):
        print "Frame __init__:"
        wx.Frame.__init__(self, *args, **kwargs)
        self.conf = {
            u'文件': [u'新建', u'打开', u'保存', u'另存为', u'退出'],
            u'编辑': [u'撤销', u'剪切', u'复制', u'粘贴', u'删除', u'查找'],
            u'格式': [u'自动换行', u'字体'],
            u'查看': [u'状态栏'],
            u'帮助': [u'帮助']
        }
        self.OnInit()

    def OnInit(self):
        print "OnInit:"
        pan = wx.Panel(self)  # create pannel
        pan.SetBackgroundColour('grep')
        menuBar = wx.MenuBar()  # create menubar

        lst = []

        for i in range(0, 5):
            menu = wx.Menu()  # create menu
            menuBar.Append(menu, self.conf.keys()[i])  # add menu to menubar
            for k in self.conf.values()[i]:
                print k,
                menu.Append(wx.NewId(), k)
                lst.append(k)
                print lst
                # if k == u'退出':
                #     self.Bind(wx.EVT_MENU, self.OnQuit, k)

        self.SetMenuBar(menuBar)

        # self.Bind(wx.EVT_MENU,self.OnQuit,)

    def OnQuit(self, event):
        self.Close()


if __name__ == '__main__':
    app = wx.App(False)
    win = Frame(None, id=-1, title=u'记事本')
    win.Show()
    app.MainLoop()
