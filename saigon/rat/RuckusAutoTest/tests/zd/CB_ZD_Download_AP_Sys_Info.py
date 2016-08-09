'''
Download system log
'''

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import monitor_ap
import libZD_TestConfig as tconfig

class CB_ZD_Download_AP_Sys_Info(Test):
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        if monitor_ap.save_ap_sys_info(self.zd,self.ap_mac):
            return ('PASS', self.pass_msg)
        else:
            return ('FAIL', self.error_msg)
        
    def cleanup(self):
        pass

    def _cfgInitTestParams(self,conf): 
        self.conf={'ap_mac':'',
                   'ap_tag':'',#@author: yuyanan @since: 2014-8-29 optimize:parameter ap mac from ap tag
                   }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']
        #@author: yuyanan @since: 2014-8-28 optimize: get ap mac from ap tag
        if self.conf.get('ap_tag'):
            self.ap_mac = tconfig.get_active_ap_mac(self.testbed,self.conf['ap_tag'])
        else:
            self.ap_mac = self.conf['ap_mac']
        self.pass_msg = 'save ap system info successfully'
        self.error_msg = 'save ap system info failed'
