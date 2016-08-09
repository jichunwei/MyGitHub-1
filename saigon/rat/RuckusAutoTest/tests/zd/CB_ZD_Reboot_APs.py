# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: An Nguyen, an.nguyen@ruckuswireless.com
   @since: July 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'ZoneDirector'
   Test parameters:
       - 'mac_addr_list': 'ap mac address list',
       - 'timeout': 'timeout for ap join',
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - If need do manual approval, approval the ap in mac address list.
        - Verify ap joins and verify ap component via cli.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: AP joins successfully. 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Reboot_APs(Test):
    required_components = ['ZoneDirector']
    parameters_description = {'ap_mac_list': []}

    def config(self, conf):
        self._init_test_params(conf) 
    
    def test(self):
        self._verify_rebooting_ap_via_zd_webui()      
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {'ap_mac_list': [], # default empty will reboot all APs in test bed
                     'pause': 2,
                     'wait_to_connect': True,
                     'timeout': 360,
                     'zd_tag': ''}
        self.conf.update(conf)
        
        if self.conf['zd_tag']:
            self.zd = self.carrierbag[self.conf['zd_tag']]
        else: 
            self.zd = self.testbed.components['ZoneDirector']

        if not self.conf['ap_mac_list']:
            self.conf['ap_mac_list'] = self.testbed.config['ap_mac_list']
        
        self.errmsg = ''
        self.passmsg = ''
    
    def _verify_rebooting_ap_via_zd_webui(self):
        fail_aps = []
        for ap_mac in self.conf['ap_mac_list']:
            res = self._reboot_ap_by_zd(ap_mac)
            if not res:
                fail_aps.append(ap_mac)
        
        if fail_aps:
            self.errmsg = 'Failed to reboot APs %s via ZD WebUI' % fail_aps
            logging.info(self.errmsg)
            return
        
        passmsg = 'APs %s are reboot via ZD WebUI successfully. ' % self.conf['ap_mac_list']
        logging.info(passmsg)
        
        if self.conf['wait_to_connect']:
            self._wait_aps_connected(self.conf['timeout'])
            if self.errmsg:
                return
        
        self.passmsg = passmsg + self.passmsg
        logging.info(self.passmsg)
            
    def _reboot_ap_by_zd(self, ap_mac):
        logging.info("On ZD WebUI reboot AP[%s] to take effect" % ap_mac)
        try:
            lib.zd.aps.reboot_ap_by_mac_addr(self.zd, ap_mac)
            time.sleep(self.conf['pause']*5)
            msg = 'Success to reboot AP[%s] via ZD WebUI' % ap_mac
            logging.info(msg)
            return True
        except Exception, e:
            msg = 'Can not reboot AP[%s] via ZD WebUI: %s' % (ap_mac, e.message)
            logging.info(msg)
            return False
        
    def _wait_aps_connected(self, timeout):
        '''
        Wait ap provisioning, till status is connected.
        '''
        logging.info('Waiting %s for ap %s connected' % (timeout, self.conf['ap_mac_list']))
        end_time = time.time() + timeout
        while True:
            disconnect_list = []
            missing_list = []
            
            for ap_mac in self.conf['ap_mac_list']:
                ap_info = self.zd.get_all_ap_info(ap_mac)
                if ap_info:
                    if ap_info['status'].lower().startswith("connected"):
                        continue
                    else:
                        disconnect_list.append(ap_mac)
                else:
                    missing_list.append(ap_mac)
            
            if not disconnect_list and not missing_list: 
                self.passmsg += "The provision process for the AP %s is completed successfully" % self.conf['ap_mac_list']
                logging.info(self.passmsg)
                break
                
            if time.time() > end_time:
                if disconnect_list:
                    self.errmsg = 'The AP %s is in the %s status instead of \"Connected\" status after %d seconds' % \
                                    (disconnect_list, 'Disconnected', timeout)
                    logging.info(self.errmsg)
                    break
                    
                if missing_list:
                    self.errmsg = "The AP %s still does not appear in the AP-Summary table after %d seconds" % \
                                    (missing_list, timeout)
                    logging.info(self.errmsg)
                    break