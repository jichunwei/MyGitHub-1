# coding:utf-8
'''
    消息对话框 & 文本对话框
'''

import wx


def Message_dilag(win):
    '''
        消息对话框
    '''
    # dlg = wx.MessageDialog(None, 'Is this the coolest thing ever!', 'MessageDiaglog', wx.YES_NO | wx.ICON_QUESTION)
    dlg = wx.MessageDialog(win, 'Is this the coolest thing ever!', 'MessageDiaglog', wx.OK | wx.CANCEL)
    result = dlg.ShowModal()
    print result
    dlg.Destroy()


def Text_enter_dilag():
    '''
        文本输入对话框
    :return:
    '''

    dlag = wx.TextEntryDialog(None, "whow is  buried in Crant's tomb", 'A Question', 'Cary Crant')
    if dlag.ShowModal() == wx.ID_OK:
        result = dlag.GetValue()
        print result


def sigle_choice_dialog():
    '''
        从一个列表中选择
    :return:
    '''

    dlg = wx.SingleChoiceDialog(None,
                                'What version of Python are you using?',
                                'Single Choice',
                                ['1.5.2', '2.0', '2.1.3', '2.2', '2.3.1'],

                                )

    if dlg.ShowModal() == wx.ID_OK:
        reponse = dlg.GetStringSelection()
        print reponse


if __name__ == '__main__':
    app = wx.App()
    win = wx.Frame(None, pos=(100, 100), size=(300, 300))
    win.Show()

    val = raw_input("Please select the dialog('M','T','S'): ")
    while True:
        if val == 'M':
            Message_dilag(win)  # 消息对话框
            break
        elif val == 'T':
            Text_enter_dilag()   # 文本输入对话框
            break
        elif val == 'S':
            sigle_choice_dialog()  # 从一个列表中选择
            break
        else:
            val = raw_input("Please select the dialog('M','T','S'): ")
    app.MainLoop()
