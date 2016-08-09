"""
Description: This script is used to edit an exist WLAN in ZD.
Author: An Nguyen
Email: an.nguyen@ruckuswireless.com
@since: Mar 2012
"""

import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Edit_Wlan(Test):
    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._edit_wlan()        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'wlan_ssid': '',
                     'new_wlan_cfg': {},
                     'pause': 1,
                     'negative_test': False}
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
        
    def _edit_wlan(self):
        passmsg = ''
        errmsg = ''
        current_wlanlist = lib.zd.wlan.get_wlan_list(self.zd)
        if current_wlanlist == None: current_wlanlist = []
        if self.conf['wlan_ssid'] not in current_wlanlist:
            raise Exception('The WLAN %s does not exist. Please check!')
        
        logging.info('Edit the WLAN [%s] in ZD WebUI with configuration:\n%s.' % (self.conf['wlan_ssid'], 
                                                                                  self.conf['new_wlan_cfg']))
        
        try:
            lib.zd.wlan.edit_wlan(self.zd, 
                                  self.conf['wlan_ssid'],
                                  self.conf['new_wlan_cfg'],
                                  self.conf['pause'])
            passmsg = '%s is edited successfully' % self.conf['new_wlan_cfg']
            time.sleep(30)
        except Exception, e:
            errmsg = e.message
        
        if not self.conf['negative_test']:
            if errmsg:
                self.errmsg = '[Edit WLAN %s FAILED][Incorrect behavior]: %s' % (self.conf['wlan_ssid'], errmsg)
                return
            self.passmsg = '[Edit WLAN %s PASSED][Correct behavior]: %s' % (self.conf['wlan_ssid'], passmsg)
        else:
            if not errmsg:
                self.errmsg = '[Edit WLAN %s PASSED][Incorrect behavior]: %s' % (self.conf['wlan_ssid'], passmsg) 
                return
            self.passmsg = '[Edit WLAN %s FAILED][Correct behavior]: %s' % (self.conf['wlan_ssid'], errmsg)       
        
    def _update_carrier_bag(self):
        if not self.conf['negative_test']:
            if self.carrierbag.has_key(self.conf['wlan_ssid']):
                self.carrierbag[self.conf['wlan_ssid']].update(self.conf['new_wlan_cfg'])
            else:
                self.carrierbag[self.conf['wlan_ssid']]= self.conf['new_wlan_cfg']