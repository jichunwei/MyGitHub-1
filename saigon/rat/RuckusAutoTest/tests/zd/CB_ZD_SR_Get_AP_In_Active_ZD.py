#import os
#import re
#import time
import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP
#from RuckusAutoTest.components.lib.zd import redundancy_zd as red
#from RuckusAutoTest.components import Helper_ZD as zhlp

class CB_ZD_SR_Get_AP_In_Active_ZD(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        logging.info('Check the number of active AP in active ZD')
        self.carrierbag[self.ap_active_zd] = self.get_ap_in_active_zd(self.active_zd)
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        msg = 'The Number of active AP in ZD is %s' % self.carrierbag[self.ap_active_zd][1]
        return self.returnResult('PASS', msg)
    
    
    def cleanup(self):
        pass


    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = dict(
                         check_status_timeout = 300
                         )
        
        self.conf.update(conf)
                
        self.active_zd = self.carrierbag['active_zd']
        self.ap_active_zd = self.conf['ap_active_zd']
        self.check_status_timeout = self.conf['check_status_timeout']
    def get_ap_in_active_zd(self,zd):
        logging.info("Get active AP Number")
        
        active_zd_mac = zd.mac_addr
        active_no = self._get_active_ap_number(zd, self.check_status_timeout)
        return (active_zd_mac,active_no)

        
    def _get_active_ap_number(self,zd,check_status_time = 300):
        '''
        Should make sure all of APs rehome to Active ZD.
        Updated by Chris.
        '''
        logging.info("Get ZD %s all active APs", zd.ip_addr)
        start_time = time.time()
        a_total_aps=0
        while time.time() - start_time < check_status_time:
            zd_active_ap_list = [] 
            
            all_ap_list_in_zd = zd.get_all_ap_info()            
            for ap in all_ap_list_in_zd:
                if  ap['status'].lower().startswith('connected'):
                    a_total_aps+=1
#                    zd_active_ap = RuckusAP(dict(ip_addr = ap['ip_addr'],username='admin',password='admin')) 
#                    zd_active_ap_list.append(zd_active_ap)
                
            e_total_aps = len(all_ap_list_in_zd)  
#            a_total_aps = len(zd_active_ap_list)
            if e_total_aps != a_total_aps:
                time.sleep(10)
                zd.refresh()
                a_total_aps=0
            else:
                break            
        
#        active_no =len(zd_active_ap_list)
        active_no =a_total_aps
#        del zd_active_ap_list
        return active_no