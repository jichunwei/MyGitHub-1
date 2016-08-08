# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: An Nguyen
   @contact: an.nguyen@ruckuswireless.com
   @since: Jul 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'Zone Director'
   Test parameters:
       - 
        
   Test procedure:
    1. Config:
        - initialize test parameters
    2. Test:
        - Configure dhcp server on ZD WebUI
        - Verify if the service is running
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: service is working as expectation. 
            FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import sys_if_info as sysif

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Configure_DHCP_Server(Test):

    def config(self, conf):
        """
        """
        self._init_test_parameters(conf)

    def test(self):
        """
        """
        self._verify_configure_zd_dhcp_server()
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
        
        logging.debug(self.passmsg)
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        """
        """
        pass

#
#
#
    def _init_test_parameters(self, conf):
        """
        """
        self.conf = {'negative': False,
                     'dhcp_ser_cfg': {},
                     'zd_tag': ''}
        self.conf.update(conf)
        
        if self.conf['zd_tag']:
            self.zd = self.carrierbag[self.conf['zd_tag']]
        else: 
            self.zd = self.testbed.components['ZoneDirector']
        
        self.zdcli1, self.zdcli2 = None, None
        if self.carrierbag.has_key('zdcli1'):
            self.zdcli1 = self.carrierbag['zdcli1']
            
        if self.carrierbag.has_key('zdcli2'):
            self.zdcli2 = self.carrierbag['zdcli2']
        
        self._update_dhcp_configuration_params()
        
        self.errmsg = ''
        self.passmsg = ''
    
    def _update_dhcp_configuration_params(self):
        if not self.conf['dhcp_ser_cfg']['enable']:
            return
        if self.conf['dhcp_ser_cfg']['number_ip'] == 'aps_num':
            num_of_aps = len(self.zd.get_all_ap_info())
            self.conf['dhcp_ser_cfg']['number_ip'] = num_of_aps
        if self.conf['dhcp_ser_cfg']['number_ip'] == 'aps_num_plus_1':
            num_of_aps = len(self.zd.get_all_ap_info())
            self.conf['dhcp_ser_cfg']['number_ip'] = num_of_aps + 1
    
    def _verify_configure_zd_dhcp_server(self):
        """
        """
        logging.info('Configure the DHCP Server')
        try:
            if self.carrierbag['zd1'] and self.zdcli1:
                ip_mode = sysif.get_sys_if_info(self.zdcli1)['Device IP Address']['Mode']
                if ip_mode != 'Manual':
                    sysif._set_sys_if_mode(self.zdcli1, {'mode':'static'}, 5)
                    self.carrierbag['zd1'].refresh()
            if self.carrierbag['zd2'] and self.zdcli2:
                ip_mode = sysif.get_sys_if_info(self.zdcli2)['Device IP Address']['Mode']
                if ip_mode != 'Manual':
                    sysif._set_sys_if_mode(self.zdcli2, {'mode':'static'}, 5)    
                    self.carrierbag['zd2'].refresh()
                
            self.zd.set_dhcp_server(self.conf['dhcp_ser_cfg'])
        except Exception, e:
            if not self.conf['negative']:
                msg = '[Incorrect behavior][Configuration Failed]: %s' % e.message
                self.errmsg = msg
            else:
                msg = '[Correct behavior][Configuration Failed]: %s' % e.message
                self.passmsg = msg
            return
        
        if not self.conf['negative']:
            self.passmsg = '[Correct behavior][Configuration successfully] [%s]' % str(self.conf['dhcp_ser_cfg'])
        else:
            self.errmsg = '[Incorrect behavior][Configuration successfully] [%s]' % str(self.conf['dhcp_ser_cfg'])