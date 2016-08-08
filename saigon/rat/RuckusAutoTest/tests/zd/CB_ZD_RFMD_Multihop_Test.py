"""
   Description: 
   @author: Kevin Tan
   @contact: kevin.tann@ruckuswireless.com
   @since: August 2012

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

class CB_ZD_RFMD_Multihop_Test(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                            }

    def config(self, conf):
        self._init_test_parameter(conf)

    def test(self):
        self._verify_dfs_enabled_on_zd()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        logging.info('Change mesh AP from 1 hop to 2 hops by manual uplink selection')
        ap_cfg = {'mac_addr':self.mesh_ap_2.base_mac_addr, 'mesh_uplink_aps':[self.mesh_ap_1.base_mac_addr]}
        self.zd.set_ap_cfg(ap_cfg)
        
        self._verify_ap_status(self.mesh_ap_2, 'Mesh AP, 2 hops')
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        self.rfmd_dfs_test()
        
        logging.info('Recover to Mesh smart uplink selection, then 2 hops change to 1 hop ')
        ap_cfg = {'mac_addr':self.mesh_ap_2.base_mac_addr}
        self.zd.set_ap_cfg(ap_cfg)

        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_parameter(self, conf):
        self.conf = {'all_ap_rfmd': True}
        self.conf.update(conf)        
        self.errmsg = ''
        self.passmsg = ''
        self.root_dfs_channel = ''
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        self.root_ap   = self.carrierbag[self.conf['root_ap']]['ap_ins']
        self.mesh_ap_1 = self.carrierbag[self.conf['mesh_ap_1']]['ap_ins']
        self.mesh_ap_2 = self.carrierbag[self.conf['mesh_ap_2']]['ap_ins']

        self.root_ap.set_rfmd_option(True)
        self.mesh_ap_1.set_rfmd_option(True)
        self.mesh_ap_2.set_rfmd_option(True)

    def rfmd_dfs_test(self):
        ap_list = [self.root_ap, self.mesh_ap_1, self.mesh_ap_2]
        self._apply_fixed_dfs_channel_to_ap(ap_list)
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        self.zd.clear_all_events()

        if self.conf['all_ap_rfmd'] == True:
            logging.info('Test two Mesh APs(one is 1 hop, the other is 2 hops) detect RFMD radar event')
            rfmd_ap_list = [self.mesh_ap_1, self.mesh_ap_2]
            self.test_radar_event_all_ap_enable(rfmd_ap_list,event_gen=True)
        else:
            logging.info('Test two 2 hops Mesh AP and root AP detect RFMD radar event while 1 hop Mesh AP RFMD is disabled')
            self.mesh_ap_1.set_rfmd_option(False)
            self.test_radar_event_non_leaf_mesh_ap_disable()
            self.mesh_ap_1.set_rfmd_option(True)
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        self.verify_all_ap_status_after_rfmd()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        self._verify_dfs_channel_event()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        self._verify_dfs_blocked_channel_on_root_ap()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        self._verify_blocked_dfs_info_on_zd_and_ap()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def _verify_ap_status(self, ap, status = 'Mesh AP, 2 hops'):
        mac = ap.base_mac_addr
        ap_info={}

        time.sleep(120)
        wait_time=720
        t0=time.time()
        
        while True:
            current_time = time.time()
            if (current_time-t0)>wait_time:
                self.errmsg += 'AP[%s] still disconnected from ZD after change mesh status to [%s] after %d seconds' % (mac, status, wait_time)
                return
            try:
                ap_info= lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, mac)
                if status in ap_info['state']:
                    self.passmsg += 'AP[%s] successfully connect to ZD after change mesh status to [%s] after %d seconds' % (mac, status, (current_time-t0))
                    return

                time.sleep(5)
            except:
                pass

    def test_radar_event_all_ap_enable(self, rfmd_ap_list, event_gen = True):
        ap_list = [self.root_ap, self.mesh_ap_1, self.mesh_ap_2]
        for ap in ap_list:
            ap.goto_shell()

        interface = 'wifi1'
        cmd = "radartool -i %s rfmdsetradar 1" % interface
        for rfmd_ap in rfmd_ap_list:
            rfmd_ap.do_cmd(cmd, prompt = "#")

        list0 = self.root_ap.cmd("rfmd -d", 0, "#")
        list1 = self.mesh_ap_1.cmd("rfmd -d", 0, "#")
        list2 = self.mesh_ap_2.cmd("rfmd -d", 0, "#")

        for rfmd_ap in rfmd_ap_list:
            rfmd_mac = rfmd_ap.base_mac_addr
            res = False
            if event_gen:
                for event in list0:
                    if rfmd_mac.upper() in event:
                        res = True
                        break
                if res == False:
                    self.errmsg += 'RFMD radar event of AP[%s] is not shown on Root AP[%s], incorrect behavior!' % (rfmd_mac, self.root_ap.base_mac_addr)  
                    return
            else:
                for event in list0:
                    if rfmd_mac.upper() in event:
                        self.errmsg += 'RFMD radar event of AP[%s] is shown on Root AP[%s], incorrect behavior!' % (rfmd_mac, self.root_ap.base_mac_addr)
                        return

            if rfmd_ap != self.root_ap:
                if rfmd_ap == self.mesh_ap_1:
                    res=False
                    for event in list1:
                        if rfmd_mac.upper() in event:
                            res=True
                            break
                    if res==False:
                        self.errmsg += 'RFMD radar event of AP[%s] is not shown on RFMD Mesh AP[%s], incorrect behavior!' % (rfmd_mac, self.mesh_ap_1.base_mac_addr)
                        return
    
                    for event in list2:
                        if rfmd_mac.upper() in event:
                            self.errmsg += 'RFMD radar event of AP[%s] is shown on another Mesh AP[%s], incorrect behavior!' % (rfmd_mac, self.mesh_ap_2.base_mac_addr)
                            return
                else:
                    for event in list1:
                        if rfmd_mac.upper() in event:
                            self.errmsg += 'RFMD radar event of AP[%s] is shown on another Mesh AP[%s], incorrect behavior!' % (rfmd_mac, self.mesh_ap_1.base_mac_addr)
                            return
    
                    res=False
                    for event in list2:
                        if rfmd_mac.upper() in event:
                            res=True
                            break
                    if res==False:
                        self.errmsg += 'RFMD radar event of AP[%s] is not shown on RFMD Mesh AP[%s], incorrect behavior!' % (rfmd_mac, self.mesh_ap_2.base_mac_addr)
                        return
            else:
                for event in list1:
                    if rfmd_mac.upper() in event:
                        self.errmsg += 'RFMD radar event of AP[%s] is shown on another Mesh AP[%s], incorrect behavior!' % (rfmd_mac, self.mesh_ap_1.base_mac_addr)
                        return

                for event in list2:
                    if rfmd_mac.upper() in event:
                        self.errmsg += 'RFMD radar event of AP[%s] is shown on another Mesh AP[%s], incorrect behavior!' % (rfmd_mac, self.mesh_ap_2.base_mac_addr)
                        return

        for ap in ap_list:
            ap.exit_shell()

    def test_radar_event_non_leaf_mesh_ap_disable(self):
        ap_list = [self.root_ap, self.mesh_ap_1, self.mesh_ap_2]
        for ap in ap_list:
            ap.goto_shell()

        interface = 'wifi1'
        cmd = "radartool -i %s rfmdsetradar 1" % interface
        self.root_ap.do_cmd(cmd, prompt = "#")
        self.mesh_ap_2.do_cmd(cmd, prompt = "#")

        list0 = self.root_ap.cmd("rfmd -d", 0, "#")
        list1 = self.mesh_ap_1.cmd("rfmd -d", 0, "#")
        list2 = self.mesh_ap_2.cmd("rfmd -d", 0, "#")
        
        root_mac = self.root_ap.base_mac_addr
        mesh2_mac = self.mesh_ap_2.base_mac_addr
        
        #check event in Root AP
        res = False
        for event in list0:
            if root_mac.upper() in event and mesh2_mac.upper() in event:
                res = True
                break
        if res == False:
            self.errmsg += 'RFMD radar event of AP[%s] or [%s] is not shown on Root AP[%s], incorrect behavior!' % (root_mac, mesh2_mac, root_mac)  
            return

        #check event in Mesh AP 1 hop
        if len(list1) > 0:
            self.errmsg += 'RFMD radar event[%s, ...] of AP[%s] is not NULL, incorrect behavior!' % (list1[0], self.mesh_ap_1.base_mac_addr)
            return

        #check event in Mesh AP 2 hops
        res = False
        for event in list2:
            if mesh2_mac.upper() in event:
                res = True
                break
        if res == False:
            self.errmsg += 'RFMD radar event of AP[%s] is not shown on 2 hops Mesh AP[%s], incorrect behavior!' % (mesh2_mac, mesh2_mac)
            return

        for ap in ap_list:
            ap.exit_shell()

    def verify_all_ap_status_after_rfmd(self):
        ap_mac_list=self.testbed.get_aps_mac_list() 

        for mac in ap_mac_list:
            ap_info= lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, mac)
            if not ap_info['state'].lower().startswith('connected'):
                self.errmsg += 'AP[%s] disconnect from ZD after RFMD radar detected' % mac

    def _apply_fixed_dfs_channel_to_ap(self, ap_list):
        """
        """
        for ap in ap_list:
            mac = ap.base_mac_addr
            dfs_channel = ''
            
            blocked_dfs_channels_info = lib.apcli.shell.get_blocked_dfs_channel(ap)['blocked_channels']        
            blocked_dfs_channels = [int(info['channel']) for info in blocked_dfs_channels_info]
            logging.debug('The current blocked dfs channels on AP[%s]: %s' % (mac, blocked_dfs_channels))

            for channel in self.dfs_mode['dfs_channels']:
                if int(channel)>100 and int(channel) not in blocked_dfs_channels:
                    try:
                        lib.zd.ap.cfg_ap(self.zd, mac, {'wlan_service': True, 'radio': 'na', 'channel': channel})
                        
                        dfs_channel = channel
                        if mac == self.root_ap.base_mac_addr:
                            self.root_dfs_channel = channel
                        
                        break
                    except:
                        msg = 'Can not apply the channel %s to AP[%s], ' % (channel, mac)
                        self.errmsg += msg
                        logging.info(msg)
            
            if not dfs_channel:
                msg = 'All allowed dfs channels are blocked in AP[%s]' % mac
                self.errmsg += msg
                logging.info(msg)
                break
        
    def _apply_fixed_non_dfs_channel_to_ap(self, ap_list):
        """
        """
        for ap in ap_list:
            mac = ap.base_mac_addr
            dfs_channel = ''
            
            if len(self.dfs_mode['non-dfs-channels']) == 0:
                self.errmsg += 'non-dfs-channels is NULL, cannot apply any channel to AP[%s], ' % mac
                return
            
            channel = self.dfs_mode['non-dfs-channels'][0]
            try:
                lib.zd.ap.cfg_ap(self.zd, mac, {'wlan_service': True, 'radio': 'na', 'channel': channel})
            except:
                msg = 'Can not apply non DFS channel %s to AP[%s], ' % (channel, mac)
                self.errmsg += msg
                logging.info(msg)

    def _verify_dfs_enabled_on_zd(self):
        """
        """ 
        zd_country_code = self.zd.get_country_code()['value']
        self.dfs_mode = self.zdcli.get_dfs_channel_by_country_code(zd_country_code)
        if not self.dfs_mode['allow_dfs']:
            self.errmsg += 'ZD under country code %s does not support dfs channel, ' % zd_country_code
            return
        
    def _verify_dfs_blocked_channel_on_root_ap(self):
        """
        """
        blocked_dfs_channels_info = lib.apcli.shell.get_blocked_dfs_channel(self.root_ap)['blocked_channels']
        logging.info('The current blocked channel on AP[%s]' % self.root_ap.base_mac_addr)
        logging.info(blocked_dfs_channels_info)
        blocked_dfs_channels = [int(info['channel']) for info in blocked_dfs_channels_info]
        
        if int(self.root_dfs_channel) not in blocked_dfs_channels:
            self.errmsg = 'Could not find the channel %s in the blocked list, ' % self.root_dfs_channel
            return
        
        for info in blocked_dfs_channels_info:
            if int(info['channel']) == int(self.root_dfs_channel):
                if int(info['remain_time']) < (1800 - 300): # 300 seconds for gap between 2 steps
                    errmsg = 'The blocking time of channel %s should be around 1800 seconds instead of %s, '
                    self.errmsg = errmsg % (info['channel'], info['remain_time'])
                    return
                
                break

    def _verify_blocked_dfs_info_on_zd_and_ap(self):
        logging.info('RFMD DFS Info both on ZD and root AP CLI')
        mac = self.root_ap.base_mac_addr
        dfs_info_on_zd = self.zdcli.get_wlaninfo_dfs(mac)['nol']
        dfs_info_on_ap = lib.apcli.shell.get_blocked_dfs_channel(self.root_ap)['blocked_channels']
        
        logging.debug('Block DFS channel info on ZD %s' % dfs_info_on_zd)
        logging.debug('Block DFS channel info on AP %s' % dfs_info_on_ap)
        blocked_channels_on_ap = [int(ap_channel['channel']) for ap_channel in dfs_info_on_ap]
        blocked_channels_on_zd = [int(zd_channel[0]) for zd_channel in dfs_info_on_zd]

        if blocked_channels_on_ap.sort() != blocked_channels_on_zd.sort():
            self.errmsg = 'The DFS info is not synchronized between ZD[%s] and Root AP[%s], ' % (dfs_info_on_zd, dfs_info_on_ap)

    def _verify_dfs_channel_event(self):
        logging.info('RFMD DFS channel hop event verification')
        all_events = self.zd.getEvents()

        #MSG_AP_dfs_radar_event={ap} detects radar burst on radio {radio} and channel {dfs-channel} goes into non-occupancy period.
        expected_event = 'AP[%s] detects radar burst on radio [11a/n] and channel [%s] goes into non-occupancy period.'
        expected_event = self.zd.messages['MSG_AP_dfs_radar_event']
        expected_event = expected_event.replace("{ap}", r"AP[%s]" )
        expected_event = expected_event.replace("{radio}", r"[11a/n]")
        expected_event = expected_event.replace("{dfs-channel}", r"[%s]")
        
        mac = self.root_ap.base_mac_addr.lower()
        expected_event = expected_event % (mac, self.root_dfs_channel)

        for event in all_events:
            if expected_event in event:
                self.passmsg = '[Correct behavior] %s' % event
                return

        errmsg = '[Incorrect behavior] There is not any event about radar burst detection for channel "%s" on AP[%s], '
        self.errmsg += errmsg % (self.root_dfs_channel, mac)
