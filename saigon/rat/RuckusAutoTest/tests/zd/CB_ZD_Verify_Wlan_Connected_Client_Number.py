'''
by west
verify the client number in wlan brief page is the same with expected
'''
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd.wlan_zd import get_wlan_brief_by_name

class CB_ZD_Verify_Wlan_Connected_Client_Number(Test):
    '''
    '''

    def config(self, conf):
        '''
        '''
        self._cfg_init_test_params(conf)


    def test(self):
        '''
        '''
        info = get_wlan_brief_by_name(self.zd,self.wlan)
        #@author: Jane.Guo @since: 2013-10 adapt to 9.8
        number = int(info['assoc_stas'])
        if not str(number)==str(self.num_sta):
            self.errmsg('sta number not match,%s instead of expected %s'%(number,self.num_sta))

        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)

        logging.debug(self.passmsg)
        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        '''
        '''


    def _cfg_init_test_params(self, conf):
        '''
        '''
        self.conf = {
            'wlan_name':'',
            'num_sta':'1'
        }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.wlan = self.conf['wlan_name']
        self.num_sta=int(self.conf['num_sta'])
        
        self.errmsg = ""
        self.passmsg = "sta nmber is %s as expected"%self.num_sta
        