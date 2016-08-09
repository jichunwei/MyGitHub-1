#coding:utf-8
'''
    Hello, wxPython!Program.
'''

import wx

class Frame(wx.Frame):
    '''Frame class that displays an image'''

    def __init__(self, image, parent=None, id=-1,
                 pos=wx.DefaultPosition, title='Hello,wxPython!'): #图像参数
        '''
        create a Frame instance and display image

        :param image:
        :param parent:
        :param id:
        :param pos:
        :param title:
        :return:
        '''
        #显示图像
        temp = image.ConvertToBitmap()

        size = temp.Getwidth(),  temp.GetHeight()
        wx.Frame.__init__(self, parent, id, title, pos, size)
        self.bmp = wx.StaticBitmap(parent=self, bitmap=temp)


class App(wx.App): #wx.App子类
    '''
        Application class
    '''

    def OnInit(self):
        #图像处理
        image = wx.Image('bd_logo1.png', wx.BITMAP_TYPE_PNG)
        self.frame = Frame(image)

        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True


def main():
    app = App()
    app.MainLoop()


if __name__ == '__main__':

    # import pdb
    # pdb.set_trace()
    main()

