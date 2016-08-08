"""
   Description: 
   @author: Jane Guo
   @contact: guo.can@odc-ruckuswireless.com
   @since: May 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
        - 'wlan_cfg': {},
        - 'sta_tag': 'sta_1'
        - 'ap_tag' : 'active_ap'
        - 'check_time' : 120,
        - 'time_range': 40
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Get the DHCP lease time of special station from AP and check the lease time      
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Verify DHCP lease time on AP success 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.apcli import radiogroup

class CB_AP_CLI_Verify_DHCP_Lease_Time(Test):
    required_components = ['RuckusAP','Station']
    parameters_description = {'wlan_cfg': {},
                              'sta_tag': 'sta_1',
                              'ap_tag' : 'active_ap',
                              'check_time' : 120,
                              'time_range': 40}

    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            self._verify_ap_lease_time()
           
        except Exception, ex:
            self.errmsg = 'Verify DHCP lease time on AP fail:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:
            self._update_carrier_bag()
            pass_msg = 'Verify DHCP lease time on AP success'
            return self.returnResult('PASS', pass_msg)
    
    def cleanup(self):
        pass
            
    def _cfg_init_test_params(self, conf):
        self.conf = {'wlan_cfg': {},
                     'sta_tag': 'sta_1',
                     'ap_tag' : 'active_ap',
                    'check_time' : 120,
                    'time_range': 40}
        self.conf.update(conf)
        self.wlan_cfg = self.conf['wlan_cfg']
        self.check_time = self.conf['check_time']
        self.time_range = self.conf['time_range']
        self.errmsg = ''
    
    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf.get('ap_tag')]['ap_ins']
        self.sta_mac = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
        if not self.check_time:
            self.check_time = self.carrierbag['backup_lease_time']   
    
    def _update_carrier_bag(self):
        pass
     
    def _verify_ap_lease_time(self):
        current_time = self._get_AP_dhcp_lease_time()
        if not current_time:
            self.errmsg = "The lease time is null"
            return
        
        if int(current_time) > (int(self.check_time) - int(self.time_range)) and int(current_time) <= int(self.check_time) :
            pass
        else:
            self.errmsg = "The lease time on AP is incorrect"
    
    def  _get_AP_dhcp_lease_time(self):
        logging.info("Get AP dhcp lease time")
        lease_time=""
        wlan_list = radiogroup.get_force_dhcp_by_ssid(self.active_ap, self.wlan_cfg['ssid'])
        
        wlanid=[]
        for wlan in wlan_list:
            if wlan['status'] == "up":
                wlanid.append(wlan['wlanid'])

        if not wlanid:
            self.errmsg = "Can't find the wlan info on AP"
            return
        
        for i in range(0,len(wlanid)): 
            rudb_list = radiogroup.get_rudb_by_wlan_id(self.active_ap, wlanid[i])
            logging.info("%s's rudb info is %s" % (wlanid[i], rudb_list))
            if not rudb_list:
                self.errmsg = "rudb info is blank"
                return
            #@ZJ 201502 ZF-12025 behavior change on 9.12.0.0.65
            for idx in range(0,len(rudb_list)):
                if rudb_list[idx].get('mac'):
                    if rudb_list[idx].get('mac').lower() == self.sta_mac.lower():
                        lease_time = rudb_list[idx]['lease_time']
                        logging.info("Get the lease time is %s on AP" % lease_time)
                        break
                if rudb_list[idx].get('Mac'):
                    if rudb_list[idx].get('Mac').lower() == self.sta_mac.lower():
                        lease_time = rudb_list[idx]['Lease_time']
                        logging.info("Get the lease time is %s on AP" % lease_time)
                        break
        
        return lease_time            
