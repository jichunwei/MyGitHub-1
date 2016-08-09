# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: An Nguyen
   @contact: an.nguyen@ruckuswireless.com
   @since: Feb 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters:
   
   Test procedure:
    1. Config:
        -         
    2. Test:
        - Verify if the mesh tree are match with expected 
    3. Cleanup:
        -
   
   Result type: PASS/FAIL
   Results: PASS: If the mesh tree is not changed
            FAIL: If the mesh tree is changed

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import time
import logging
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.common import lib_Debug as bugme

class CB_ZD_Mesh_Recovery_SSID_Testing(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                            }

    def config(self, conf):
        self._init_test_parameter(conf)

    def test(self):
        self._get_recovery_ssid_info()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self._change_mesh_ssid_and_reboot_ap()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self._verify_station_could_scan_the_recovery_ssid()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self._verify_station_could_connect_to_recovery_ssid_wlan()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_parameter(self, conf):
        self.conf = {'timeout': 600}
        self.conf.update(conf)        
        self.errmsg = ''
        self.passmsg = ''
        
        self.zd = self.testbed.components['ZoneDirector']
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
    
    def _get_recovery_ssid_info(self):
        self.recovery_ssid_info = lib.apcli.radiogrp.get_recovery_ssid(self.active_ap)
        if not self.recovery_ssid_info['timeout'] and not self.recovery_ssid_info['service_wlan']:
            self.errmsg = 'The recovery-ssid function is not supported. Please check the system.'
                   
        elif self.recovery_ssid_info['service_wlan'].lower() != 'enabled':
            self.errmsg = 'The service wlan is not enabled as expected.'
        if self.errmsg: return
        
        self.recovery_wlan_cfg = {}
        wlan_list_info = lib.apcli.radiogrp.get_wlanlist(self.active_ap)
        
        for wlan_info in wlan_list_info:
            if wlan_info['name'] == 'recovery-ssid':
                self.recovery_wlan_cfg['ssid'] = wlan_info['ssid']
                passphrase = lib.apcli.radiogrp.get_passphrase(self.active_ap, wlan_info['wlanid'])
                if passphrase['passphrase'] == 'DID NOT EXIST':
                    self.errmsg = 'Can not get the recovery-ssid wlan passphrase'
                    return
                self.recovery_wlan_cfg['key_string'] = passphrase['passphrase'][0]
                self.recovery_wlan_cfg['encryption'] = 'AES'
                self.recovery_wlan_cfg['wpa_ver'] = 'WPA2'
                self.recovery_wlan_cfg['auth'] = 'PSK'
                return
            
        self.errmsg = 'Can not find out the recovery-ssid wlan settings'
        
    def _change_mesh_ssid_and_reboot_ap(self):
        """
        the mesh ap could not reconnect to the system during the meshu and meshd ssid be change
        """
        test_ssid = 'test-recovery-ssid'
        logging.info('Change the mesh ssid to %s and reboot the active ap' % test_ssid)
        self.active_ap.cmd('set ssid meshu %s' % test_ssid)
        self.active_ap.cmd('set ssid meshd %s' % test_ssid)
        self.active_ap.reboot(login=False)
        
        msg = 'Waiting %s seconds for the recovery-ssid wlan [%s] is up'
        msg = msg % (self.recovery_ssid_info['timeout'], self.recovery_wlan_cfg['ssid'])
        logging.info(msg)
        time.sleep(int(self.recovery_ssid_info['timeout']))
          
    def _verify_station_could_scan_the_recovery_ssid(self):
        """
        """
        msg = tmethod.verify_wlan_in_the_air(self.target_station, 
                                             self.recovery_wlan_cfg['ssid'], 
                                             self.conf['timeout'])
        if "The station didn't see the WLAN" in msg:
            self.errmsg = '[SCANNED IN %s SECS] %s' % (self.conf['timeout'], msg)
        else:
            self.passmsg = 'The recovery-ssid wlan[%s] is up as expected.' % self.recovery_wlan_cfg['ssid']
                
    
    def _verify_station_could_connect_to_recovery_ssid_wlan(self):
        """
        """
        tconfig.remove_all_wlan_from_station(self.target_station, 
                                             check_status_timeout = self.conf['timeout'])
            
        self.errmsg = tmethod.assoc_station_with_ssid(self.target_station, 
                                                      self.recovery_wlan_cfg,
                                                      self.conf['timeout'])       
        if not self.errmsg:
            passmsg = '; target station could connect to the recovery-ssid wlan %s'
            passmsg = passmsg % str(self.recovery_wlan_cfg)
            self.passmsg += passmsg