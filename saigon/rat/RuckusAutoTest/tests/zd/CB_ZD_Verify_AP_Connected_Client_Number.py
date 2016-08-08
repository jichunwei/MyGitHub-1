'''
by west
verify the client number in ap brief page is the same with expected
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd.aps import get_ap_brief_by_mac_addr
import libZD_TestConfig as tconfig

class CB_ZD_Verify_AP_Connected_Client_Number(Test):
    '''
    '''

    def config(self, conf):
        '''
        '''
        self._cfg_init_test_params(conf)


    def test(self):
        '''
        '''
        info = get_ap_brief_by_mac_addr(self.zd,self.ap_mac_addr)
        #@author: Jane.Guo @since: 2013-10 adapt to 9.8
        number = int(info['assoc_stas'])
        if not number==self.num_sta:
            self.errmsg= 'sta number not match,%s instead of expected %s'%(number,self.num_sta)

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
            'ap_mac':'',
            'num_sta':'1'
        }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        
        if self.conf.has_key('ap_tag') and self.conf['ap_tag']:
            active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['ap_tag'])
            self.ap_mac_addr = active_ap.base_mac_addr
        else:
            self.ap_mac_addr = self.conf['ap_mac']
        
        self.num_sta=int(self.conf['num_sta'])
        
        self.errmsg = ""
        self.passmsg = "sta nmber is %s as expected"%self.num_sta
        