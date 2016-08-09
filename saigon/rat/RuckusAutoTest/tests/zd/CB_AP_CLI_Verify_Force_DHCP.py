"""
   Description: 
   @author: Jane Guo
   @contact: guo.can@odc-ruckuswireless.com
   @since: May 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
        - 'wlan_cfg': 'wlan cfg'
        format: wlan_cfg = {"name" : "RAT-Open-Non-Force-DHCP",
                    "ssid" : "RAT-Open-Non-Force-DHCP",
                    "auth" : "open",
                    "encryption" : "none",
                    "force_dhcp" : True,
                    "force_dhcp_timeout" : 30
                    }
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Get the data from AP
        - Compare the data between set and AP get       
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If data are same between get and set 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.apcli import radiogroup


class CB_AP_CLI_Verify_Force_DHCP(Test):
    required_components = ['RuckusAP']
    parameters_description = {'wlan_cfg': {},
                              'ap_tag': 'active_ap'}

    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            cli_cfg = self._get_AP_force_dhcp_conf(self.wlan_cfg['ssid'])
            self._verify_AP_force_dhcp_between_set_and_get(self.wlan_cfg, cli_cfg)
                
        except Exception, ex:
            self.errmsg = 'Compare set and AP get failed:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:
            self._update_carrier_bag()
            pass_msg = 'set and AP get are same'
            return self.returnResult('PASS', pass_msg)
    
    def cleanup(self):
        pass
            
    def _cfg_init_test_params(self, conf):
        self.conf = {'wlan_cfg': {},
                     'ap_tag': 'AP_01'}
        self.conf.update(conf)
        self.wlan_cfg = self.conf['wlan_cfg']
        self.errmsg = ''
    
    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf.get('ap_tag')]['ap_ins']
    
    def _update_carrier_bag(self):
        pass
     
    def _get_AP_force_dhcp_conf(self, ssid):
        wlan_list = radiogroup.get_force_dhcp_by_ssid(self.active_ap, ssid)
        if not wlan_list:
            self.errmsg = "Can't find wlan configuration on AP"
        return wlan_list
         
    def _verify_AP_force_dhcp_between_set_and_get(self, set_cfg, cli_cfg):
        logging.info("Verify Force DHCP on AP")
        wlanlist = cli_cfg
        
        if set_cfg.has_key('force_dhcp'):
            set_cfg_1=""
            if set_cfg['force_dhcp'] == True : 
                set_cfg_1 = 'Enabled' 
            elif set_cfg['force_dhcp'] == False:
                set_cfg_1 = 'Disabled'
            get_list = []
            for wlan in wlanlist:
                if wlan['status'] == "up":
                    if not wlan['force_dhcp'] == set_cfg_1 :
                        logging.info("Set cfg is %s, get cfg is %s"%(set_cfg['force_dhcp'],wlan['force_dhcp']))
                        self.errmsg = "The info between set and get is different"
                    else:
                        get_list.append(wlan)
        if not get_list:                                 
            if not self.errmsg:
                self.errmsg = "Don't find force dhcp info on AP"                    
