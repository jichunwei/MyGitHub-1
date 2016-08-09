# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description:
Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters: 'target_station': IP address of the target station
                    'active_ap': the AP symbolic name of the active AP. It is the Mesh AP or Root AP
                    'wlan_config_set': list of 32 WLAN configurations will be test. ]
                                       Default is list of 32 WLANs with 'Open - None' encryption.

   Result type: PASS/FAIL/ERROR
   Results:

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
        - Create 32 WLANs on the Zone Director base on the 'wlan_config_set'parameter.
   2. Test:
        - Create 2 L2 ACL that includes the MAC address of the target station:
            a.    "Allow": allow the target access to the network
            b.    "Deny": deny the target station association
        - Sequence, assign 32 WLANs to the Default group:
            a.    Apply the "Allow" policy to the WLAN and verify:
                i.    Target station could access to the network and get the correct IP.
            b.    Change the ACL to "Deny", verify:
                i.    Target station could not re access to the network.
   3. Cleanup:
        - Return all non-default setting on Zone Director

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

class ZD_MultiWlans_ACL_Integration(Test):
    required_components = ['RuckusAP', 'ZoneDirector']
    test_parameters = {'target_station': 'IP address of the target station',
                       'active_ap': 'the AP symbolic name of the active AP. It is the Mesh AP or Root AP',
                       'wlan_config_set': 'list of 32 WLAN configurations will be test.'}

    def config(self, conf):
        self._initTestParameter(conf)
        self._cfgTargetStation()
        self._cfgActiveAP()
        self._cfgZoneDirector()

    def test(self):
        # Create 2 ACL policy for testing
        self._create2ACLForTesting()

        logging.info('Verify the ACL policy that allows station access to net work')
        self._verifyL2ACLIntegration(self.allow_access_acl, True, self.check_status_timeout)
        if self.errmsg: return ('FAIL', self.errmsg)
        passmsg = self.passmsg

        logging.info('Verify the ACL policy that denies station access to net work')
        self._verifyL2ACLIntegration(self.deny_access_acl, False, self.negative_check_status_timeout)
        if self.errmsg: return ('FAIL', self.errmsg)
        passmsg = '%s, %s' % (passmsg, self.passmsg)

        return ('PASS', passmsg)

    def cleanup(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_wlan_group()
        #self.zd.remove_all_wlan()
        #self.zd.remove_all_cfg()
        #lib.zd.wlan.delete_all_wlans(self.zd)
        #self.zd.remove_all_acl_rules()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)

        # Remove all wlan profiles on target station
        if self.target_station:
            self.target_station.remove_all_wlan()

    def _initTestParameter(self, conf):
        self.conf = {'target_station':'',
                     'active_ap':'',
                     'wlan_config_set':'set_of_32_open_none_wlans', 
                     'tested_wlan_list': []}
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']
        self.target_station = None

        self.wlan_conf_list = tconfig.get_wlan_profile(self.conf['wlan_config_set'])
        self.wlan_name_list = [wlan['ssid'] for wlan in self.wlan_conf_list]
        self.check_status_timeout = 180
        self.negative_check_status_timeout = 20
        self.break_time = 2
        self.test_wlan_number = 6
        self.errmsg = ''
        self.passmsg = ''
        self.allow_access_acl = 'Allow Access'
        self.deny_access_acl = 'Deny Access'

    def _cfgTargetStation(self):
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                                                       , self.testbed.components['Station']
                                                       , check_status_timeout = self.check_status_timeout
                                                       , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

        # Get mac address of wireless adapter on the target station.
        # This address is used as the restricted mac address in an ACL rule
        sta_wifi_ip_addr = None
        self.sta_wifi_mac_addr = None
        try:
            sta_wifi_ip_addr, self.sta_wifi_mac_addr = self.target_station.get_wifi_addresses()
        except:
            raise Exception("Unable to get MAC address of the wireless adapter of the target station %s" % 
                            self.conf['target_station'])

    def _cfgZoneDirector(self):
        logging.info("Remove all configuration on the Zone Director")
        self.zd.unblock_clients('')
        #self.zd.remove_all_wlan_group()
        #lib.zd.wlan.delete_all_wlans(self.zd)
        #self.zd.remove_all_acl_rules()
        #self.zd.remove_all_cfg()        
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        # Create wlans set for testing
        lib.zd.wlan.create_multi_wlans(self.zd, self.wlan_conf_list)   
        tmethod8.pause_test_for(10, 'Wait for ZD to push config to the APs')
    
    def _cfgActiveAP(self):
        logging.info('Configure the active AP')
        if self.conf.has_key('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if not self.active_ap:
                raise Exception("Active AP (%s) not found in test bed" % self.conf['active_ap'])
            self.active_ap_mac = self.active_ap.get_base_mac().lower()

    def _remove_all_wlanOnNonActiveAPs(self):
        if self.active_ap:
            for ap in self.testbed.components['AP']:
                if ap is not self.active_ap:
                    logging.info("Remove all WLAN on non-active AP %s" % ap.ip_addr)
                    ap.remove_all_wlan()

            logging.info("Verify WLAN status on the active AP %s" % self.active_ap.ip_addr)
            if not self.active_ap.verify_wlan():
                raise Exception('Not all wlan are up on active AP %s' % self.active_ap.ip_addr)

    def _create2ACLForTesting(self):
        # Create 2 ACL policies which allow and deny access from target station.
        logging.info('Create the ACL that allows client access')
        self.zd.create_acl_rule([self.allow_access_acl], [self.sta_wifi_mac_addr], True)
        logging.info('Create the ACL that denies client access')
        self.zd.create_acl_rule([self.deny_access_acl], [self.sta_wifi_mac_addr], False)

    def _verifyStationAssociation(self, wlan_conf_list, alow_access = True, check_status_timeout = 180):
        error_at_wlan = []
        for wlan in wlan_conf_list:
            logging.info('Verify L2 ACL Option on wlan wlan %s [%s]' % (wlan['ssid'], str(wlan)))
            errmsg = tmethod.assoc_station_with_ssid(self.target_station, wlan, check_status_timeout)
            if errmsg and not alow_access:
                msg = '[Correct Behavior]: Station [%s] is not allowed and %s' % (self.sta_wifi_mac_addr, errmsg)
            elif errmsg and alow_access:
                msg = '[Incorrect Behavior]: Station [%s] is allowed but %s' % (self.sta_wifi_mac_addr, errmsg)
                error_at_wlan.append(wlan['ssid'])
            elif not errmsg and not alow_access:
                msg = '[Incorrect Behavior]: Station [%s] is not allowed but still connected to wlan %s successfully'
                msg = msg % (self.sta_wifi_mac_addr, wlan['ssid'])
                error_at_wlan.append(wlan['ssid'])
            elif not errmsg and alow_access:
                msg = '[Correct Behavior]: Station [%s] is allowed and connected to wlan %s successfully'
                msg = msg % (self.sta_wifi_mac_addr, wlan['ssid'])
            else:
                msg = ''
            logging.info(msg)

        return error_at_wlan

    def _verifyL2ACLIntegration(self, acl_name, allow_access, check_status_timeout):
        """
        """
        # Aplly the L2 ACL rule to verify wlan only
        lib.zd.wlan.edit_multi_wlans(self.zd, self.wlan_name_list, {'acl_name':acl_name})

        # Verify the policy on all wlans
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
        # Remove all wlans on the non active APs
        self._remove_all_wlanOnNonActiveAPs()

        # Verify station association
        val = self._verifyStationAssociation(verify_wlan_conf_list, allow_access, check_status_timeout)
        error_at_wlan.extend(val)

        if error_at_wlan:
            self.errmsg = 'The ACL policy "%s" did not work with wlans % s' % (acl_name, str(error_at_wlan))
        else:
            self.errmsg = ''
            self.passmsg = 'The ACL policy "%s" worked well with %d wlans' % (acl_name, len(self.wlan_conf_list))

