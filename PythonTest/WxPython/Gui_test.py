#coding:utf-8

import wx

#入门
app = wx.App()
win = wx.Frame(None, title = u'入门', size=(500,300))#窗口大小，标题
win.Move((500, 0))#窗口移动
win.Center()#窗口居中


Menu_bar = wx.MenuBar() #创建菜单栏
Menu = wx.Menu() #创建一个菜单
option_exit = Menu.Append(wx.ID_EXIT, u'退出', u'退出程序')#向菜单中添加一个选项
Menu_bar.Append(Menu, u'下拉菜单') #将创建好的菜单添加到菜单栏
win.SetMenuBar(Menu_bar) #将菜单栏添加到窗口win

# import pdb
# pdb.set_trace()
win.Bind(wx.EVT_MENU, wx.EVT_CLOSE, option_exit)#选项与动作绑定，这样点击该选项就会执行退出动作



win.Show()#显示窗口
app.MainLoop()



