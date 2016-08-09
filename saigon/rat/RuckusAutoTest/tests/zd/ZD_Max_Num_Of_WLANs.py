# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: This script is verify if we could create and delete max number of wlan on Zone Director
Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters: 'max_num_of_wlans': The maximum wlans that we could create
                    'target_station': the target wireless station ip address
                    'wlan_conf_list': list of wlan configuration dictionary to test with different wlan encryption.
                                      Default the test use the same encryption 'open - none' for all wlan
   
   Result type: PASS/FAIL/ERROR
   Results: 

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
            - Delete all wlan configuration on Zone Director and Station

   2. Test:
            - Verify if we could create max number of wlans
            - Verify if all wlans functionality works well by try to access to all wlans from station.
            - Verify if we could delete all wlan at the same time

   3. Cleanup:
            - Delete all wlan configuration on Zone Director and Station


   How it is tested?
            - Delete some of wlans during the test running --> the test should be Failed
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

class ZD_Max_Num_Of_WLANs(Test):
    required_components = ['ZoneDirector']
    test_parameters = {'max_num_of_wlans': 'The maximum wlans that we could create',
                       'target_station': 'the target wireless station ip address',
                       'wlan_conf_list': 'list of wlan configuration dictionary to test with different wlan encryption.'}

    def config(self, conf):
        self._initTestParameters(conf)
        self._cfgTargetStation()
        
    def test(self):
        self._testCreateMaxNumOfWLANs()
        if self.errmsg: return ('FAIL', self.errmsg)
        
        self._testWlansFunctionality()
        if self.errmsg: return('FAIL', self.errmsg)
        
        self._testDeleteAllWLANs()
        if self.errmsg: return('FAIL', self.errmsg)
        
        return ('PASS', self.passmsg)

    def cleanup(self):
        if self.target_station:
            self.target_station.remove_all_wlan()
        
        lib.zd.wlan.delete_all_wlans(self.zd)        
    
    def _initTestParameters(self, conf):
        self.conf = conf
        self.errmsg = ''
        self.passmsg = ''
        self.target_station = None
        self.active_ap = None
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.check_status_timeout = 180
        self.wlan_conf_list = []
        
        if conf.has_key('max_num_of_wlans') and conf['max_num_of_wlans']:
            self.max_num_of_wlans = conf['max_num_of_wlans']
        else:
            self.max_num_of_wlans = 32
        
        self._defineWlansConfig()
        
        lib.zd.wlan.delete_all_wlans(self.zd)
    
    def _testCreateMaxNumOfWLANs(self):
        self.errmsg = ''
        wlan_name_list_on_zd = []        
        
        lib.zdcli.set_wlan.create_multi_wlans(self.zdcli, self.wlan_conf_list)
        wlan_name_list_on_zd = lib.zd.wlan.get_wlan_list(self.zd)
        
        expected_ssids_list = [wlan_conf['ssid'] for wlan_conf in self.wlan_conf_list]
        diff_list = [ssid for ssid in wlan_name_list_on_zd if ssid not in expected_ssids_list]
       
        if len(wlan_name_list_on_zd) == self.max_num_of_wlans:
            if diff_list:
                msg = '%d WLANs are created but wlan(s) [%s] do(es) not match with the expected wlan list'
                msg = msg % (self.max_num_of_wlans, repr(wlan_name_list_on_zd))
                logging.info(msg)
                self.errmsg = msg
            else:
                msg = '%d WLANs are created successfully' % self.max_num_of_wlans
                logging.info(msg)
                self.passmsg = '%s' % msg
         
        else:
            msg = '%d WLANs are created instead of max [%d] WLANs' 
            msg = msg % (len(wlan_name_list_on_zd), self.max_num_of_wlans)
            self.errmsg = msg
    
    def _testDeleteAllWLANs(self):
        logging.info('Verify deleting all %d wlans at the same time' % self.max_num_of_wlans)
        self.errmsg = ''
        try:
            lib.zd.wlan.delete_all_wlans(self.zd)
            msg = 'Delete all of %d WLANs successfully' % self.max_num_of_wlans
            self.passmsg = '%s, %s' % (self.passmsg, msg)
        except Exception, e:
            logging.info('[Delete Error] - %s' % e.message)
            raise
    
    def _testWlansFunctionality(self):
        error_ssid_list = []
        
        logging.info('Uncheck all wlan member of Default wlan group')
        ssid_list = [wlan_conf['ssid'] for wlan_conf in self.wlan_conf_list]
        
        # Remove all wlan members out of Default group
        lib.zd.wgs.cfg_wlan_group_members(self.zd, 'Default', ssid_list, False)
        
        logging.info('Assign each wlan to default group and verify if client could be access to wlan')
        last_ssid = ''
        if self.conf.has_key('tested_wlan_list'):
            test_wlan_list = [self.wlan_conf_list[i] for i in self.conf['tested_wlan_list']] 
        else:
            test_wlan_list = self.wlan_conf_list
        for wlan_conf in test_wlan_list:
            if last_ssid:
                lib.zd.wgs.uncheck_default_wlan_member(self.zd, last_ssid)
                
            val = self._verify_wlanFunctionality(wlan_conf)
            if val:
                error_ssid_list.append(val)
            last_ssid = wlan_conf['ssid']
            
        if error_ssid_list:
            msg = 'Wlan(s) [%s] is(are) created but the station could not access to' % repr(error_ssid_list)
            logging.info(msg)
            self.errmsg = msg
        else:
            msg = 'Functionality test for %d WLANs is successfully' % self.max_num_of_wlans
            logging.info(msg)
            self.passmsg = '%s, %s' % (self.passmsg, msg)

    def _cfgTargetStation(self):
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                                                       , self.testbed.components['Station']
                                                       , check_status_timeout = self.check_status_timeout
                                                       , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _defineWlansConfig(self):
        if self.conf.has_key('wlan_conf_list') and self.conf['wlan_conf_list']:
            wlan_conf_list = self.conf['wlan_conf_list']
        else:
            wlan_conf_list = [{'auth':'open', 'encryption':'none','username':'','password':''}]
        
        count = 0
        while count < self.max_num_of_wlans:
            for wlan in wlan_conf_list:
                wlan_conf = wlan.copy()
                ssid = 'Wlan_options-Wlan%d' % count
                wlan_conf['ssid'] = ssid 
                self.wlan_conf_list.append(utils.generate_wlan_parameter(wlan_conf))
                count += 1
                if count == self.max_num_of_wlans:
                    break
        self.wlan_conf_list = sorted(self.wlan_conf_list)
    
    def _verify_wlanFunctionality(self, wlan_conf):
        logging.info('Verify wlan functionality for wlan %s' % wlan_conf['ssid'])
        # Assign wlan to Default wlan group to verify
        lib.zd.wgs.check_default_wlan_member(self.zd, wlan_conf['ssid'])
        time.sleep(3) # Sleep time for the ZD apply the confgiuration to APs
        
        self.target_station.remove_all_wlan()
        msg = tmethod.assoc_station_with_ssid(self.target_station, wlan_conf, self.check_status_timeout)            
        if msg:
            logging.info(msg)
            return wlan_conf['ssid']
     
        return None

