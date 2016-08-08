# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""Description:

    Prerequisite (Assumptions about the state of the testbed/DUT):

    Required components:
    Test parameters:
    Result type: PASS/FAIL
    Results: PASS
             FAIL otherwise

    Messages:
        - If PASS,
        - If FAIL, prints out the reason for failure

    Test procedure:
    1. Config:
        -
    2. Test:
        -
    3. Cleanup:
        -

    How is it tested: (to be completed by test code developer)
    
"""
import logging

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zd.upgrade_zd import get_ap_version_info

class CB_ZD_Get_Support_AP_Versions(Test):
    
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()        
    
    def test(self):
        self._get_ap_versions()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrive_carrier_bag(self):
        self.zd_fw_upgrade_cfg = self.carrierbag['zd_fw_upgrade_cfg']
    
    def _update_carrier_bag(self):
        self.carrierbag['zd_support_ap_versions'] = self.zd_support_ap_versions

    def _get_ap_versions(self):
        '''
        Get expected versions for ap.
        '''
        try:
            logging.info('Get ZD support ap versions information')
            aps_version_dict = get_ap_version_info(self.zd)
            
            self.zd_support_ap_versions = aps_version_dict
            
            logging.info('ZD support ap versions info: %s' % self.zd_support_ap_versions)
            self.passmsg = 'Get ZD support ap versions information successfully: %s' % self.zd_support_ap_versions 
        except Exception, ex:
            self.errmsg = ex.message