import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import redundancy_zd
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components.RuckusAP import RuckusAP

class CB_ZD_SR_Check_AP_Num_In_Active_Zd(Test):
    
    def config(self,conf):
        self._retrive_carrier_bag()
        self._cfgInitTestParams(conf)
        
    def test(self):
        ap_num=self._get_active_ap_Num(self.active_zd)
        if ap_num<self.expected_ap_num:
            self.errmsg="there are %d aps before SR enabled,but %d left after SR enabled" % (self.expected_ap_num,ap_num)
        
        if self.errmsg:
            return 'FAIL',self.errmsg
        else:
            return 'PASS',"there are %d aps before SR enabled,and all back after SR enabled" % self.expected_ap_num
        
    def _cfgInitTestParams(self,conf):
        self.expected_ap_num=len(self.active_zd.get_all_ap_info())
        self.errmsg=''
        pass
    
    def _retrive_carrier_bag(self):
        self.active_zd=self.carrierbag['active_zd']
        
    def _get_active_ap_Num(self,zd):
        zd_active_ap_Num = 0
        logging.info("Get ZD %s all active APs", zd.ip_addr)
        all_ap_in_zd_dict = zd.get_all_ap_info()
        for ap in all_ap_in_zd_dict:
            if ap['status'].lower() == 'connected':
                zd_active_ap_Num += 1
        
        return zd_active_ap_Num
     
    def cleanup(self):
        pass
        