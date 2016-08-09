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
        
        
Create on 2012-12-20
@author: kevin.tan@ruckuswireless.com
'''

import logging
import time
import re

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.zd import dashboard_zd

class CB_ZD_Verify_HW_Acceleration(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}

    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()        
    
    def test(self):
        if self.conf['device'].lower() == 'zd5k':
            if self.conf['check_crypto']:
                sys_info = dashboard_zd.get_system_info(self.zd)
                if 'ZD5' not in sys_info['Model']:
                    self.passmsg = 'ZD model is not ZD5K, HW acceleration check is not needed'
                    return self.returnResult('PASS', self.passmsg)
                
                raw_info = self.zdcli.get_crypto()
                res_name = re.findall(r'name\s*:\s*cbc\(aes\)', raw_info)
                if len(res_name) == 0:
                    self.errmsg = 'Unexpected interrupt name[%s] of ZD' % (raw_info)
        
                res_driver = re.findall(r'driver\s*:\s*cbc\(aes-aesni\)', raw_info)
                if len(res_driver) == 0:
                    self.errmsg = 'Unexpected interrupt driver[%s] of ZD' % (raw_info)

        elif self.conf['device'].lower() == 'ap':
            current_ap_info = self.zd.get_all_ap_info(self.apmac)
            if not current_ap_info:
                logging.info('Get active AP[%s] info on "Currently Managed APs" page failed, wait a few second and get it again' % (self.apmac))
                time.sleep(15)
                current_ap_info = self.zd.get_all_ap_info(self.apmac) 
                if not current_ap_info:
                    self.errmsg = 'Get active AP[%s] info on "Currently Managed APs" page failed' % (self.apmac)
                    logging.info(self.errmsg)
                    return self.returnResult('FAIL', self.errmsg)
            
            ap_model = current_ap_info['model'].lower()
            if 'zf7982' not in ap_model and 'zf7782' not in ap_model: # only support SnoopDogg 7982 and Corfu 7782
                self.errmsg = 'Active AP model[%s] is unexpected and HW acceleration unsupported' % ap_model 
                logging.info(self.errmsg)
                return self.returnResult('FAIL', self.errmsg)

            if self.conf['check_crypto']:
                info = active_ap.get_crypto()
                res_name = re.findall(r'name\s*:\s*cbc\(aes\)', raw_info)
                if len(res_name) == 0:
                    self.errmsg = 'Unexpected crypto name[%s] of active AP[%s]' % (raw_info, apmac)
        
                res_driver = re.findall(r'driver\s*:\s*cbc\(cbc-aes-talitos\)', raw_info)
                if len(res_driver) == 0:
                    self.errmsg = 'Unexpected crypto driver[%s] of active AP[%s]' % (raw_info, apmac)

            if self.conf['check_interrupts']:
                info = ap.get_interrupts()
                res = re.findall(r'OpenPIC\s*Level\s*talitos', raw_info)
                if len(res_name) == 0:
                    self.errmsg = 'Unexpected crypto name[%s] of active AP[%s]' % (raw_info, apmac)
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        self._update_carrier_bag()
        pass
    
    def _init_test_params(self, conf):
        self.conf = {'check_crypto':False, 'check_interrupts': False}
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrive_carrier_bag(self):
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.apmac = self.active_ap.base_mac_addr
        pass
    
    def _update_carrier_bag(self):
        pass
