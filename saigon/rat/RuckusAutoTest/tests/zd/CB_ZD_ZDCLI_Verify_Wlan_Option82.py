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
       -            
   3. Cleanup:
       - 
    How it was tested:
        
        
Create on 2012-2-15
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

class CB_ZD_ZDCLI_Verify_Wlan_Option82(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(wlan_cfg = None)
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.wlan_cfg = self.conf['wlan_cfg']
        self.errmsg = ""
        self.passmsg = ""
    
    def _retrieve_carribag(self):
        self.zdcli_wlan = self.carrierbag['existed_zdcli_wlan']
        self.zd_wlan = self.carrierbag['wlan_info_gui_get']        
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        aname = self.zd_wlan['name']
        bname = self.zdcli_wlan['NAME']
        if aname != bname:
            return self.returnResult("FAIL", 
                                     "Different WLAN name %s, %s, please check" % (aname, bname))
            
        aoption82 = self.zd_wlan['option82']
        #@author: Liu Anzuo @since: 20130925 add ['Satus'] to get option82 status for 9.8
        boption82 = self.zdcli_wlan['DHCP Option82']['Status']
        if self.wlan_cfg is not None:
            option82 = self.wlan_cfg['option82']
            if option82:
                if aoption82 != 'Enabled':
                    return self.returnResult("FAIL", "Expected option82 is enabled, but %s" % aoption82)
            else:
                if aoption82 != 'Disabled':
                    return self.returnResult("FAIL", "Expected option82 is disabled, but %s" % aoption82)
        
        if aoption82 != boption82:
            return self.returnResult("FAIL", 
                                     "Different option82 setting %s, %s, please check" % (aoption82, boption82))
        
        return self.returnResult('PASS', 'DHCP Option82 setting is valid.')
    
    def cleanup(self):
        self._update_carribag()
        