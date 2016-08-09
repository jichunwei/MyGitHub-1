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


# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Verify_DHCP_Server_Info(Test):

    def config(self, conf):
        """
        """
        self._init_test_parameters(conf)

    def test(self):
        """
        """
        self._verify_zd_dhcp_server_configuration()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', '')

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
        self.conf = {'zd_tag': ''}
        self.conf.update(conf)
        
        if self.conf['zd_tag']:
            self.zd = self.carrierbag[self.conf['zd_tag']]
        else: 
            self.zd = self.testbed.components['ZoneDirector']
        
        self._get_expected_dhcp_server_info()
        
        self.errmsg = ''
        self.passmsg = ''
    
    def _get_expected_dhcp_server_info(self):
        self.expected_info = self.carrierbag['dhcp_server']
    
    def _verify_zd_dhcp_server_configuration(self):
        """
        """
        logging.info('Verify the DHCP Server configuration')
        zd_dhcp_config = self.zd.get_dhcp_server_info()
        zd_assigned_ip = self.zd.get_assigned_ip_info()
        logging.info('ZD DHCP Server configuration: \n%s' % zd_dhcp_config)
        logging.info('Assigned IP Info: \n%s' %zd_assigned_ip)
        
        if zd_dhcp_config != self.expected_info['configure']:
            errmsg = 'The current DHCP configuration is %s instead of %s as expected'
            errmsg = errmsg % (zd_dhcp_config, self.expected_info['configure'])
            logging.info(errmsg)
            self.errmsg = errmsg
        
        zd_assigned_ip_info = {}
        expected_assigned_ip_info = {}
        
        for entry in zd_assigned_ip:
            zd_assigned_ip_info[entry['mac']] = entry['ip']
        
        for entry in self.expected_info['assigned_ip']:
            expected_assigned_ip_info[entry['mac']] = entry['ip']
        
        if zd_assigned_ip_info != expected_assigned_ip_info:
            errmsg = 'The current assigned ip info is %s instead of %s as expected'
            errmsg = errmsg % (zd_assigned_ip_info, expected_assigned_ip_info)
            logging.info(errmsg)
            self.errmsg = self.errmsg + '. ' + errmsg
        
        if self.errmsg:
            logging.info(self.errmsg)
            return
        
        self.passmsg = 'All DHCP server configuration and assigned ip info are displayed as expected'
        logging.info(self.passmsg)