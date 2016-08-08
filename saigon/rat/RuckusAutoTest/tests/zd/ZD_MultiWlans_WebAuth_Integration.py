# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: 
Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters: 
   
   Result type: PASS/FAIL/ERROR
   Results: 

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:

   2. Test:

   3. Cleanup:


   How it is tested?
        
"""

import os
import re
import logging
import time

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib

class ZD_MultiWlans_WebAuth_Integration(Test):
    required_components = []
    test_parameters = {}

    def config(self, conf):
        self._initTestParameter(conf)
        self._cfgZoneDirector()
        self._cfgTargetStation()

    def test(self):
        # Verify station could access and be authenticated successfully on all wlans 
        self._verifyWebAuthWorkOnAllWlans()
        
        if self.errmsg: return ('FAIL', self.errmsg)
        return ('PASS', self.passmsg)

    def cleanup(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        #lib.zd.wlan.delete_all_wlans(self.zd)

        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)

        # Remove all wlan profiles on target station
        if self.target_station:
            self.target_station.remove_all_wlan()
    
    def _initTestParameter(self, conf):
        self.conf = {'target_station':'',
                     'wlan_config_set':'set_of_32_open_none_wlans',
                     'dest_ip':'192.168.0.252',
                     'tested_wlan_list': []
                     }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector'] 
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.target_station = None
        self.active_ap = None
        
        self.wlan_conf_list = tconfig.get_wlan_profile(self.conf['wlan_config_set'])
        test_conf = {'do_webauth': True}
        for wlan in self.wlan_conf_list:
            wlan.update(test_conf)  
        self.wlan_name_list = [wlan['ssid'] for wlan in self.wlan_conf_list] 
        
        self.check_status_timeout = 180
        self.break_time = 2
        self.test_wlan_number = 6
        self.errmsg = ''
        self.passmsg = ''
        
        self.authen_server = 'Local Database'
        self.username = 'testuser'
        self.password = 'testpassword'
        self.dest_ip = self.conf['dest_ip']

    def _cfgTargetStation(self):        
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                                                       , self.testbed.components['Station']
                                                       , check_status_timeout = self.check_status_timeout
                                                       , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _cfgZoneDirector(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        #lib.zd.wlan.delete_all_wlans(self.zd)

        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)


        self.zd.unblock_clients('')
        
        # Create wlans set for testing
#        lib.zd.wlan.create_multi_wlans(self.zd, self.wlan_conf_list)
        lib.zdcli.set_wlan.create_multi_wlans(self.zdcli, self.wlan_conf_list)
        tmethod8.pause_test_for(10, 'Wait for ZD to push config to the APs')

        # Create user for authentication
        self.zd.create_user(self.username, self.password)

    def _verifyStationAssociation(self, wlan_conf_list):  
        error_at_wlan = []
        for wlan in wlan_conf_list:
            self.target_station.remove_all_wlan()
            tmethod.assoc_station_with_ssid(self.target_station, wlan, self.check_status_timeout, self.break_time)
            val, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout, self.break_time)
            if not val:
                raise Exception(val2)
            sta_wifi_ip_addr = val1
            sta_wifi_mac_addr = val2
        
            errmsg, client_info = tmethod.verify_zd_client_is_unauthorized(self.zd, sta_wifi_ip_addr, sta_wifi_mac_addr,
                                                                       self.check_status_timeout)
            if errmsg:
                logging.info(errmsg)
                error_at_wlan.append(wlan['ssid'])
                continue
        
            errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.dest_ip)
            if errmsg:
                logging.info(errmsg)
                error_at_wlan.append(wlan['ssid'])
                continue
        
            logging.info("Perform Web Authentication on the target station %s" % self.conf['target_station'])
            arg = tconfig.get_web_auth_params(self.zd, self.username, self.password)
            self.target_station.perform_web_auth(arg)
        
            errmsg, client_info = tmethod.verify_zd_client_is_authorized(self.zd, self.username, sta_wifi_mac_addr,
                                                                     self.check_status_timeout)
            if errmsg:
                logging.info(errmsg)
                error_at_wlan.append(wlan['ssid'])
                continue
        
            errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.dest_ip)
            if errmsg:
                logging.info(errmsg)
                error_at_wlan.append(wlan['ssid'])
                continue
    
        return error_at_wlan

    def _verifyWebAuthWorkOnAllWlans(self):
        error_at_wlan = []
        # Remove all wlan members out of Default group
        lib.zd.wgs.cfg_wlan_group_members(self.zd, 'Default', self.wlan_name_list, False)
        last_asigned_wlans = []
        logging.info('Verify on wlans %s' % self.conf['tested_wlan_list'])      
        verify_wlan_conf_list = []
        for i in self.conf['tested_wlan_list']:                
            verify_wlan_conf_list.append(self.wlan_conf_list[i])
                    
        # Remove all assigned wlans out of Default group
        if last_asigned_wlans:
            lib.zd.wgs.cfg_wlan_group_members(self.zd, 'Default', last_asigned_wlans, False)
        # Apply the selected wlans to Default group for testing
        verify_wlan_name_list = [wlan['ssid'] for wlan in verify_wlan_conf_list]
        lib.zd.wgs.cfg_wlan_group_members(self.zd, 'Default', verify_wlan_name_list, True)
        last_asigned_wlans = verify_wlan_name_list
        
        # Verify on each of wlans
        val = self._verifyStationAssociation(verify_wlan_conf_list)
        error_at_wlan.extend(val)
        
        if error_at_wlan:
            self.errmsg = 'The Web Authentication option did not work on wlans %s' % str(error_at_wlan)
        else:
            self.passmsg = 'The Web Authentication option worked well on %d wlans' % len(self.wlan_conf_list)

