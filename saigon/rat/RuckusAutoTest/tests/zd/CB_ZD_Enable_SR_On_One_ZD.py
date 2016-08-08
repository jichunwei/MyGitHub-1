'''
Created on 2014-11-10
@author: chen.tao@odc-ruckuswireless.com
'''
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import redundancy_zd

class CB_ZD_Enable_SR_On_One_ZD(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        self.enable_sr_on_one_zd()
        if self.errmsg:
            if self.negative:
                return self.returnResult('PASS', self.errmsg)
            else:
                return self.returnResult('FAIL', self.errmsg)
        else:
            msg = 'Enable Smart Redundancy on ZD successfully.'
            if self.negative:
                return self.returnResult('FAIL', msg)
            else:
                return self.returnResult('PASS', msg)
    
    def cleanup(self):
        pass

        
    def _cfgInitTestParams(self, conf):
        self.conf = {'zd_tag':'',
                     'sr_cfg':{
                               'peer_ip_addr':'1.1.1.1',
                               'share_secret':'testing123'
                               },
                     'negative':False
                     }
        self.conf.update(conf)
        self.negative = self.conf['negative']
        self.errmsg = ''
        self.passmsg = ''
        zd_tag = self.conf.get('zd_tag')
        if zd_tag:
            self.zd = self.carrierbag[zd_tag]
        else:
            self.zd = self.testbed.components['ZoneDirector']
        
    def enable_sr_on_one_zd(self):

        peer_ip_addr = self.conf['sr_cfg']['peer_ip_addr']
        share_secret = self.conf['sr_cfg']['share_secret']
        try:
            redundancy_zd.enable_single_smart_redundancy(self.zd, peer_ip_addr, share_secret)
        except Exception,ex:
            self.errmsg = ex.message 