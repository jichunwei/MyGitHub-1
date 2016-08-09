# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
"""
Description: This combo API support to remove the expected approval APs via ZD WebUI
Author: An Nguyen
Email: an.nguyen@ruckuswireless.com

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:
       'ap_mac_list': the expected APs mac address list
       'ap_tag': the ap_tag or ap_tag list that stored in carrier bag
       'zd_tag': the expected/active zd tag, optional. If none the default ZD is used

   Result type: PASS/FAIL/ERROR

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:  

   How it is tested?
"""
import logging

from RuckusAutoTest.models import Test

class CB_ZD_Delete_APs(Test):
    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        self._remove_approval_aps()
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
        
        logging.debug(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
        
    def _init_test_params(self, conf):
        self.conf = {'ap_mac_list': [],
                     'ap_tag': ''}
        self.conf.update(conf)
        
        self.errmsg = ''
        self.passmsg = ''
        
        if self.conf.get('zd_tag'):
            self.zd = self.carrierbag[self.conf['zd_tag']]
        else:
            self.zd = self.testbed.components['ZoneDirector']
        
        if self.conf['ap_tag'] and type(self.conf['ap_tag']) in [str, list]:
            ap_tag_list = list([self.conf['ap_tag']])
        else:
            msg = '[ERROR] The "ap_tag" value is a %s instead of str or list.'
            logging.debug(msg)
        
        for ap_tag in ap_tag_list:
            ap = self.carrierbag[ap_tag]['ap_ins']
            self.conf['ap_mac_list'].append(ap.base_mac_addr)
                
    def _remove_approval_aps(self):
        if self.conf['ap_mac_list']:
            msg = 'Remove the below approval APs %s' % self.conf['ap_mac_list']
            logging.info(msg)
            try:
                for ap_mac in self.conf['ap_mac_list']:
                    self.zd.remove_approval_ap(ap_mac)
                self.passmsg = 'Remove approval APs %s successfully' % self.conf['ap_mac_list']
            except:
                self.errmsg = 'Failed to remove approval APs %s' % self.conf['ap_mac_list']                
        else:
            msg = 'Remove all approval APs'
            logging.info(msg)
            try:
                self.zd.remove_approval_ap()
                self.passmsg = 'Remove approval APs successfully'
            except:
                self.errmsg = 'Failed to remove all approval APs'
            
        