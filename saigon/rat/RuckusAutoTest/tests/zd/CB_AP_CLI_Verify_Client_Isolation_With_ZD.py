"""
   Description: 
   @author: Jane Guo
   @contact: guo.can@odc-ruckuswireless.com
   @since: August 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
        - 'wlan_cfg': 'wlan cfg'
        format: wlan_cfg = {"name" : "RAT-Open-Non-Force-DHCP",
                    "ssid" : "RAT-Open-Non-Force-DHCP",
                    "auth" : "open",
                    "encryption" : "none",
        -'whitelist_name': white list name bind to wlan
        -'ap_tag': AP component tag
                    }
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Get the data from ZD
        - Get the data from AP
        - Compare the data between AP get and ZD get       
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
from RuckusAutoTest.components.lib.zdcli import white_list

class CB_AP_CLI_Verify_Client_Isolation_With_ZD(Test):
    required_components = ['RuckusAP','ZoneDirectorCLI']
    parameters_description = {'wlan_cfg': {},
                              'whitelist_name':'',
                              'ap_tag': 'active_ap'}

    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            zd_wl_cfg = self._get_whitelist_from_zd(self.whitelist_name)
            ap_ci_cfg = self._get_client_isolation_by_ssid(self.wlan_cfg['ssid'])
            self._verify_AP_ci_between_zd(self.wlan_cfg, zd_wl_cfg, ap_ci_cfg)
                
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
                     'whitelist_name':'',
                     'ap_tag': 'AP_01'}
        self.conf.update(conf)
        self.wlan_cfg = self.conf['wlan_cfg']
        self.whitelist_name = self.conf['whitelist_name']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
    
    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf.get('ap_tag')]['ap_ins']
    
    def _update_carrier_bag(self):
        pass

    def _get_whitelist_from_zd(self, whitelist_name):
        wl_conf = white_list.show_special_white_list(self.zdcli, whitelist_name)
        if not wl_conf:
            self.errmsg = "Can't find white list %s configuration on zd" % whitelist_name
        return wl_conf
         
    def _get_client_isolation_by_ssid(self, ssid):
        ci_conf = radiogroup.get_client_isolation_by_ssid(self.active_ap, ssid)
        if not ci_conf:
            self.errmsg = "Can't find client isolation configuration on AP"
        return ci_conf
         
    def _verify_AP_ci_between_zd(self, wlan_cfg, zd_wl_cfg, ap_ci_cfg):
        """
zd_wl_cfg
        2:
          Name= 222
          Description=
          Rules:
            1:
              Description=
              MAC = 12:11:11:11:11:11
              IP Address =    
ap_ci_cfg
wlan1: {client_isolation:{'mode': 'Enabled', 'filter_mode':'Source MAC & IP based ARP filters active',
                  'filter_acl':['11:11:11:11:11:11192.168.0.2','11:11:11:11:11:11192.168.0.3']}}    
        """
        logging.info("Verify Client Isolation on AP between ZD")
        get_list = []
        if wlan_cfg.has_key('isolation_per_ap') and not wlan_cfg.has_key('isolation_across_ap'):
            set_cfg_1=""
            if wlan_cfg['isolation_per_ap'] == True : 
                set_cfg_1 = 'Enabled' 
            elif wlan_cfg['isolation_per_ap'] == False:
                set_cfg_1 = 'Disabled'            

            for wlan in ap_ci_cfg:
                if wlan['status'] == "up":             
                    if not wlan['client_isolation']['mode'][0] == set_cfg_1 :
                        logging.info("Set cfg is %s, get cfg is %s"%(wlan_cfg['isolation_per_ap'],wlan['client_isolation']))
                        self.errmsg = "The info between set and get is different"
                    else:
                        get_list.append(wlan)
        
        elif wlan_cfg.has_key('isolation_across_ap') and wlan_cfg.has_key('white_list'): 
            zd_wl_filter_mode = ''
            rule_list = []
            for wl_no in zd_wl_cfg:
                rules = zd_wl_cfg[wl_no]['Rules']
                for idx in rules:
                    rule_conf = rules[idx]
                    wl_mac = rule_conf.get('MAC')
                    wl_ip = rule_conf.get('IP Address')
                    if wl_mac and wl_ip:
                        zd_wl_filter_mode = "Source MAC & IP based ARP filters active"
                        rule_list.append(wl_mac.lower()+wl_ip.lower())
                    elif wl_mac and not wl_ip:
                        zd_wl_filter_mode = "Source MAC Guard filter active"
                        rule_list.append(wl_mac.lower()+'0')
                    elif not wl_mac and wl_ip:
                        zd_wl_filter_mode = "IP based ARP filter active"
                        rule_list.append('0'+wl_ip)

            for wlan in ap_ci_cfg:
                if wlan['status'] == "up": 
                    filter_mode = wlan['client_isolation']['filter_mode'][0]
                    mode = wlan['client_isolation']['mode'][0]
                    filter_acl = wlan['client_isolation']['filter_acl']
                    filter_acl.sort()
                    rule_list.sort()
                    if not (zd_wl_filter_mode == filter_mode and filter_acl == rule_list and mode == 'Enabled'):
                        logging.info("Set cfg is %s, get cfg is %s"%(zd_wl_cfg,wlan))
                        self.errmsg = "The info between set and get is different"
                    else:
                        get_list.append(wlan)            
                        
        if not get_list:                                 
            if not self.errmsg:
                self.errmsg = "Don't find whitelist info on ZD or AP"            
