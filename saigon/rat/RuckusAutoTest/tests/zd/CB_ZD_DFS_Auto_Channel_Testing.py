"""
   Description: 
   @author: Kevin Tan
   @contact: kevin.tann@ruckuswireless.com
   @since: June 2012

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
import re
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import lib_Debug as bugme

class CB_ZD_DFS_Auto_Channel_Testing(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                            }

    def config(self, conf):
        self._init_test_parameter(conf)

    def test(self):
        #enabled DFS channel
        self._enable_dfs_channel_on_zd()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._apply_auto_dfs_channel_to_active_ap()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        self._verify_aps_info()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        active_ap_info = lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, self.active_ap.base_mac_addr)
        self.ap_mac_list=self.testbed.get_aps_mac_list() 

        if active_ap_info['state'].find('(Mesh AP')>0:
            self.passmsg += 'all aps connect to zd after %s [%s] change DFS channel, ' % (active_ap_info['state'], active_ap_info['mac'])
            return self.returnResult('PASS', self.passmsg)

        self.zd.clear_all_events()
        self._do_bangradar_on_active_ap()

        self._testBlockedDFSChannelEvent()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        if active_ap_info['state'].find('(Mesh AP')>0:
            #Mesh AP, all APs keep original stage after DFS channel changed 
            #wait all ap connect after country code change
            wait_time=2400
            t0=time.time()
    
            for mac in self.ap_mac_list:
                while True:
                    if time.time()-t0>wait_time:
                        return('FAIL','not all ap connect to zd after change mesh DFS channel %d seconds, '%wait_time)
                    try:
                        ap_info= lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, mac)
                        if ap_info['state'].lower().startswith('connected'):
                            break
                    except:
                        pass
        else:
            #Root/eMesh AP or non-Mesh AP, all APs keep original stage after DFS channel changed
            for mac in self.ap_mac_list:
                ap_info= lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, mac)
                if ap_info['state'].lower().startswith('connected'):
                    break
                else:
                    return('FAIL','not all ap connect to zd after change mesh DFS channel, AP info: MAC %s, status %s, '%(mac, ap_info['status']))

        self.passmsg += 'all aps connect to zd after %s [%s] change DFS channel, ' % (active_ap_info['state'], active_ap_info['mac'])
        
        self._verify_dfs_blocked_channel_on_active_ap()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._testSyncDFSInfo()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_parameter(self, conf):
        self.conf = {'is_block_channel': True}
        self.conf.update(conf)        
        self.errmsg = ''
        self.passmsg = ''
        self.test_dfs_channel = ''
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        if self.carrierbag.get('expected_aps_info'):
            self.expected_aps_info = self.carrierbag['expected_aps_info']
        else:
            self.expected_aps_info = lib.zd.aps.get_all_ap_briefs(self.zd)
            
        zd_country_code = self.zd.get_country_code()['value']
        self.dfs_mode = self.zdcli.get_dfs_channel_by_country_code(zd_country_code)
        if not self.dfs_mode['allow_dfs']:
            self.errmsg = 'ZD under country code %s does not support dfs channel, ' % zd_country_code
            return

    
    def _verify_aps_info(self):
        logging.debug('The expected APs info:\n %s' % pformat(self.expected_aps_info))
        current_aps_info = lib.zd.aps.get_all_ap_briefs(self.zd)
        logging.debug('The current APs info: \n %s' % pformat(current_aps_info))
               
        lost_aps = []
        error_aps = []
        for mac_addr in self.expected_aps_info.keys():
            if mac_addr not in current_aps_info.keys():
                lost_aps.append(mac_addr)
                continue
#            if current_aps_info[mac_addr]['state'] != self.expected_aps_info[mac_addr]['state']:
            if not current_aps_info[mac_addr]['state'].lower().startswith('connected'):
                error_aps.append(mac_addr)
                continue
        
        if lost_aps:
            self.errmsg = 'There are APs %s lost, ' % lost_aps 
        if error_aps:
            self.errmsg += 'The APs %s have the information is not match with expected, ' % error_aps 
        
        if self.errmsg:
            return
        
        self.passmsg += '; all APs are reconnected as effected.'
    
    def _do_bangradar_on_active_ap(self):
        """
        """
        logging.info('Bang radar on the AP[%s]' % self.active_ap.base_mac_addr)
        try:
            lib.apcli.shell.set_bangradar(self.active_ap) 
        except:
            logging.info('Exception occurred when bang radar on AP, try again')
            time.sleep(5)
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
                self.errmsg = 'Could not find the channel %s in the blocked list, ' % self.test_dfs_channel
            else:
                self.passmsg += '; the channel %s is not blocked as expected' % self.test_dfs_channel
            
        else:
            if self.conf['is_block_channel']:
                self.passmsg += '; the channel %s in the blocked list as expected' % self.test_dfs_channel
            else:
                self.errmsg = 'The channel %s is blocked unexpected, ' % self.test_dfs_channel    
        
        if self.errmsg: return
        
        if self.conf['is_block_channel']:
            for info in blocked_dfs_channels_info:
                if int(info['channel']) == int(self.test_dfs_channel):
                    if int(info['remain_time']) < (1800 - 45): # 45 seconds for gap between 2 steps
                        errmsg = 'The blocking time of channel %s should be around 1800 seconds instead of %s, '
                        self.errmsg = errmsg % (info['channel'], info['remain_time'])
                        return
                    
                    self.passmsg += '; the blocking time is %s as expected' % info['remain_time']
                    break
            
            lib.zd.ap.cfg_ap(self.zd, self.active_ap.base_mac_addr, {'wlan_service': True, 'radio': 'na', 'channel': 'Auto'})
            try:
                lib.zd.ap.cfg_ap(self.zd, self.active_ap.base_mac_addr, {'wlan_service': True, 'radio': 'na', 'channel': self.test_dfs_channel})
                msg = 'Blocked dfs channel [%s] is applied to AP[%s] successfully, '
                self.errmsg = msg % (self.test_dfs_channel, self.active_ap.base_mac_addr)
                return
            except:
                msg = 'can not apply the blocked channel %s to AP[%s], ' % (info['channel'], self.active_ap.base_mac_addr)
                logging.info(msg)
                self.passmsg += '; %s ' % msg
                return

    def _get11NAChannel(self, channel_info):
        channel = re.findall('(\d+)\s*.*\(11a/n', channel_info)
        if channel:
            return channel[0]
        else:
            raise Exception('There is no info of 11N/A channel on ZD WebUI')
                               
    def _apply_auto_dfs_channel_to_active_ap(self):
        """
        """
        logging.info('Test DFS with Auto Channel assignment')
        lib.zd.ap.cfg_ap(self.zd, self.active_ap.base_mac_addr, {'wlan_service': True, 'radio': 'na', 'channel': 'Auto'})

        ap_info = lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, self.active_ap.base_mac_addr)
        if 'Connected' not in ap_info['state']:
            self.errmsg = 'Can not apply any dfs channel to AP[%s] because of AP disconnected' % self.active_ap.base_mac_addr
            return
        if not ap_info['radio_channel']: # or 'Auto (11a/n' in ap_info['radio_channel']:
            self.errmsg = 'Can not apply any dfs channel to AP[%s] because of AP channel unexpected' % ap_info['channel']
            return

        logging.debug(ap_info['radio_channel'])
        current_channel_11na = self._get11NAChannel(ap_info['radio_channel'])
        if current_channel_11na in self.dfs_mode['dfs_channels']:
            self.test_dfs_channel = current_channel_11na
            self.passmsg = 'Apply auto dfs channel [%s] to AP[%s] successfully' % (current_channel_11na, self.active_ap.base_mac_addr)
            return

        #If auto value is not DFS allowed, change it to an available DFS channel first
        blocked_dfs_channels_info = lib.apcli.shell.get_blocked_dfs_channel(self.active_ap)['blocked_channels']        
        blocked_dfs_channels = [int(info['channel']) for info in blocked_dfs_channels_info]
        logging.debug('The current blocked dfs channels: %s' % blocked_dfs_channels)
        for channel in self.dfs_mode['dfs_channels']:
            if int(channel)>100 and int(channel) not in blocked_dfs_channels:
                try:
                    lib.zd.ap.cfg_ap(self.zd, self.active_ap.base_mac_addr, {'wlan_service': True, 'radio': 'na', 'channel': channel})
                    self.test_dfs_channel = channel
                    time.sleep(20)

                    #After set fixed DFS channel value, change it to Auto again 
                    logging.info('Test DFS with Auto Channel assignment with channel %s' % (channel))
                    lib.zd.ap.cfg_ap(self.zd, self.active_ap.base_mac_addr, {'wlan_service': True, 'radio': 'na', 'channel': 'Auto'})
                    self.passmsg += 'Apply fixed dfs channel [%s] to AP[%s] then change to auto channel successfully, ' % (channel, self.active_ap.base_mac_addr)
                    return
                except:
                    msg = 'Can not apply the fixed channel %s to AP[%s]' % (channel, self.active_ap.base_mac_addr)
                    logging.info(msg)
                    pass
        
        if self.test_dfs_channel == '':
            self.errmsg = 'All allowed dfs channel are blocked'
        else:
            self.errmsg = 'Can not apply any dfs channel to AP[%s]' % self.active_ap.base_mac_addr
        
    def _enable_dfs_channel_on_zd(self):
        """
        """ 
        zd_country_code = self.zd.get_country_code()['value']
        self.dfs_mode = self.zdcli.get_dfs_channel_by_country_code(zd_country_code)
        if not self.dfs_mode['allow_dfs']:
            self.errmsg = 'ZD under country code %s does not support dfs channel.' % zd_country_code
            return
        
#        logging.debug('Select the "Optimize for Performance" option to enable dfs channel on APs.')
#        lib.zd.sys.set_country_code(self.zd, {'channel_optimization': 'performance'})
#        time.sleep(60) # waiting for the configuration apply to APs side

    def _testSyncDFSInfo(self):
        logging.info('Test Sync DFS Info')
        dfs_info_on_zd = self.zdcli.get_wlaninfo_dfs(self.active_ap.base_mac_addr)['nol']
        dfs_info_on_ap = lib.apcli.shell.get_blocked_dfs_channel(self.active_ap)['blocked_channels']
        
        logging.debug('Block DFS channel info on ZD %s' % dfs_info_on_zd)
        logging.debug('Block DFS channel info on AP %s' % dfs_info_on_ap)
        blocked_channels_on_ap = [int(ap_channel['channel']) for ap_channel in dfs_info_on_ap]
        blocked_channels_on_zd = [int(zd_channel[0]) for zd_channel in dfs_info_on_zd]

        if blocked_channels_on_ap.sort() != blocked_channels_on_zd.sort():
            errmsg = 'The DFS info is not sync between ZD %s and AP %s'
            self.errmsg = 'The DFS info is not sync between ZD %s and AP %s, ' % (dfs_info_on_zd, dfs_info_on_ap)
            return

        self.passmsg += 'The DFS info on ZD %s is sync with on AP %s, ' % (dfs_info_on_zd, dfs_info_on_ap)

    def _testBlockedDFSChannelEvent(self):
        logging.info('Test Block DFS channel events')
        all_events = self.zd.getEvents()

        #MSG_AP_dfs_radar_event={ap} detects radar burst on radio {radio} and channel {dfs-channel} goes into non-occupancy period.
        expected_event = 'AP[%s] detects radar burst on radio [11a/n] and channel [%s] goes into non-occupancy period.'
        expected_event = self.zd.messages['MSG_AP_dfs_radar_event']
        expected_event = expected_event.replace("{ap}", r"AP[%s]" )
        expected_event = expected_event.replace("{radio}", r"[11a/n]")
        expected_event = expected_event.replace("{dfs-channel}", r"[%s]")

        expected_event = expected_event % (self.active_ap.base_mac_addr.lower(), self.test_dfs_channel)

        for event in all_events:
            if expected_event in event:
                self.passmsg = '[Correct behavior] %s' % event
                return

        errmsg = '[Incorrect behavior] There is not any event about radar burst detection for channel "%s" on AP[%s], '
        self.errmsg = errmsg % (self.test_dfs_channel, self.active_ap.base_mac_addr)
