'''
Created on Jan 20, 2011
@author: louis.lou@ruckuswireless.com
description:

'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import wlan_zd

from RuckusAutoTest.components import Helper_ZD as zhlp


class CB_ZD_Get_Wlans_Info(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
       
        self.wlan_info_gui_get = wlan_zd.get_wlan_conf_detail(self.zd, self.wlan_name)
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)
    
    
    def cleanup(self):
        pass

     

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = dict(
                         wlan_name = '',
                         )
        
        self.conf.update(conf)
                
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
    def  _retrive_carrier_bag(self):
        if self.conf['wlan_name']:
            self.wlan_name = self.conf['wlan_name']
            
        elif self.carrierbag.has_key('wlan_name'):
            self.wlan_name = self.carrierbag['wlan_name']
             
    def _update_carrier_bag(self):
        self.carrierbag['wlan_info_gui_get'] = self.wlan_info_gui_get         