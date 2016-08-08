'''
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 
   Result type: PASS/FAIL
   Results: PASS:
            FAIL:  

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - 
   2. Test:
       - Assign WLAN-Group1 to Active AP.
       - Move from WLAN-Group1 to WLAN-Group2.
       - Repeat do step#2 until timeout.
       - Check Active AP "uptime" and memory, and make sure which is running and no reboot
   3. Cleanup:
       - 
    How it was tested:
        
        
Create on 2013-2-19
@author: cwang@ruckuswireless.com
'''

import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

from RuckusAutoTest.components.lib.zdcli import configure_ap

class CB_ZD_Test_AP_Mem_Check(Test):
    required_components = ['ZoneDirectorCLI', 'RuckusAP']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.wg = self.conf['wlan_groups'][0]
        self.wg2 = self.conf['wlan_groups'][1]
        self.dur = self.conf.get('duration', 60 * 10)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.is_ap_support_11n = self.conf.get('is_ap_support_11n')
        self.ap_mac = self.conf.get('ap_mac')
        self.ap_tag = self.conf.get('active_ap')
    
    
    def _cfg_ap(self, wg):
        if self.is_ap_support_11n:
            ap_cfg = {'mac_addr': '%s' % self.ap_mac,      
                       'radio_ng': {'wlangroups': '%s' % wg},
                       'radio_na': {'wlangroups': '%s' % wg},
                       }
        else:
            ap_cfg = {'mac_addr': '%s' % self.ap_mac,      
                       'radio_ng': {'wlangroups': '%s' % wg},                   
                       }
        
        return ap_cfg
        
    
    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.ap_tag]['ap_ins']
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        st = time.time()
        flag = False
        while time.time() - st < self.dur:
            if flag:
                ap_cfg = self._cfg_ap(self.wg)           
                
            else:
                ap_cfg = self._cfg_ap(self.wg2)
                
            configure_ap.configure_ap(self.zdcli, ap_cfg)
            
            flag = not flag
            time.sleep(20)
        
        uptime = int(self.active_ap.get_up_time())
        if uptime < 120:
            return self.returnResult('FAIL', 'AP has rebooted.')
        else:
            return self.returnResult('PASS', 'Memory check pass.')
    
    def cleanup(self):
        self._update_carribag()