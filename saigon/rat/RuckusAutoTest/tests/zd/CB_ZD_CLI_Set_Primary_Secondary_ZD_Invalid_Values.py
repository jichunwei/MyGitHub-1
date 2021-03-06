# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: April 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'ZoneDirectorCLI'
   Test parameters:
       - 'invalid_primary_zd_ip_list': "Invalid primary zd ip address values",
       - 'invalid_secondary_zd_ip_list': "Invalid secondary zd ip address values",
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Configure limited ZD discovery with valid values.
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Error message is correct.

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging
import copy

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import config_ap_policy as lib

class CB_ZD_CLI_Set_Primary_Secondary_ZD_Invalid_Values(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {'invalid_primary_zd_ip_list': "Invalid primary zd ip address values",
                              'invalid_secondary_zd_ip_list': "Invalid secondary zd ip address values",
                              }
    
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        try:
            logging.info("Verify configure limited ZD discovery with invalid values")
            self._verify_config_with_invalid_values()
        except Exception, e:
            self.errmsg = "Set limited ZD discovery with invalid values failure: [%s]" % e.message
            
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult("FAIL", self.errmsg)
        else:
            self._update_carrier_bag()
            self.passmsg = "Error message is correct when configure limited ZD discovery with invalid values"
            return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(invalid_primary_zd_addr_list = [],
                         invalid_secondary_zd_addr_list = [],
                         zd_tag = '')
        self.conf.update(conf)
        
        default_zd_discovery_cfg = dict(enabled = True, 
                                        primary_zd_ip = '192.168.0.2',
                                        secondary_zd_ip = '192.168.0.3',
                                        keep_ap_setting = False, 
                                        prefer_prim_zd = False,)
        
        zd_tag = self.conf.pop('zd_tag')
        if zd_tag:
            self.zdcli = self.carrierbag[zd_tag]
        else:
            self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        zd_ip_addr = self.zdcli.ip_addr
        
        invalid_cfg_list = []
        
        for pri_zd_ip in self.conf['invalid_primary_zd_addr_list']:
            new_cfg = copy.deepcopy(default_zd_discovery_cfg)
            new_cfg['primary_zd_ip'] = pri_zd_ip
            new_cfg['secondary_zd_ip'] = zd_ip_addr
            
            invalid_cfg_list.append(new_cfg)
            
        for sec_zd_ip in self.conf['invalid_secondary_zd_addr_list']:
            new_cfg = copy.deepcopy(default_zd_discovery_cfg)
            new_cfg['primary_zd_ip'] = zd_ip_addr
            new_cfg['secondary_zd_ip'] = sec_zd_ip
            
            invalid_cfg_list.append(new_cfg)
            
        self.zd_discovery_cfg_list = invalid_cfg_list
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _verify_config_with_invalid_values(self):
        '''
        Verify error message is displayted when configure with invalid values for limited zd discovery.
        '''
        all_err_list = []
        
        exp_err_msg_list = ['The Primary ZoneDirector IP/IPv6 address or FQDN can not be empty or longer than 64 bytes.',
                            'The secondary ZoneDirector IP/IPv6 address or FQDN can not be longer than 64 bytes.']
        
        for cfg in self.zd_discovery_cfg_list:
            err_list = lib.cfg_limited_zd_discovery(self.zdcli, cfg)
            err_msg = str(err_list)
            
            result = False
            for exp_err in exp_err_msg_list:
                if exp_err in err_msg:
                    result = True
                    break
            
            if not result:
                all_err_list.append("Config:%s, Error:%s" % (cfg, err_msg))
        
        if all_err_list:
            self.errmsg = "Error message is incorrect: %s" % all_err_list
            logging.debug(self.errmsg)