#import os
#import re
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP
#from RuckusAutoTest.components.lib.zd import redundancy_zd
#from RuckusAutoTest.components import Helper_ZD as zhlp

class CB_ZD_SR_AP_Rehome_Disable_Port(Test):
    
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
        ap_in_active = self._get_active_ap_number(self.active_zd)
        logging.info("Cut down network service 3 times on Active ZD")
        for i in range(0,3):
            self.cut_down_active_zd_5s_ap_rehome(self.active_zd,self.sw)
        
        ap_in_active_after_cut_down_interface_5s = self._get_active_ap_number(self.active_zd)
        
        if ap_in_active == ap_in_active_after_cut_down_interface_5s:
            self.passmsg = 'Cut down network service for 5 sec 3 times on Active ZD, APs should still managed by Active ZD'
            
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass

        
    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.active_zd = self.carrierbag['active_zd']
        self.sw = self.carrierbag['sw'] 
        
        
    def cut_down_active_zd_5s_ap_rehome(self, active_zd,sw):
        logging.info('Get the Active ZD interface')
#        active_zd.navigate_to(0,-1)
        active_zd_mac = active_zd.mac_addr
        active_zd_interface = sw.mac_to_interface(active_zd_mac)
        logging.debug('The Active ZD interface is %s',active_zd_interface)
        
        logging.info('Disable the active ZD interface')
        sw.disable_interface(active_zd_interface)
        
        time.sleep(5)
        
        logging.info('Enable the former Active ZD %s interface', active_zd.ip_addr)
        sw.enable_interface(active_zd_interface)
        time.sleep(5)
        active_zd.refresh()
            
            
    def _get_active_ap_number(self,zd,check_status_time = 300):
        
        logging.info("Get ZD %s all active APs", zd.ip_addr)
        start_time = time.time()
        all_ap_in_zd_dict = zd.get_all_ap_info()
        total_ap_num = len(all_ap_in_zd_dict)
        while time.time() - start_time < check_status_time:
            active_no=0
            for ap in all_ap_in_zd_dict:
                if  ap['status'].lower().startswith('connected'):
                    active_no+=1
                    
                else:
                    time.sleep(10)
                    zd.refresh()
                    break
                
            if total_ap_num == active_no:
                break
        return active_no