'''
by west
enable/disable ap wlan service by mac address

'''

import logging
import types

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd.access_points_zd import set_ap_wlan_service_by_mac
import libZD_TestConfig as tconfig

class CB_ZD_Config_AP_Wlan_Service(Test):
    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        if type(self.ap_macs) is types.ListType:
            pass
        else:
            tmp = self.ap_macs
            self.ap_macs = []
            self.ap_macs.append(tmp)
            
        for ap_mac in self.ap_macs:
            logging.info('set ap [%s] radio[%s] to [%s]'%(ap_mac,self.conf['radio'],self.conf['enable']))
            set_ap_wlan_service_by_mac(self.zd, ap_mac,self.conf['radio'],self.conf['enable'])
        logging.info('set wlan service successfully')
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        #radio:'both'/'2.4'/'5.0'
        #enable:True/False
        self.conf = {'radio': 'both',
                     'enable': False}
        self.conf.update(conf)
        self.ap_macs=[]
        if self.conf.has_key('ap_tag') and self.conf['ap_tag']:
            if type(self.conf['ap_tag']) != list:
                self.conf['ap_tag'] = [self.conf['ap_tag']]
            for item in self.conf['ap_tag']:
                active_ap = tconfig.get_testbed_active_ap(self.testbed, item)
                self.ap_macs.append(active_ap.base_mac_addr)
        else:
            self.ap_macs = self.conf['ap_mac']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

            
            