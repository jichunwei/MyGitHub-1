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

class CB_ZD_Backup_DHCP_Server_Info(Test):

    def config(self, conf):
        """
        """
        self._init_test_parameters(conf)

    def test(self):
        """
        """
        self._backup_zd_dhcp_server_info()
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
        
        self.errmsg = ''
        self.passmsg = ''

    def _backup_zd_dhcp_server_info(self):
        """
        """
        logging.info('Backup DHCP Server configuration and the assigned ip info')
        try:
            dconf = self.zd.get_dhcp_server_info()
            iassi = self.zd.get_assigned_ip_info()
            self.carrierbag['dhcp_server'] = {'configure': dconf, 'assigned_ip': iassi}
        except Exception, e:
            msg = '[Failed]: %s' % e.message
            self.errmsg = msg
            logging.info(self.errmsg)

        self.passmsg = 'Backup all DHCP server info to carrierbag successfully'
        logging.info(self.passmsg)