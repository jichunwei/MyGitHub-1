'''
get ap number from zd web ui
by west.li 2012.03.05
'''

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP


class CB_ZD_Check_Ap_Num_From_Web(Test):

    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        self.ap_list=[]
        self.ap_num=len(self.ap_list)
        t0=time.time()
        while True:
            if time.time()-t0>self.timeout*60:
                return "FAIL","timeout when waiting for all ap connect,only %d/%d connected"\
                        %(self.ap_num,self.expect_ap_num)
                        
            self.ap_list=self._get_active_ap_list(self.zd)
            self.ap_num=len(self.ap_list)
            if self.ap_num==self.expect_ap_num:
                msg = 'there are %d ap connect to zd' % self.ap_num
                self.carrierbag['managed_ap_num']=self.ap_num 
                return ('PASS', msg)
        
    def cleanup(self):
        pass


    def _get_active_ap_list(self,zd):
        zd_active_ap_list = []
        logging.info("Get ZD %s all active APs", zd.ip_addr)
        for mac in self.ap_mac_list:
            ap = zd.get_all_ap_info(mac)
            if ap and ap['status'].lower().startswith('connected'):
                zd_active_ap_list.append(ap)
        
        return zd_active_ap_list    
    
    def _cfgInitTestParams(self,conf): 
        self.conf={'timeout':30}#minutes
        self.conf.update(conf)
        self.timeout=self.conf['timeout']
        self.errmsg=''
        self.zd = self.testbed.components['ZoneDirector']
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']
        self.ap_mac_list=self.testbed.ap_mac_list
        if self.carrierbag.has_key('managed_ap_num'):
            self.expect_ap_num=self.carrierbag['managed_ap_num']
        else:
            self.expect_ap_num=len(self.ap_mac_list)
            
        
    