# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   set ap to factory default according to the ap mac address
   west
   2013.2.17
"""

import logging
import libZD_TestConfig as tconfig
from RuckusAutoTest.models import Test

class CB_ZD_AP_Set_Factory_By_MAC(Test):

    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()        
    
    def test(self):
        for active_ap in self.active_ap_list:
            ap_mac = active_ap.get_base_mac()
            logging.info("Set AP %s to factory default" % ap_mac)
            active_ap.set_factory(force_ssh = self.conf['force_ssh'])
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {'ap_mac': '',
                     'ap_tag':'',
                     'force_ssh':False}
        self.conf.update(conf)
        
        if self.conf['ap_tag']:
            self.active_ap_list = []
            active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['ap_tag'])
            self.active_ap_list.append(active_ap)
        else:
            ap_mac = self.conf['ap_mac']
            self.active_ap_list = []
            if ap_mac:
                if type(ap_mac) != list:
                    ap_mac_list = [ap_mac]
                else:
                    ap_mac_list = ap_mac
                    
                for mac in ap_mac_list:
                    self.active_ap_list.append(self.testbed.mac_to_ap[mac])
            else:
                #If no ap_tag is specified, will set all ap as specified values.
                self.active_ap_list = self.testbed.components['AP']
           
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass