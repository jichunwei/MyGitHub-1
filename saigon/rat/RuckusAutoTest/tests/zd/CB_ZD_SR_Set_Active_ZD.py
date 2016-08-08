#import os
#import re
#import time
#import logging

from RuckusAutoTest.models import Test
#from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components.lib.zd import redundancy_zd as red
#from RuckusAutoTest.components import Helper_ZD as zhlp
from RuckusAutoTest.common import lib_Debug as bugme

class CB_ZD_SR_Set_Active_ZD(Test):
    
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
        if self.active_zd != self.new_active_zd:
            self.is_failover = True
            
            #Failover active zd.
            red.failover(self.active_zd)
            
            #self.new_active_zd = self.standby_zd
            self.new_standby_zd = self.active_zd
            if self.carrierbag.has_key('standby_zd_cli') and self.carrierbag.has_key('active_zd_cli'):
                self.new_active_zdcli = self.carrierbag['standby_zd_cli']
                self.new_standby_zdcli = self.carrierbag['active_zd_cli']
        else:
            self.is_failover = False
        
        self._update_carrier_bag()
            
        if self.errmsg:
            return ('FAIL', self.errmsg)
        else:
            msg = 'The active ZD is %s' % self.new_active_zd.ip_addr
            return ('PASS', msg)
        
    def cleanup(self):
        pass
    
    def _update_carrier_bag(self):
        if self.is_failover:
            #add by west.li
            #update carrierbag after failover        
            self.carrierbag['active_zd'] = self.new_active_zd
            self.carrierbag['standby_zd'] = self.new_standby_zd
            if self.carrierbag.has_key('standby_zd_cli') and self.carrierbag.has_key('active_zd_cli'):
                self.carrierbag['standby_zd_cli'] = self.new_standby_zdcli
                self.carrierbag['active_zd_cli'] = self.new_active_zdcli

    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.conf = dict()
        
        self.conf.update(conf)
                
        self.active_zd = self.carrierbag['active_zd']
        self.standby_zd = self.carrierbag['standby_zd']
        self.new_active_zd = self.carrierbag[self.conf['zd']]