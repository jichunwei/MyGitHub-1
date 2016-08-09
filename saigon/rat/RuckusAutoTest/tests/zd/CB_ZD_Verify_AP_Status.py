'''
Description:

This function is used to verify status of AP


Created on 2012-12-31
@author: zoe.huang@ruckuswireless.com
'''

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Verify_AP_Status(Test):
    required_components = ['Zone Director', 'Active AP']
    test_parameters = {'ap_tag':'',
                       'Status':'Connected, Connected (Mesh AP, 1 hop),Connected (Root AP)',
                       'uplink_ap':'mac address'
                      }

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._verify_ap_info()
        if self.errmsg: return ('FAIL', self.errmsg)
        self.passmsg = 'Ap status is correct, status is %s, uplink is %s' % (self.status,self.uplink_ap)
        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    # Configuration
    def _init_test_parameters(self, conf):
    
        self.conf = {'ap_tag':'',
                     'status': 'Connected',
                     'uplink_ap':''}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.ap_tag = self.conf['ap_tag']
        self.active_ap = self.carrierbag[self.ap_tag]['ap_ins']
        self.ap_macaddr = self.active_ap.base_mac_addr
        self.status = self.conf['status']
        self.uplink_ap = self.conf.get('uplink_ap', None)        

        self.errmsg = ''
        self.passmsg = ''


    def _verify_ap_info(self):
        try:
            logging.info('Get ap info for AP %s' % self.ap_macaddr)
            ap_info = self.zd.get_all_ap_info(self.ap_macaddr)
            if  self.status.lower() not in ap_info['status'].lower():
                self.errmsg += 'The status of AP %s is %s instead of %s' % (self.ap_macaddr,ap_info['status'] , self.status)
    
            if 'mesh ap' in ap_info['status'].lower() and self.uplink_ap != None:
                logging.info('Begin to verify uplink of AP %s' % self.ap_macaddr)
                uplink_ap = lib.zd.aps.get_ap_detail_uplink_ap_by_mac_addr(self.zd, self.ap_macaddr)['ap']
                if str(uplink_ap)!= self.uplink_ap:
                    self.errmsg += 'The uplink of AP %s is %s instead of %s' % (self.ap_macaddr,uplink_ap, self.uplink_ap)                       
        except Exception, e:
            self.errmsg += '[Apply failed]: %s' % e.messag