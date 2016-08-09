'''
Created on 2014-11-10
@author: chen.tao@odc-ruckuswireless.com
'''
import time
import logging
import win32gui
import win32api
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import redundancy_zd
class CB_Answer_Smart_Redundancy_Pool_Choice(Test):

    def config(self,conf):
        self._init_test_params(conf)

    def test(self):
        try:
            share_secret = self.conf['share_secret']
            redundancy_zd.sync_with_peer(self.zd1,'from')#chen.tao 2015-01-06, to fix script bug ZF-11482 
            redundancy_zd.enable_single_smart_redundancy_only(self.zd2,self.zd1.ip_addr,share_secret)
            self.zd1.refresh()
            res = self.answer_srp_choice()
            if self.choice == 'OK':
                redundancy_zd.sync_with_peer(self.zd2,'from')
        except Exception, ex: 
            self.errmsg = ex.message
        if not res:
            self.errmsg += 'No expected pop-up confirmations are found'
        else:
            self.passmsg = 'Found pop-up confirmation %s times, answered %s successfully!'%(res, self.choice)

        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = {'zd_tag':'',
                     'choice':'OK',#OK or Cancel
                     'share_secret':'testing',
                     'timeout':60
                     }
        self.conf.update(conf)
        self.choice = self.conf['choice']
        if self.conf['zd_tag'] == 'active_zd':
            self.zd1 = self.carrierbag['active_zd']
            self.zd2 = self.carrierbag['standby_zd']
        else:
            self.zd2 = self.carrierbag['active_zd']
            self.zd1 = self.carrierbag['standby_zd']
    def answer_srp_choice(self):
        st = time.time()
        confirm_windows = []
        while time.time() - st < self.conf['timeout']:
            handle = win32gui.FindWindow("MozillaDialogClass",None)
            if handle:
                if handle not in confirm_windows:
                    confirm_windows.append(handle)
                if self.choice == 'OK':
                    self.select_OK(handle)
                else:
                    self.select_Cancel(handle)
                    
        return len(confirm_windows)

    def select_OK(self,handle):
        try:
            win32gui.SetForegroundWindow(handle)
            win32api.keybd_event(13,0)
        except:
            pass

    def select_Cancel(self,handle):
        try:
            win32gui.SetForegroundWindow(handle)
            win32api.keybd_event(27,0)
        except:
            pass