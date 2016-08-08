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
        ap_tag: AP tag
        ap_radio: 802.11g/n or 802.11a/n
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Get the bssid of special AP and special radio   
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Get the bssid
                FAIL: Can't get the bssid

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging
import time
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.apcli import radiogroup


class CB_AP_CLI_Get_BSSID(Test):
    required_components = ['RuckusAP']
    parameters_description = {'wlan_cfg': {},
                              'ap_tag': 'AP_01',
                              'ap_radio': '802.11g/n'}

    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            self.bssid = self._get_bssid(self.wlan_cfg['ssid'], self.ap_radio)
            
            if not self.bssid:
                self.errmsg = "Get bssid fail"
                return self.returnResult("FAIL",self.errmsg)
                
        except Exception, ex:
            self.errmsg = 'Get bssid failed:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:
            self._update_carrier_bag()
            pass_msg = 'Get bssid is %s' % self.bssid
            return self.returnResult('PASS', pass_msg)
    
    def cleanup(self):
        pass
            
    def _cfg_init_test_params(self, conf):
        self.conf = {'wlan_cfg': {},
                     'ap_tag': 'AP_01',
                     'ap_radio': '802.11g/n'}
        self.conf.update(conf)
        self.wlan_cfg = self.conf['wlan_cfg']
        self.ap_radio = self.conf['ap_radio']
        self.errmsg = ''
    
    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf.get('ap_tag')]['ap_ins']
    
    def _update_carrier_bag(self):
        self.carrierbag[self.conf['ap_tag']]['bssid'] = self.bssid
     
    def _get_bssid(self, ssid, radio):
        """
        {'status': 'up', 
'name': 'wlan0', 
'bssid': '54:3d:37:10:57:08', 
'wlanid': 'wlan0', 
'type': 'AP', 
'radioid': '0', 
'ssid': 'Rqa-rat-client-isolation'
}
        """
        if 'a' in radio:
            radioid = 1
        else:
            radioid = 0
#zj 20140415 optimization zf-7997
        time_getbssid=0
        while time_getbssid < 3:
            bssid = radiogroup.get_bssid_by_ssid_radio(self.active_ap, ssid, radioid)
            if bssid: break
            else:
                time_getbssid +=1
                time.sleep(5)
                
        return bssid      
