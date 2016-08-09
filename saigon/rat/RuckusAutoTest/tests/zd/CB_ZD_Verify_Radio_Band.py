"""
   Description: 
   @author: Kevin Tan
   @contact: kevin.tan@ruckuswireless.com
   @since: December 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'ZoneDirector'
   Test parameters:
       - 'ap_tag': 'ap instance identifier',
       - 'ap_model': 'AP model such as ZF7321',
       - 'ap_group': 'AP group that active AP belongs to',
       - 'ap_radioband_type': 'inherit from AP group config or override it',
       - 'ap_radioband_value': '2.4G or 5G Hz',
       - 'apgrp_radioband_type': 'inherit from default AP group ot not',
       - 'apgrp_radioband_value': '2.4G or 5G Hz',
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Verify radio band info in ap configuration and ap-group  configuration.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: AP joins successfully. 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Verify_Radio_Band(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}

    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()        
    
    def test(self):
        self._verify_ap_band_switch()

        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        self._update_carrier_bag()
        pass
    
    def _init_test_params(self, conf):
        self.conf = {'ap_tag':'',}
        self.conf.update(conf)
        
        zd_tag = self.conf.get('zd_tag')
        if zd_tag:
            self.zd = self.carrierbag[zd_tag]
        else:
            self.zd = self.testbed.components['ZoneDirector']
        
        self.ap_mac = self.carrierbag[self.conf['ap_tag']]['ap_ins'].base_mac_addr.lower()
                              
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass

    def _verify_ap_band_switch(self):
        apmac = self.ap_mac
        apgrp = self.conf['ap_group']

        ap_config_info = lib.zd.ap.get_ap_general_info_by_mac(self.zd, apmac)
        
        if ap_config_info['ap_group'] != apgrp:
            self.errmsg += 'active AP is in AP group %s, not %s for band switch' % (ap_config_info['ap_group'], apgrp)
            return
        if ap_config_info['radion_band_type'] != self.conf['ap_radioband_type']:
            self.errmsg += 'active AP radio band type %s not %s as expected' % (ap_config_info['radion_band_type'], self.conf['ap_radioband_type'])
            return
        if ap_config_info['radion_band_value'] != self.conf['ap_radioband_value']:
            self.errmsg += 'active AP radio band value %s not %s as expected' % (ap_config_info['radion_band_value'], self.conf['ap_radioband_value'])
            return
        
        current_ap_info = self.zd.get_all_ap_info(apmac)
        if not current_ap_info:
            logging.info('Get active AP[%s] info on "Currently Managed APs" page failed, wait for a few second and get it again' % (apmac))
            sleep(30)
            self.zd.get_all_ap_info(apmac)
            if not current_ap_info:
                self.errmsg += 'Get active AP[%s] info on "Currently Managed APs" page failed!' % (apmac)
                return

        ap_radioband = self.conf['ap_radioband_value']
        ap_channel = current_ap_info['channel']
        if  ap_radioband== '2.4 GHz':
            if not ('g/n' in ap_channel):#chen.tao 2014-2-24, to fix ZF-7563
                self.errmsg += 'Active AP[%s] channel[%s] on "Currently Managed APs" page unexpected, should be 11a/n!' % (apmac, ap_channel)
                return
        elif ap_radioband == '5 GHz':
            if not ('a/n' in ap_channel):#chen.tao 2014-2-24, to fix ZF-7563
                self.errmsg += 'Active AP[%s] channel[%s] on "Currently Managed APs" page unexpected, should be 11g/n!' % (apmac, ap_channel)
                return

        if self.conf.get('ap_model'):
            apgrp_radioband = lib.zd.apg.get_ap_group_radio_band_by_ap_model(self.zd, apgrp, self.conf['ap_model'])
            if apgrp_radioband['type'] != self.conf['apgrp_radioband_type']:
                self.errmsg += 'AP group [%s] radio band type[%s] for AP[%s] should be [%s]' % \
                                (apgrp, apgrp_radioband['type'], self.conf['ap_model'], self.conf['apgrp_radioband_type'])
                return
                    
            if apgrp_radioband['value'] != self.conf['apgrp_radioband_value']:
                self.errmsg += 'AP group [%s] radio band value[%s] for AP[%s] should be [%s]' % \
                                (apgrp, apgrp_radioband['apgrp_radioband_value'], self.conf['ap_model'], self.conf['apgrp_radioband_value'])
                return
