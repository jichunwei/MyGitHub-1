"""
   Description: 
   @author: Jane Guo
   @contact: guo.can@odc-ruckuswireless.com
   @since: May 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
       - 'invalid_timeout_list': Invalid force dhcp time out values
       - 'wlan_cfg': wlan cfg
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Config invalid force dhcp time out values       
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Config invalid force dhcp time out values, get the correct error message
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import logging
import re
from copy import deepcopy
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_CLI_Set_Force_DHCP_Invalid_Values(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {'invalid_timeout_list':{}, #Invalid force dhcp time out values
                              'wlan_cfg': {},
                              }
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._retrieve_carribag()
        
    def test(self):
        self._cfg_invalid_force_dhcp_timeout()
 
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:
            self._update_carrier_bag()
            pass_msg = 'Configure an invalid Force DHCP timeout on the ZD CLI success'
            return self.returnResult('PASS', pass_msg)
        
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.conf = {'invalid_timeout_list':{}, #Invalid force dhcp time out values
                 'wlan_cfg': {},
                 }
        self.conf.update(conf)    
        self.invalid_timeout_list = self.conf['invalid_timeout_list']     
        self.wlan_cfg = self.conf['wlan_cfg']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        self.errmsg = ''

    def _retrieve_carribag(self):
        pass
                
    def _update_carrier_bag(self):
        pass

    def _cfg_invalid_force_dhcp_timeout(self):
        logging.info("Configure an invalid Force DHCP timeout on the ZD CLI")

        for timeout in self.invalid_timeout_list:
            default_cfg = deepcopy(self.wlan_cfg)
            default_cfg['force_dhcp_timeout'] = timeout
            logging.info("Time out value is '%s'" % timeout ) 
            try:
                lib.zdcli.wlan.create_wlan(self.zdcli, default_cfg)
            except Exception, e:
                msg = e.message
                #can't find this message type
                if not re.findall("The seconds must be between 5 and 120", msg):
                    self.errmsg = msg