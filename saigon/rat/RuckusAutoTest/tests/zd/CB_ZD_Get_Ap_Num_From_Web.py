'''
get ap number from zd web ui
by west.li 2012.03.05
'''

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP


class CB_ZD_Get_Ap_Num_From_Web(Test):

    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        self.ap_list=self._get_active_ap_list(self.zd)
        self.ap_num=len(self.ap_list)
        
        if self.errmsg:
            return ('FAIL', self.errmsg)  
        
        self.carrierbag['managed_ap_num']=self.ap_num      
        
        msg = 'there are %d ap connect to zd' % self.ap_num
        return ('PASS', msg)
        
    def cleanup(self):
        pass


    def _get_active_ap_list(self,zd):
        zd_active_ap_list = []
        logging.info("Get ZD %s all active APs", zd.ip_addr)
        all_ap_in_zd_dict = zd.get_all_ap_info()
        for ap in all_ap_in_zd_dict:
            if ap['status'].lower() == 'connected':
#                zd_active_ap = RuckusAP(dict(ip_addr = ap['ip_addr'],username='admin',password='admin')) 
                zd_active_ap_list.append(ap)
        
        return zd_active_ap_list    
    
    def _cfgInitTestParams(self,conf): 
        self.errmsg=''
        self.zd = self.testbed.components['ZoneDirector']
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']
            
        
    