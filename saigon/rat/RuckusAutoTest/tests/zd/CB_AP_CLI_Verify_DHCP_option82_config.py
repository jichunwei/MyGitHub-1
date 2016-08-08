"""
   Description: 
   This test class support to verify the AP DHCP option82 configuration
   @since: Mar 2014
   @author: Anzuo

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
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
from RuckusAutoTest.components.lib.zdcli import get_wlan_info
       
map = {'Status':{'Status':'option82','Enabled':'enabled','Disabled':'disabled',},
       'Option82 sub-Option1':{'Option82 sub-Option1':'subopt1','IF-Name:VLAN-ID:ESSID:AP-Model:AP-Name:AP-MAC':'rks-circuitid','AP-MAC-hex':'ap-mac-hex','AP-MAC-hex ESSID':'ap-mac-hex essid','Disabled':None},
       'Option82 sub-Option2':{'Option82 sub-Option2':'subopt2','Client-MAC-hex':'clientmac-hex','Client-MAC-hex ESSID':'clientmac-hex essid','AP-MAC-hex':'ap-mac-hex','AP-MAC-hex ESSID':'ap-mac-hex essid','Disabled':None},
       'Option82 sub-Option150':{'Option82 sub-Option150':'subopt150','VLAN-ID':'vlan','Disabled':None},
       'Option82 sub-Option151':{'Option82 sub-Option151':'subopt151','Area-Name':'areaname','ESSID':'essid','Disabled':None}
       }


class CB_AP_CLI_Verify_DHCP_option82_config(Test):
    required_components = ['RuckusAP','Station']

    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        self._verify_ap_dhcp_option82()
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult("FAIL", self.errmsg)
        else:
            logging.debug(self.passmsg)
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
            
    def _cfg_init_test_params(self, conf):
        self.conf = dict(ap_tag = '',
                         ssid = '')
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = 'The configuration of option82 subopt on AP is the same as the one on ZD'
    
    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf.get('ap_tag')]['ap_ins']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
   
    def _verify_ap_dhcp_option82(self):
        logging.info('Verify the AP dhcp option82 %s' % self.active_ap.base_mac_addr)
        wlan_list = self.active_ap.get_wlan_list_by_ssid(self.conf.get('ssid'))
        option82_on_zd = get_wlan_info.get_wlan_by_ssid(self.zdcli, self.conf.get('ssid')).get('DHCP Option82')
        
        for wlan_if in wlan_list:
            option82_on_ap = self.active_ap.get_dhcp_option82_by_wlan_if(wlan_if)
            for i in option82_on_zd.keys():
                ap_subopt = map.get(i)
                
                actual = option82_on_ap.get(ap_subopt.get(i))
                expect = map.get(i).get(option82_on_zd.get(i).split(":")[0]if "Area-Name:" in option82_on_zd.get(i) else option82_on_zd.get(i))            
                
                if actual != expect:
                    self.errmsg += "[AP side]%s--%s,   [ZD side]%s--%s" % (ap_subopt, actual, i, option82_on_zd.get(i))


                 
                    
            
                    
                    
                    
                    
                    
                    
                    
                    
                    