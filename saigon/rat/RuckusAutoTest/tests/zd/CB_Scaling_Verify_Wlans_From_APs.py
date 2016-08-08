# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
'''
Verify WLANs can deploy to RuckusAPs or SIMAPs successfully.
'''
import logging
import random

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components.lib.zd import scaling_zd_lib as SCALING 

class CB_Scaling_Verify_Wlans_From_APs(Test):
    
    required_components = ["ZoneDirector"]
    parameter_description = {}
    
    def config(self, conf):
        self.conf = conf
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.ap_username = self.zd.username
        self.ap_password = self.zd.password 
               
        self.aps = self.carrierbag['existing_aps_list']
        self.wlan_conf_list = self.carrierbag['existing_wlans_list']
        self.errmsg = ''
        self.passmsg = ''
    
    def test(self): 
        ap_list = self.aps.values()
        ap = ap_list[0]
        logging.info('Checking the first AP[%s, %s]' % (ap['mac'], ap['model']))
        self._chk_wlan_on_ap(ap)
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        random.seed()
        index = random.randrange(1, len(ap_list) - 2)
        ap = ap_list[index]
        logging.info('Checking  AP[%s, %s]' % (ap['mac'], ap['model']))
        self._chk_wlan_on_ap(ap)
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        ap = ap_list[-1]
        logging.info('Checking the last AP[%s, %s]' % (ap['mac'], ap['model']))
        self._chk_wlan_on_ap(ap)
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
                
        
        return self.returnResult("PASS","All of WLANs can deploy to RuckusAPs and SIMAPs successfully, WLANs[%s]" % self.wlan_conf_list)
                    
    def cleanup(self):
        pass
    
    def _chk_wlan_on_ap(self, ap):
        mac_addr = ap['mac']
        try:
            ip_addr = SCALING.get_ap_ip_addr_by_ap_mac(self.zdcli, mac_addr)
        except Exception, e:
            logging.warning(e.message)
            self.errmsg = "AP[%s] haven't been managed by ZD" % mac_addr
            return
                                
        active_ap = RuckusAP(dict(ip_addr = ip_addr, username = self.ap_username, password = self.ap_password, ))
        #For wlan_name in self.wlan_conf_list:
        if not active_ap.verify_wlan():
            self.errmsg =  'WLANs do not deploy to AP [%s] correctly' % mac_addr
            return 
                    
        logging.info("WLANs exist in AP[%s]" % (mac_addr))        
        