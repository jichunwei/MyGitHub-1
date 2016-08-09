# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: An Nguyen
   @contact: an.nguyen@ruckuswireless.com
   @since: Dec 2011

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
from RuckusAutoTest.common import lib_Debug as bugme

class CB_ZD_DFS_Channel_Testing(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                            }

    def config(self, conf):
        self._init_test_parameter(conf)

    def test(self):
        self._enable_dfs_channel_on_zd()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self._apply_a_dfs_channel_to_active_ap()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self._verify_aps_info()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self._do_bangradar_on_active_ap()
        self._verify_dfs_blocked_channel_on_active_ap()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_parameter(self, conf):
        self.conf = {'is_block_channel': True}
        self.conf.update(conf)        
        self.errmsg = ''
        self.passmsg = ''
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        if self.carrierbag.get('expected_aps_info'):
            self.expected_aps_info = self.carrierbag['expected_aps_info']
        else:
            self.expected_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
    
    def _verify_aps_info(self):
        logging.debug('The expected APs info:\n %s' % pformat(self.expected_aps_info))
        current_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
        logging.debug('The current APs info: \n %s' % pformat(current_aps_info))
               
        lost_aps = []
        error_aps = []
        for mac_addr in self.expected_aps_info.keys():
            if mac_addr not in current_aps_info.keys():
                lost_aps.append(mac_addr)
                continue
            if current_aps_info[mac_addr]['status'] != self.expected_aps_info[mac_addr]['status']:
                error_aps.append(mac_addr)
                continue
        
        if lost_aps:
            self.errmsg = 'There are APs %s lost.' % lost_aps 
        if error_aps:
            self.errmsg += 'The APs %s have the information is not match with expected' % error_aps 
        
        if self.errmsg:
            return
        
        self.passmsg += '; all APs are reconnected as effected.'
    
    def _do_bangradar_on_active_ap(self):
        """
        """
        logging.info('Bang radar on the AP[%s]' % self.active_ap.base_mac_addr)
        lib.apcli.shell.set_bangradar(self.active_ap)
    
    def _verify_dfs_blocked_channel_on_active_ap(self):
        """
        """
        blocked_dfs_channels_info = lib.apcli.shell.get_blocked_dfs_channel(self.active_ap)['blocked_channels']
        logging.info('The current blocked channel on AP[%s]' % self.active_ap.base_mac_addr)
        logging.info(blocked_dfs_channels_info)
        blocked_dfs_channels = [int(info['channel']) for info in blocked_dfs_channels_info]
        
        if int(self.test_dfs_channel) not in blocked_dfs_channels:
            if self.conf['is_block_channel']:
                self.errmsg = 'Could not find the channel %s in the blocked list' % self.test_dfs_channel
            else:
                self.passmsg += '; the channel %s is not blocked as expected' % self.test_dfs_channel
            
        else:
            if self.conf['is_block_channel']:
                self.passmsg += '; the channel %s in the blocked list as expected' % self.test_dfs_channel
            else:
                self.errmsg = 'The channel %s is blocked unexpected' % self.test_dfs_channel    
        
        if self.errmsg: return
        
        if self.conf['is_block_channel']:
            for info in blocked_dfs_channels_info:
                if int(info['channel']) == int(self.test_dfs_channel):
                    if int(info['remain_time']) < (1800 - 20): # 20 seconds for gap between 2 steps
                        errmsg = 'The blocking time of channel %s should be around 1800 seconds instead of %s'
                        self.errmsg = errmsg % (info['channel'], info['remain_time'])
                        return
                    
                    self.passmsg += '; the blocking time is %s as expected' % info['remain_time']
                    break
            
            lib.zd.ap.cfg_ap(self.zd, self.active_ap.base_mac_addr, {'radio': 'na', 'channel': 'Auto'})
            try:
                lib.zd.ap.cfg_ap(self.zd, self.active_ap.base_mac_addr, {'radio': 'na', 'channel': self.test_dfs_channel})
                msg = 'Blocked dfs channel [%s] is applied to AP[%s] successfully'
                self.errmsg = msg % (self.test_dfs_channel, self.active_ap.base_mac_addr)
                return
            except:
                msg = 'can not apply the blocked channel %s to AP[%s]' % (info['channel'], self.active_ap.base_mac_addr)
                logging.info(msg)
                self.passmsg += '; %s ' % msg
                return
                               
    def _apply_a_dfs_channel_to_active_ap(self):
        """
        """
        blocked_dfs_channels_info = lib.apcli.shell.get_blocked_dfs_channel(self.active_ap)['blocked_channels']        
        blocked_dfs_channels = [int(info['channel']) for info in blocked_dfs_channels_info]
        logging.debug('The current blocked dfs channels: %s' % blocked_dfs_channels)
        for channel in self.dfs_mode['dfs_channels']:
            if int(channel) not in blocked_dfs_channels:
                try:
                    lib.zd.ap.cfg_ap(self.zd, self.active_ap.base_mac_addr, {'radio': 'na', 'channel': channel})
                    self.test_dfs_channel = channel
                    passmsg = 'Apply a dfs channel [%s] to AP[%s] successfully'
                    self.passmsg = passmsg % (channel, self.active_ap.base_mac_addr)
                    return
                except:
                    msg = 'Can not apply the channel %s to AP[%s]' % (channel, self.active_ap.base_mac_addr)
                    logging.info(msg)
                    pass
        
        self.errmsg = 'Can not apply any dfs channel to AP[%s]' % self.active_ap.base_mac_addr
        
    def _enable_dfs_channel_on_zd(self):
        """
        """ 
        zd_country_code = self.zd.get_country_code()['value']
        self.dfs_mode = self.zdcli.get_dfs_channel_by_country_code(zd_country_code)
        if not self.dfs_mode['allow_dfs']:
            self.errmsg = 'ZD under country code %s does not support dfs channel.' % zd_country_code
            return
        
        logging.debug('Select the "Optimize for Performance" option to enable dfs channel on APs.')
        lib.zd.sys.set_country_code(self.zd, {'channel_optimization': 'performance'})
        time.sleep(60) # waiting for the configuration apply to APs side
        