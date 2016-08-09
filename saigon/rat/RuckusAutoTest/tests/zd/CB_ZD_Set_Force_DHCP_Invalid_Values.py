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

class CB_ZD_Set_Force_DHCP_Invalid_Values(Test):
    required_components = ['ZoneDirector']
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
            pass_msg = 'Configure an invalid Force DHCP timeout on the ZD GUI success'
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
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''

    def _retrieve_carribag(self):
        pass
                
    def _update_carrier_bag(self):
        pass

    def _cfg_invalid_force_dhcp_timeout(self):
        logging.info("Configure an invalid Force DHCP timeout on the ZD GUI")

        for timeout in self.invalid_timeout_list:
            default_cfg = deepcopy(self.wlan_cfg)        
            default_cfg['force_dhcp_timeout'] = timeout
            logging.info("Time out value is '%s'" % timeout ) 
            try:
                lib.zd.wlan.create_wlan(self.zd, default_cfg)
            except Exception, e:
                msg = e.message
                if timeout:
                    cfg = self._init_check_message()
                else:
                    cfg = "Force DHCP Timeout cannot be empty"
                if not re.findall(cfg, msg):
                    self.errmsg = msg
                    
    def _init_check_message(self):
        """
            E_FailRange={1} must be a number between {2} and {3} 
        """
        message=self.zd.messages
        event_msg =message['E_FailRange']
        event_msg=event_msg.replace('{1}','Force DHCP Timeout')
        event_msg=event_msg.replace('{2}','5')
        event_msg=event_msg.replace('{3}','120')
        return event_msg