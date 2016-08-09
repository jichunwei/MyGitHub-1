"""
   Description: 
   @author: Kevin Tan
   @contact: kevin.tann@ruckuswireless.com
   @since: June 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters:
   
   Test procedure:
    1. Config:
        -         
    2. Test:
        - Verify if RAPS available/blocked/DFS blocked radar channels comparison are successful between ZD GUI and AP CLI 
    3. Cleanup:
        -
   
   Result type: PASS/FAIL
   Results: PASS: If the RAPS channel test successfully
            FAIL: If the RAPS channel test failed

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import time
import logging
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import lib_Debug as bugme

class CB_ZD_RAPS_Channel_Status_Check(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                            }

    def config(self, conf):
        self._init_test_parameter(conf)

    def test(self):
        logging.info('Compare the available/blocked/dfs-blocked 11-na channels between ZD WebUI and AP CLI')

        self._compare_channels_between_zd_and_ap()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        logging.info('Trigger DFS channel hop by radar radio burst and compare 11na channels between ZD WebUI and AP again')
        
        self._verify_dfs_enabled_on_zd()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        self.zd.clear_all_events()
        self._apply_fixed_dfs_channel_to_active_ap()
        self._do_bangradar_on_active_ap()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        self._verify_blocked_dfs_channel_event()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        time.sleep(60)
        self._compare_channels_between_zd_and_ap()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        self.passmsg = 'RAPS common channels and DFS channels verification successfully'
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_parameter(self, conf):
        self.conf = {'channel_type': 'fixed'}
        self.conf.update(conf)        
        self.errmsg = ''
        self.passmsg = ''
        self.dfs_mode = ''
        self.test_dfs_channel = ''
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.ap_mac_addr = self.active_ap.base_mac_addr.lower()

    def _compare_channels_between_zd_and_ap(self,):
        info = lib.zd.aps.get_ap_detail_by_mac_addr(self.zd, self.ap_mac_addr)
        if not info:
            self.errmsg += 'Get AP[%s] detail info by its MAC failed!' % self.ap_mac_addr 
            logging.info(self.errmsg)
            return
        
        radio = info['radio_na']
        if len(radio) == 0:
            self.errmsg += 'Get AP[%s] radio na info in ZD GUI failed!' % self.ap_mac_addr 
            logging.info(self.errmsg)
            return
        
        if radio['avail_channel'] == '':
            avail_channel_list = []
        else:
            avail_channel_list = radio['avail_channel'].split(',')

        if radio['block_channel'] == '':
            block_channel_list = []
        else:
            block_channel_list = radio['block_channel'].split(',')
        
        if radio['dfs_block_channel'] == '':
            dfs_block_channel_list = []
        else:
            dfs_block_channel_list = radio['dfs_block_channel'].split(',')
        
        chn_dict = self.active_ap.get_channel_availability()
        if chn_dict['avail_channel'] != avail_channel_list:
            self.errmsg += 'Available channel list in AP CLI %s and ZD GUI %s are different, ' % (chn_dict['avail_channel'], avail_channel_list)
        if chn_dict['block_channel'] != block_channel_list:
            self.errmsg += 'Block channel list in AP CLI %s and ZD GUI %s are different, ' % (chn_dict['block_channel'], block_channel_list)
        if chn_dict['dfs_block_channel'] != dfs_block_channel_list:
            self.errmsg += 'DFS block channel list in AP CLI %s and ZD GUI %s are different, ' % (chn_dict['dfs_block_channel'], dfs_block_channel_list)
        
        return

    def _verify_dfs_enabled_on_zd(self):
        """
        """ 
        zd_country_code = self.zd.get_country_code()['value']
        logging.info('Country code is %s' % zd_country_code)

        try:
            self.dfs_mode = self.zdcli.get_dfs_channel_by_country_code(zd_country_code)
        except:
            logging.info('Get DFS channels and non-DFS channels from ZDCLI failed, wait 120s and retrieve them again')
            time.sleep(120)
            self.dfs_mode = self.zdcli.get_dfs_channel_by_country_code(zd_country_code)

        logging.info('allow_dfs:%s, dfs_channels:%s, non-dfs-channels:%s' % (self.dfs_mode['allow_dfs'], 
                                                                             self.dfs_mode['dfs_channels'], 
                                                                             self.dfs_mode['non-dfs-channels']))

        if not self.dfs_mode['allow_dfs']:
            self.errmsg += 'ZD under country code %s does not support DFS channel, ' % zd_country_code
            return

    def _apply_fixed_dfs_channel_to_active_ap(self):
        """
        """
        ch_dict = lib.apcli.shell.get_blocked_dfs_channel(self.active_ap)
        blocked_dfs_channels_info = ch_dict.get('blocked_channels')         
        
        blocked_dfs_channels = [int(info['channel']) for info in blocked_dfs_channels_info]
        logging.info('Current blocked DFS channels are [%s]' % blocked_dfs_channels)
        
        for channel in self.dfs_mode['dfs_channels']:
            if int(channel)>100 and int(channel) not in blocked_dfs_channels:
                try:
                    #@ChenTao ZF-10195
                    lib.zd.ap.set_ap_device_info(self.zd, self.ap_mac_addr, {'device_name': 'RuckusAP'})
                    lib.zd.ap.cfg_ap(self.zd, self.ap_mac_addr, {'wlan_service': True, 'radio': 'na', 'channel': channel})
                    self.test_dfs_channel = channel
                    msg = 'Apply a dfs channel [%s] to AP[%s] successfully, '
                    logging.info(msg)
                    return
                except:
                    msg = 'Can not apply the channel %s to AP[%s], try again.' % (channel, self.ap_mac_addr)
                    logging.info(msg)
                    pass
        
        if not self.test_dfs_channel:
            self.errmsg = 'All allowed dfs channels are blocked in AP, '
        
        return

    def _do_bangradar_on_active_ap(self):
        """
        """
        logging.info('Bang radar on the AP[%s]' % self.ap_mac_addr)
        lib.apcli.shell.set_bangradar(self.active_ap)

    def _verify_blocked_dfs_channel_event(self):
        logging.info('Verify Block DFS channel events')
        #MSG_AP_dfs_radar_event={ap} detects radar burst on radio {radio} and channel {dfs-channel} goes into non-occupancy period.
        expected_event = self.zd.messages['MSG_AP_dfs_radar_event']
        expected_event = expected_event.replace("{ap}", r"AP[%s]" )
        expected_event = expected_event.replace("{radio}", r"[11a/n]")
        expected_event = expected_event.replace("{dfs-channel}", r"[%s]")

        expected_event = expected_event % (self.ap_mac_addr, self.test_dfs_channel)

        #@ZJ 2014121 Optimization ZF-11905
        t0 = time.time()
        while time.time() - t0 < 50:
            all_events_list = self.zd.getEvents()
            for event in all_events_list:
                if expected_event in event:
                    self.passmsg = '[Correct behavior] %s' % event
                    return
        #@ZJ 2014121 Optimization ZF-11905
        errmsg = '[Incorrect behavior] There is not any event about radar burst detection for channel "%s" on AP[%s], '
        self.errmsg += errmsg % (self.test_dfs_channel, self.ap_mac_addr)
        return
