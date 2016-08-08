# coding:utf-8
'''
   AddMenuBar.py is A sample frame with menubar, toolbar, and status bar
   给框架增加菜单栏、工具栏和状态栏

'''

import wx
# import images #没有这个模块
import wx.py.images


class ToolBarFrame(wx.Frame):

    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'Toolbars', size=(300, 200))
        pannel = wx.Panel(self)
        pannel.SetBackgroundColour('Yellow')
        statusBar = self.CreateStatusBar()  # 创建状态栏

        toolbar = self.CreateToolBar()  # 创建工具栏
        # 给工具栏添加一个工具
        toolbar.AddSimpleTool(wx.NewId(), wx.py.images.getPyBitmap(), 'New', "Long help for 'New'")
        toolbar.Realize() #准备显示工具栏

        menuBar = wx.MenuBar()  # 创建菜单栏
        menu1 = wx.Menu()  # 创建2个菜单
        menuBar.Append(menu1, "&File")
        menu2 = wx.Menu()
        # 创建菜单的项目
        menu2.Append(wx.NewId(), "&Copy", 'Copy in status bar')
        menu2.Append(wx.NewId(), "&Cut", '')
        menu2.Append(wx.NewId(), '&Options...', 'Display Options')

        # 在菜单栏上附上菜单
        menuBar.Append(menu2, "&Edit")

        # 在框架上附上菜单栏
        self.SetMenuBar(menuBar)


if __name__ == '__main__':
    app = wx.App()

    frame = ToolBarFrame(parent=None, id=-1)
    frame.Show()
    app.MainLoop()
