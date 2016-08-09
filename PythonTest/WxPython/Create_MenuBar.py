#coding:utf-8

import wx


class Example(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(Example, self).__init__(*args, **kwargs)

        self.InitUI()


    def InitUI(self):

        caidanlan = wx.MenuBar()#创建菜单栏
        caidan = wx.Menu()#创建菜单
        caidan_1 = wx.Menu()

        '''
            将选项加到“菜单”里面
        '''
        xuanxiang = caidan.Append(wx.ID_EXIT, u'退出', u'退出程序')#创建菜单选项
        Edit = caidan.Append(wx.ID_EDIT, u'编辑', u'开始编辑') #添加“编辑”
        ed = caidan_1.Append(wx.ID_EDIT, u'编辑', u'开始编辑')

        caidan.SetTitle("Hello")#给下拉菜单设置“标题”
        caidan_1.SetTitle("world")
        '''
            将“菜单”加到“菜单栏”里面
        '''
        caidanlan.Append(caidan, u'文件')
        caidanlan.Append(caidan_1, u'查看')
        self.SetMenuBar(caidanlan)


        #事件绑定
        self.Bind(wx.EVT_MENU, self.OnQuit, xuanxiang)

        self.SetSize((500, 300))
        self.SetTitle(u'菜单')
        self.Show(True)


    def OnQuit(self, e):
        self.Close()



def main():

    ex = wx.App()
    Example(None)
    ex.MainLoop()


if __name__ == "__main__":
    # import pdb
    # pdb.set_trace()
    main()

