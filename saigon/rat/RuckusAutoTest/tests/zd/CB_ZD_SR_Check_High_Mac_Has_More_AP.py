#import os
#import re
#import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP
#from RuckusAutoTest.components.lib.zd import redundancy_zd as red
#from RuckusAutoTest.components import Helper_ZD as zhlp

class CB_ZD_SR_Check_High_Mac_Has_More_AP(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        logging.info('Get lower MAC ZD active AP')
        self.higher_mac_zd = self._get_higher_mac_zd()
        
        lower_zd_ap_number = len(self._get_active_ap_list(self.lower_mac_zd))
        higher_zd_ap_number = len(self._get_active_ap_list(self.higher_mac_zd))
        if cmp(higher_zd_ap_number,lower_zd_ap_number) != 1:
            self.errmsg = 'Higher MAC address ZD has no more AP than Lower MAC ZD,higher mac zd(%d),lower mac zd(%d)' % (higher_zd_ap_number,lower_zd_ap_number)
            
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        msg = 'Higher Mac address ZD has more APs than lower mac ZD'
        return self.returnResult('PASS', msg)
    
    
    def cleanup(self):
        pass


    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = dict(
                         
                         )
        
        self.conf.update(conf)
                
        self.zd1 = self.carrierbag['zd1']
        self.zd2 = self.carrierbag['zd2']
        del self.carrierbag['active_zd']

    def _get_active_ap_list(self,zd):
        zd_active_ap_list = []
        logging.info("Get ZD %s all active APs", zd.ip_addr)
        all_ap_in_zd_dict = zd.get_all_ap_info()
        for ap in all_ap_in_zd_dict:
            if str(ap['status'].lower()).startswith('connected'):
                zd_active_ap = RuckusAP(dict(ip_addr = ap['ip_addr'],username='admin',password='admin')) 
                zd_active_ap_list.append(zd_active_ap)
        
        return zd_active_ap_list
    def _get_higher_mac_zd(self):
        mac_address1 = self.zd1.mac_addr
        mac_address2 = self.zd2.mac_addr
        if cmp(mac_address1,mac_address2) == 1:
            logging.info("ZD [%s] with MAC address [%s] is Higher",self.zd1.ip_addr,mac_address1)
            self.lower_mac_zd = self.zd2
            return self.zd1
        else:
            logging.info("ZD [%s] with MAC address [%s] is Higher",self.zd2.ip_addr,mac_address2)    
            self.lower_mac_zd = self.zd1
            return self.zd2
        