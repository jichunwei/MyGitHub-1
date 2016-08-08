'''
@author: phan.nguyen@ruckuswireless.com
@since: Apr 8, 2011
'''
import time

from pywinauto.application import Application
from pywinauto.findwindows import WindowNotFoundError
from pywinauto.findbestmatch import MatchError
from pywinauto.controls.HwndWrapper import ControlNotEnabled


class DialogHandler2(object):
    '''
    '''

    def __init__(self):
        self.app = Application()
        self.dlg = None


    def control_dialog(
            self, button_name = '', tries = 3, timeout = 1, **search_args
        ):
        '''
        '''
        if search_args.has_key('class_name') and \
        search_args['class_name'] == 'tooltips_class32':
            _title = 'ToolTips'

        if search_args.has_key('title'):
            _title = '%s' % search_args['title']

        _button = '%s' % button_name

        while tries != 0:
            try:
                self.dlg = self.app.connect_(**search_args)
                if button_name:
                    self.dlg[_title][_button].Click()
                    print 'Found dialog "%s". Clicked on its "%s" button.' % (_title, _button)

                else:
                    self.dlg[_title].Click()
                    print 'Found dialog "%s". Clicked on it directly.' % _title

                time.sleep(timeout)

            except (WindowNotFoundError, MatchError):
                break

            except ControlNotEnabled:
                continue

            except Exception, e:
                print e.message

            tries -= 1


    def install_cert(self, tries = 3, timeout = 1):
        '''
        '''
        self.done_import_cert = False

        while tries >= 0:
            self.control_dialog(
                title = 'Security Warning', class_name = '#32770',
                button_name = '&Yes'
            )

            self.control_dialog(
                title = 'Info', class_name = '#32770',
                button_name = 'OK'
            )

            self._import_cert(title = 'Certificate Import Wizard')

            self.control_dialog(
                title = 'Certificate Import Wizard', class_name = '#32770',
                button_name = 'OK'
            )

            tries -= 1

            time.sleep(timeout)


    def _import_cert(self, title, tries = 10, timeout = 1):
        '''
        '''
        while tries != 0 and not self.done_import_cert:
            try:
                self.dlg = self.app.connect_(title = title)
                self.dlg[title].Next.Click()
                print 'Found dialog "%s". Clicked on its "%s" button.' % (title, 'Next')

            except WindowNotFoundError:
                break

            except (MatchError, ControlNotEnabled):
                try:
                    self.dlg[title].Finish.Click()
                    print 'Found dialog "%s". Clicked on its "%s" button.' % (title, 'Finish')
                    self.done_import_cert = True

                except (MatchError, ControlNotEnabled):
                    tries -= 1

            except Exception, e:
                print e.message

            time.sleep(timeout)
            tries -= 1


    def _select_tooltip(self, title_re, tries = 15, timeout = 1):
        '''
        '''
        while tries != 0 and not self.done_select_tooltip:
            try:
                self.dlg = self.app.connect_(
                    class_name = 'tooltips_class32',
                    title_re = title_re,
                )
                self.dlg['ToolTips'].Click()
                print 'Found tooltips dialog. Clicked on it'
                self.done_select_tooltip = True

            except WindowNotFoundError:
                tries -= 1

            time.sleep(timeout)

#chen.tao 2014-03-07, to fix ZF-7665, change the retry times from 6 to 20
    def select_cert_xp(self, tries = 20, timeout = 0.5):
        '''
        '''
        self.done_select_tooltip = False

        while tries >= 0:
            self.control_dialog(
                title = '', class_name = '#32770',
                button_name = 'Close'
            )

            self._select_tooltip(title_re = 'Click here to process your logon information.*')

            self._select_tooltip(title_re = 'Click here to select a certificate.*', tries = 3)

            self.control_dialog(
                class_name = 'tooltips_class32',
                title_re = 'Windows was unable to find a certificate.*',
                tries = 2
            )

            self.control_dialog(
                title = 'Validate Server Certificate', class_name = '#32770',
                button_name = 'OK'
            )

            tries -= 1

            time.sleep(timeout)


    def select_cert_win7(self, tries = 6, timeout = 0.5):
        '''
        '''
        self.done_select_tooltip = False

        while tries >= 0:
            self.control_dialog(
                title = '', class_name = '#32770',
                button_name = 'Close'
            )

            self._select_tooltip(title_re = 'Click to provide additional information.*')

            self.control_dialog(
                title = 'Windows Security Alert', class_name = '#32770',
                button_name = 'Connect'
            )

            self.control_dialog(
                title = 'Select Certificate', class_name = '#32770',
                button_name = 'OK'
            )

            tries -= 1

            time.sleep(timeout)

