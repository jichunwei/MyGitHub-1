# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: This script is use for verify create(max length of wlan name)/clone/edit wlan
Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters: 'testing_feature': the wlan feature will be tested
                    'target_station': the wireless station ip address
   
   Result type: PASS/FAIL/ERROR

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
            - Delete all wlan configuration on Zone Director and Station
   2. Test:
            - Try to create/clone/edit wlan base on the feature be tested
            - Verify the behavior of those feature is correct

   3. Cleanup:
            - Delete all wlan configuration on Zone Director and Station

   How it is tested?
"""

import os
import re
import random
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8

class ZD_WLAN_Options(Test):
    required_components = ['ZoneDirector']
    test_parameters = {'testing_feature': 'the wlan feature will be tested',
                       'target_station': 'the wireless station ip address'}

    def config(self, conf):
        self._initTestParameters(conf)
        self._cfgTargetStation()

    def test(self):
        if self.testing_feature == 'max length wlan':
            self._testMaxLengthWLAN()            
        elif self.testing_feature == 'clone wlan':            
            self._testCloneWLAN()
        elif self.testing_feature == 'edit wlan':
            self._testEditWLAN()
        elif self.testing_feature == 'random length wlan':
            self._testRandomLengthWLAN()
        elif self.testing_feature == 'min length wlan':
            self._testMinLengthWLAN()
        elif self.testing_feature == 'ex max length wlan':
            self._testExMaxLengthWLAN()
        else:
            raise Exception('The test option "%s" is not valid')

        if self.errmsg: return ('FAIL', self.errmsg)
        else: return ('PASS', self.passmsg)
    
    def cleanup(self):
        if self.target_station:
            self.target_station.remove_all_wlan()
        
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        
    
    def _initTestParameters(self, conf):
        self.conf = conf
        self.errmsg = ''
        self.passmsg = ''
        self.target_station = None
        self.zd = self.testbed.components['ZoneDirector']
        self.check_status_timeout = 180
        self.max_length = 32
        self.testing_feature = ''
        self.wlan_conf = {'ssid': '', 'encryption':'none', 'auth':'open', 'wpa_ver':'',
                          'sta_auth':'open', 'sta_wpa_ver':'', 'sta_encryption':'none',
                          'key_index':'', 'key_string':'', 'username':'', 'password':'',
                          'ras_addr':'', 'ras_port':'', 'ras_secret':'', 'use_radius':''}
        self.testing_wlan_conf = {'ssid':'', 'auth':'shared', 'encryption':'WEP-64',
                                  'key_index':'1' , 'key_string':utils.make_random_string(10, "hex")}
        self.valid_chars = 'abcdefghiklmnopqrstuvwxyzABCDEFGHILKMNOPQRSTUVWXYZ0123456789-_'
        
        if conf.has_key('testing_feature') and conf['testing_feature']:
            self.testing_feature = conf['testing_feature'].lower()
            
        self._cfgZoneDirector()
        self._cfgTargetStation()
    
    def _verifyWLANOption(self, option, wlan_conf, new_wlan_conf = {}, is_allowed = True):
        self.errmsg = ''
        exmsg = ''
        try:
            if option == 'create':
                lib.zd.wlan.create_wlan(self.zd, wlan_conf)                
            elif option == 'clone':
                lib.zd.wlan.clone_wlan(self.zd, wlan_conf['ssid'], new_wlan_conf)
            elif option == 'edit':
                lib.zd.wlan.edit_wlan(self.zd, wlan_conf['ssid'], new_wlan_conf)            
            allowed = True
        except Exception, e:
            if 'already exists. Please enter a different name' in e.message:
                exmsg = e.message
                allowed = False
            else:
                raise
        
        if is_allowed and not allowed:
            msg = '[Configuration failed][Incorrect behavior]: %s' % exmsg
            logging.info(msg)
            self.errmsg = msg
        if is_allowed and allowed:
            msg = '[Configuration successfully][Correct behavior]'
            logging.info(msg)            

        if not is_allowed and allowed:
            msg = '[Configuration successfully][Incorrect behavior]'
            logging.info(msg)
            self.errmsg = msg
        if not is_allowed and not allowed:
            msg = '[Configuration failed][Correct behavior]: %s' % exmsg
            logging.info(msg)
    
    def _testMaxLengthWLAN(self):
        self.errmsg = ''
        valid_ssid_with_max_length = ''.join([random.choice(self.valid_chars) for x in range(0, self.max_length)])
        self.wlan_conf['ssid'] = valid_ssid_with_max_length
        try:
            lib.zd.wlan.create_wlan(self.zd, self.wlan_conf)
        except Exception, e:
            if 'can only contain between 2 and 32 characters' in e.message:
                msg = 'Could not create the WLAN [%s] with %d characters' 
                msg = msg % valid_ssid_with_max_length, len(valid_ssid_with_max_length)
                self.errmsg = msg
                return
            else:
                raise           

        msg = tmethod.assoc_station_with_ssid(self.target_station, self.wlan_conf, self.check_status_timeout)
        if msg:
            self.errmsg = 'WLAN %s is created successfully but %s' % (self.wlan_conf['ssid'], msg)
        else:
            msg = 'WLAN [%s] with %d chars is created and station could access to this WLAN' 
            msg = msg % (valid_ssid_with_max_length, self.max_length)
            self.passmsg = msg
            
    def _testMinLengthWLAN(self):
        self.errmsg = ''
        valid_ssid_with_random_length = ''.join([random.choice(self.valid_chars) for x in range(0, 1)])
        self.wlan_conf['ssid'] = valid_ssid_with_random_length
        try:
            lib.zd.wlan.create_wlan(self.zd, self.wlan_conf)
        except Exception, e:
            if 'can only contain between 2 and 32 characters' in e.message:
                msg = 'Could not create the WLAN [%s] with %d characters' 
                msg = msg % valid_ssid_with_random_length, len(valid_ssid_with_random_length)
                self.errmsg = msg
                return
            else:
                raise           

        msg = tmethod.assoc_station_with_ssid(self.target_station, self.wlan_conf, self.check_status_timeout)
        if msg:
            self.errmsg = 'WLAN %s is created successfully but %s' % (self.wlan_conf['ssid'], msg)
        else:
            msg = 'WLAN [%s] with %d chars is created and station could access to this WLAN' 
            msg = msg % (valid_ssid_with_random_length, self.max_length)
            self.passmsg = msg
            
    def _testRandomLengthWLAN(self):
        self.errmsg = ''
        valid_ssid_with_random_length = ''.join([random.choice(self.valid_chars) for x in range(0, random.randint(1, self.max_length))])
        self.wlan_conf['ssid'] = valid_ssid_with_random_length
        try:
            lib.zd.wlan.create_wlan(self.zd, self.wlan_conf)
        except Exception, e:
            if 'can only contain between 2 and 32 characters' in e.message:
                msg = 'Could not create the WLAN [%s] with %d characters' 
                msg = msg % valid_ssid_with_random_length, len(valid_ssid_with_random_length)
                self.errmsg = msg
                return
            else:
                raise           

        msg = tmethod.assoc_station_with_ssid(self.target_station, self.wlan_conf, self.check_status_timeout)
        if msg:
            self.errmsg = 'WLAN %s is created successfully but %s' % (self.wlan_conf['ssid'], msg)
        else:
            msg = 'WLAN [%s] with %d chars is created and station could access to this WLAN' 
            msg = msg % (valid_ssid_with_random_length, self.max_length)
            self.passmsg = msg

    def _testExMaxLengthWLAN(self):
        self.errmsg = ''
        valid_ssid_with_max_length = ''.join([random.choice(self.valid_chars) for x in range(0, self.max_length+random.randint(0,self.max_length))])
        self.wlan_conf['ssid'] = valid_ssid_with_max_length
        try:
            lib.zd.wlan.create_wlan(self.zd, self.wlan_conf)
        except Exception, e:
            if 'can only contain between 1 and 32 characters' in e.message:
                pass
            elif ('Can not set value "%s" to the element "//input[@id=\'name\']"' % (self.wlan_conf['ssid'])) in e.message:
                pass
            else:
                self.errmsg = e.message   

        if not self.errmsg:
            msg = 'WLAN [%s] with %d chars cannot be created, which is correct' 
            msg = msg % (valid_ssid_with_max_length, self.max_length)
            self.passmsg = msg
    
    def _testCloneWLAN(self):
        self.errmsg = ''
        logging.info('Clone wlan %s use same configuration with the clonning wlan' % self.wlan_to_clone['ssid'])
        self._verifyWLANOption('clone', self.wlan_to_clone, self.wlan_to_clone, False)
        if self.errmsg: return
        
        logging.info('Clone wlan  %s use same ssid but different configuration with the clonning wlan'\
                     % self.wlan_to_clone['ssid'])
        new_wlan_conf = self.testing_wlan_conf.copy()
        new_wlan_conf['ssid'] = self.wlan_to_clone['ssid']
        self._verifyWLANOption('clone', self.wlan_to_clone, new_wlan_conf, False)
        if self.errmsg: return
        
        logging.info('Clone wlan %s use different SSID but same configuration with the clonning wlan'\
                     % self.wlan_to_clone['ssid'])
        new_wlan_conf = self.wlan_to_clone.copy()
        new_wlan_conf['ssid'] = 'Clone wlan with diff ssid'
        self._verifyWLANOption('clone', self.wlan_to_clone, new_wlan_conf, True)
        if self.errmsg: return
        
        logging.info('Clone wlan %s use different configuration with the clonning wlan' % self.wlan_to_clone['ssid'])
        new_wlan_conf = self.testing_wlan_conf.copy()
        new_wlan_conf['ssid'] = 'Clone wlan with diff conf'
        self._verifyWLANOption('clone', self.wlan_to_clone, new_wlan_conf, True)
        if self.errmsg: return
        
        self.passmsg = 'WLAN option - Clone wlan works well'
    
    def _testEditWLAN(self):
        self.errmsg = ''
        
        logging.info('Edit wlan %s to change to different encryption' % self.wlan_to_edit['ssid'])
        new_wlan_conf = self.testing_wlan_conf
        new_wlan_conf['ssid'] = self.wlan_to_edit['ssid']
        self._verifyWLANOption('edit', self.wlan_to_edit, new_wlan_conf, True)
        if self.errmsg: return
        
        logging.info('Edit wlan "%s" use same configuration with the existing wlan "%s"'\
                     % (self.wlan_to_edit['ssid'], self.wlan_to_compare['ssid']))
        new_wlan_conf = self.wlan_to_compare.copy()
        self._verifyWLANOption('edit', self.wlan_to_edit, new_wlan_conf, False)
        if self.errmsg: return
        
        logging.info('Edit wlan "%s" use same ssid the existing wlan "%s"'\
                     % (self.wlan_to_edit['ssid'], self.wlan_to_compare['ssid']))
        new_wlan_conf = self.testing_wlan_conf
        new_wlan_conf['ssid'] = self.wlan_to_compare['ssid']
        self._verifyWLANOption('edit', self.wlan_to_edit, new_wlan_conf, False)
        if self.errmsg: return
        
        logging.info('Edit wlan %s use different configuration with the editting wlan and the existing one' % \
                     self.wlan_to_edit['ssid'])
        new_wlan_conf = self.testing_wlan_conf
        new_wlan_conf['ssid'] = 'Edit with diff config'
        self._verifyWLANOption('edit', self.wlan_to_edit, new_wlan_conf, True)
        if self.errmsg: return
        
        self.passmsg = 'WLAN option - Edit wlan works well'
    
    def _cfgTargetStation(self):
        if not self.conf.has_key('target_station'): return
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                                                       , self.testbed.components['Station']
                                                       , check_status_timeout = self.check_status_timeout
                                                       , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])
    
    def _cfgZoneDirector(self):        
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        
            
        if self.testing_feature == 'edit wlan':
            # Create 2 wlan to verify the edit wlan feature
            self.wlan_to_edit = self.wlan_conf.copy()
            self.wlan_to_edit['ssid'] = 'Wlan to edit'
            lib.zd.wlan.create_wlan(self.zd, self.wlan_to_edit)
            
            self.wlan_to_compare = self.wlan_conf.copy()
            self.wlan_to_compare['ssid'] = 'Wlan to compare'
            lib.zd.wlan.create_wlan(self.zd, self.wlan_to_compare)
            
        if self.testing_feature == 'clone wlan':
            # Create 1 wlan to verify the clone wlan feature
            self.wlan_to_clone = self.wlan_conf.copy()
            self.wlan_to_clone['ssid'] = 'Wlan to clone'
            lib.zd.wlan.create_wlan(self.zd, self.wlan_to_clone)
