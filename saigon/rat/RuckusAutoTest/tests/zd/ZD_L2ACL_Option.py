# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: The test script support to test create, clone, edit, remove and delete an L2 ACL policy.
Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters:
            'target_station': the target station IP address
            'active_ap': the symbolic name of the active ap
            'testcase': the testcase description. Ex: 'clone-acl', 'create-max-l2-acls'
            'max_entries': maximum number of ACL or MAC entries in an ACL,
                          only need in create max num of ACLs or max num of MAC entries.

   Result type: PASS/FAIL/ERROR
   Results:

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
        - Clean up the testing environment by remove all non default configuration on ZD,
        target station, and active AP.
        - Create an Open None WLAN, and apply the ACL to that WLAN to verify if it's behavior is correct
             + If the test case is 'apply-to-an-wlan' (2Ghz or 5Ghz):
                  Create an WLAN group that include the WLAN
                  Apply the active AP to wlan group in the appropriate radio.

   2. Test:
        - Create ACL to test:
             + If testcase is 'create-max-l2-acl': verify create max ACL policy
             + If testcase is 'create-max-mac-entries': create an ACL with max num of MAC entries
             + Or create an ACL (allowing the target station access to)
        - Apply the ACL to the WLAN and verify if the behavior is correct.
        - If testcase is 'clone-acl': clone the testing ACL and verify if the cloned ACL is work well
        - If testcase is 'edit-acl': change the policy of the testing ACL from allow to deny,
                                     and verify if the edited ACL works correct
        - If testcase is 'delete-an-in-used-acl': verify if we could not delete an in used ACL
        - If testcase is 'remove-an-acl-from-wlan': verify if we could remove the assgned ACL out of WLAN

   3. Cleanup:
        - Clean up the testing environment by remove all non default configuration on ZD,
        target station, and active AP.

   How it is tested?

"""

import logging
import time

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib

class ZD_L2ACL_Option(Test):
    required_components = []
    test_parameters = {}

    def config(self, conf):
        self._initTestParameters(conf)
        self._cfgZoneDirector()
        self._cfgActiveAP()
        self._cfgTargetStation()
        self._updateTestParameters()

    def test(self):
        self._createL2ACL()

        self._testCreateMaxL2ACLs()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testVerifyCreateMaxMacEntries()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testVerifyL2ACLFunctionality()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testVerifyEditACLPolicy()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testVerifyCloneACLPolicy()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testVerifyRemoveAnACLFromWLAN()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testVerifyDeleteAnInUsedACL()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        # Remove all wlan profiles on target station
        if self.target_station:
            self.target_station.remove_all_wlan()

    # Configuration
    def _initTestParameters(self, conf):
        self.conf = {}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.active_ap = None
        self.target_station = None

        self.test_wlan_conf = {'ssid':'Testing WLAN', 'auth':'open', 'encryption':'none'}
        self.test_l2acl_conf = {'acl_name':'Testing ACL', 'description': '', 'allowed_access': True, 'mac_list': []}
        self.test_wlan_group_name = 'Testing WLAN Group'
        self.test_l2acl_conf_list = []
        self.test_mac_client_list = []
        self.testing_l2acl = self.test_l2acl_conf.copy()
        self.non_acl_setting = 'No ACLs'
        self.check_status_timeout = 180
        self.negative_check_status_timeout = 20
        self.break_time = 2

        self.errmsg = ''
        self.passmsg = ''
        self.testcase = self.conf['testcase']

    def _cfgZoneDirector(self):
        logging.info('Remove all configuration on the Zone Director')
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        logging.info('Create WLAN "%s" for testing' % self.test_wlan_conf['ssid'])
        lib.zd.wlan.create_wlan(self.zd, self.test_wlan_conf)
        self._remove_all_wlanOnNonActiveAPs()
        if self.testcase == 'apply-to-wlan-for-5ghz':
            logging.info('Create WLAN Group "%s"' % self.test_wlan_group_name)
            lib.zd.wgs.create_wlan_group(self.zd, self.test_wlan_group_name, self.test_wlan_conf['ssid'])

    def _cfgActiveAP(self):
        if self.conf.has_key('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if not self.active_ap:
                raise Exception("Active AP (%s) not found in testbed" % self.conf['active_ap'])
            self.active_ap_mac = self.active_ap.base_mac_addr.lower()

            if self.testcase == 'apply-to-wlan-for-5ghz':
                if 'na' not in lib.zd.ap.get_supported_radio(self.zd, self.active_ap_mac):
                    raise Exception('The active AP "%s" does not support 5Ghz' % self.active_ap.ip_addr)

                logging.info('Apply the active AP to WLAN Group "%s"' % self.test_wlan_group_name)
                lib.zd.ap.assign_to_wlan_group(self.zd, self.active_ap_mac, 'na', self.test_wlan_group_name)

    def _applyL2ACLToWLAN(self, wlan_name, acl_name):
        logging.info('Apply the ACL policy "%s" to the WLAN "%s"' % (acl_name, wlan_name))
        lib.zd.wlan.edit_wlan(self.zd, wlan_name, {'acl_name': acl_name})

    def _remove_all_wlanOnNonActiveAPs(self):
        if self.active_ap:
            for ap in self.testbed.components['AP']:
                if ap is not self.active_ap:
                    logging.info("Remove all WLAN on non-active AP %s" % ap.ip_addr)
                    ap.remove_all_wlan()

            logging.info("Verify WLAN status on the active AP %s" % self.active_ap.ip_addr)
            if not self.active_ap.verify_wlan():
                raise Exception('Not all WLAN are up on active AP %s' % self.active_ap.ip_addr)

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
                            self.target_station.get_ip_addr())

    def _defineMaxACLConf(self, max_num = 32):
        default = {'acl_name': '', 'description': '', 'allowed_access': True, 'mac_list': [self.sta_wifi_mac_addr]}
        acl_conf_list = []
        for idx in range(0, max_num, 2):
            idx_num = idx + 1
            for policy in [True, False]:
                acl_conf = default.copy()
                acl_conf.update({'acl_name': 'L2 ACL %02d' % idx_num, 'allowed_access': policy})
                acl_conf_list.append(acl_conf)
                idx_num += 1
        return acl_conf_list

    def _defineMaxMacClientEntries(self, max_num = 128):
        mac_random = ''
        mac_client_list = [self.sta_wifi_mac_addr]
        for i in range(0, max_num - 1):
            for j in range(6):
                mac_random = mac_random + "%02x" % (i + j) + ":"
            mac_client_list.append(mac_random.rstrip(':'))
            mac_random = ''
        return mac_client_list

    def _updateTestParameters(self):
        self.test_l2acl_conf.update({'mac_list': [self.sta_wifi_mac_addr]})
        if self.testcase == 'create-max-l2-acls':
            self.test_l2acl_conf_list = self._defineMaxACLConf(self.conf['max_entries'])
        if self.testcase == 'create-max-mac-entries':
            self.test_mac_client_list = self._defineMaxMacClientEntries(self.conf['max_entries'])

    # Testing
    def _createL2ACL(self):
        if self.testcase == 'create-max-l2-acls': return
        lib.zd.ac.create_l2_acl_policy(self.zd, self.test_l2acl_conf)

    def _testCreateMaxL2ACLs(self):
        if self.testcase != 'create-max-l2-acls': return

        # Create maximum number of ACL policies
        try:
            lib.zd.ac.create_multi_l2_acl_policies(self.zd, self.test_l2acl_conf_list)
        except Exception, e:
            self.errmsg = e.message
            logging.info(self.errmsg)
            return

        # Check the total ACL policies are created on Zone Director
        expect_acl_name_list = [acl_conf['acl_name'] for acl_conf in self.test_l2acl_conf_list]
        acl_name_list = self.zd.get_all_acl_names()

        if not acl_name_list == expect_acl_name_list:
            diff_list = [acl_name for acl_name in expect_acl_name_list if acl_name not in acl_name_list]
            self.errmsg = '%d L2 ACL policies are created but not %s' % (len(acl_name_list), repr(diff_list))
            return

        # Verify if all ACL policy work correct behavior
        error_at_acl_policy = []
        for acl in self.test_l2acl_conf_list:
            logging.info("Remove all WLANs from the station")
            self.target_station.remove_all_wlan()

            logging.info('Verify the behavior of the ACL %s' % repr(acl))
            self._applyL2ACLToWLAN(self.test_wlan_conf['ssid'], acl['acl_name'])
            self._verifyStationAssociation(self.test_wlan_conf, acl['allowed_access'])
            if self.errmsg:
                error_at_acl_policy.append(acl['acl_name'])
                self.errmsg = None

        if error_at_acl_policy:
            self.errmsg = '%d ACLs are created successfully but the behavior did not work well at %s'
            self.errmsg = self.errmsg % (len(self.test_l2acl_conf_list), repr(error_at_acl_policy))
            return

        self.passmsg = '%d L2 ACL policies are created successfully' % len(self.test_l2acl_conf_list)

    def _testVerifyCreateMaxMacEntries(self):
        if self.testcase != 'create-max-mac-entries': return

        # Edit the existing ACL policy to add max num of Mac client entries
        lib.zd.ac.edit_l2_acl_policy(self.zd, self.test_l2acl_conf['acl_name'], {'mac_list':self.test_mac_client_list})

        # Check the mac entry list of ACL policy
        acl_info_on_zd = self.zd.get_acl_info(self.test_l2acl_conf['acl_name'])
        mac_client_list = acl_info_on_zd['mac_entries']
        if len(mac_client_list) == (self.test_mac_client_list):
            diff_list = [mac_client for mac_client in self.test_mac_client_list not in mac_client_list]
            self.errmsg = '%d MAC client entries are added but %s' % (len(mac_client_list), repr(diff_list))
            return

        self.passmsg = '%d MAC client entries are added successfully' % len(mac_client_list)

    def _testVerifyL2ACLFunctionality(self):
        if self.testcase == 'create-max-l2-acls': return

        logging.info('Verify the behavior of the ACL %s' % repr(self.testing_l2acl))
        self._applyL2ACLToWLAN(self.test_wlan_conf['ssid'], self.testing_l2acl['acl_name'])
        self._verifyStationAssociation(self.test_wlan_conf, self.testing_l2acl['allowed_access'])
        if self.errmsg:
            return

        self.passmsg = 'The ACL policy works correct behavior'

    def _testVerifyEditACLPolicy(self):
        if self.testcase != 'edit-acl': return

        # Change the policy of the ACL from allow to deny
        lib.zd.ac.edit_l2_acl_policy(self.zd, self.test_l2acl_conf['acl_name'], {'allowed_access': False})

        # Verify if the policy of the ACL is changed
        edited_acl_info = self.zd.get_acl_info(self.test_l2acl_conf['acl_name'])
        if edited_acl_info['policy'] != 'deny-all':
            self.errmsg = 'The policy of the L2 ACL "%s" is "%s" instead of "deny-all"'
            self.errmsg = self.errmsg % (self.test_l2acl_conf['acl_name'], edited_acl_info['policy'])
            logging.info(self.errmsg)
            return

        self.testing_l2acl = self.test_l2acl_conf.copy()
        self.testing_l2acl.update({'allowed_access': False})

        # Verify if the cloned ACL work correct behavior
        self._testVerifyL2ACLFunctionality()
        if self.errmsg: return

        self.passmsg = 'The ACL "%s" policy is changed successfully' % self.test_l2acl_conf['acl_name']

    def _testVerifyCloneACLPolicy(self):
        if self.testcase != 'clone-acl': return

        # Clone an existing ACL to a new ACL
        cloned_acl_conf = {'acl_name': 'Cloned L2 ACL'}
        lib.zd.ac.clone_l2_acl_policy(self.zd, self.test_l2acl_conf['acl_name'], cloned_acl_conf)

        # Verify if the cloned ACL exists on the ACL table
        if cloned_acl_conf['acl_name'] not in self.zd.get_all_acl_names():
            self.errmsg = 'The L2 ACL "%s" did not exist on the L2 ACL table after be cloned from "%s"'
            self.errmsg = self.errmsg % (cloned_acl_conf['acl_name'], self.test_l2acl_conf['acl_name'])
            logging.info(self.errmsg)
            return

        # Verify if the policy information of the cloned ACL.
        cloned_acl_info_on_zd = self.zd.get_acl_info(cloned_acl_conf['acl_name'])

        if {'deny-all':False, 'allow-all': True}[cloned_acl_info_on_zd['policy']] != self.test_l2acl_conf['allowed_access'] \
           or cloned_acl_info_on_zd['mac_entries'] != self.test_l2acl_conf['mac_list']:
            self.errmsg = 'The policy information on the cloned L2 ACL are %s in stead of %s'
            self.errmsg = self.errmsg % (repr([cloned_acl_info_on_zd['policy'], cloned_acl_info_on_zd['mac_entries']]),
                                         repr([self.test_l2acl_conf['allowed_access'], self.test_l2acl_conf['mac_list']]))
            logging.info(self.errmsg)
            return

        self.testing_l2acl = self.test_l2acl_conf.copy()
        self.testing_l2acl.update({'acl_name': cloned_acl_conf['acl_name']})

        # Verify if the cloned ACL work correct behavior
        self._testVerifyL2ACLFunctionality()
        if self.errmsg: return

        self.passmsg = 'The ACL "%s" is cloned to "%s" successfully' % (self.test_l2acl_conf['acl_name'], cloned_acl_conf['acl_name'])

    def _testVerifyRemoveAnACLFromWLAN(self):
        if self.testcase != 'remove-acl-out-a-wlan': return

        logging.info('Remove the ACL policy out of WLAN "%s"' % self.test_wlan_conf['ssid'])
        lib.zd.wlan.edit_wlan(self.zd, self.test_wlan_conf['ssid'], {'acl_name': self.non_acl_setting})

        # Verify if the client could access to WLAN after the ACL policy is removed
        self._verifyStationAssociation(self.test_wlan_conf, True)
        if self.errmsg:
            self.errmsg = '[Incorrect behavior] The ACL policy is removed but %s' % self.errmsg
            logging.info(self.errmsg)
            return

        # Verify if the ACL policy could be delete without any problem
        self._verifyDeleteL2ACL(True)
        if self.errmsg:
            self.errmsg = '[Incorrect behavior] The ACL policy is removed but %s' % self.errmsg
            logging.info(self.errmsg)
            return

        self.passmsg = 'The ACL policy is removed out the WLAN %s successfully' % (self.test_wlan_conf['ssid'])

    def _testVerifyDeleteAnInUsedACL(self):
        if self.testcase != 'delete-an-in-used-acl': return

        # The test ACL policy still be used by the test WLAN, it could be not deleted
        self._verifyDeleteL2ACL(False)
        if self.errmsg:
            msg = '[Incorrect behavior] The ACL policy is used by WLAN "%s" but %s'
            msg = msg % (self.test_wlan_conf['ssid'], self.errmsg)
            logging.info(self.errmsg)
            return

        # Remove the ACL policy out of WLAN, it could be deleted
        logging.info('Remove the ACL policy out of WLAN "%s"' % self.test_wlan_conf['ssid'])
        lib.zd.wlan.edit_wlan(self.zd, self.test_wlan_conf['ssid'], {'acl_name': self.non_acl_setting})

        self._verifyDeleteL2ACL(True)
        if self.errmsg:
            self.errmsg = '[Incorrect behavior] The ACL policy is removed but %s' % self.errmsg
            logging.info(self.errmsg)
            return

        self.passmsg = 'The delete ACL option worked well'

    def _verifyDeleteL2ACL(self, allow_delete = True):
        # The test ACL policy still be used by the test WLAN, it could be not deleted
        try:
            lib.zd.ac.delete_l2_acl_policy(self.zd, self.testing_l2acl['acl_name'])
            if not allow_delete:
                self.errmsg = 'The ACL "%s" is deleted' % self.testing_l2acl['acl_name']

        except Exception, e:
            if 'could not be deleted' in e.message:
                if allow_delete:
                    self.errmsg = '[Incorrect behavior] %s' % e.message
                    logging.info(self.errmsg)
                else:
                    logging.info('[Correct behavior] %s' % e.message)
            else:
                raise

    def _verifyStationAssociation(self, wlan_conf, allow_access = True):
        check_status_timeout = self.check_status_timeout if allow_access else self.negative_check_status_timeout

        errmsg = tmethod.assoc_station_with_ssid(self.target_station, wlan_conf, check_status_timeout)
        if errmsg and not allow_access:
            msg = '[Correct Behavior]: Station [%s] is not allowed and %s' % (self.sta_wifi_mac_addr, errmsg)
        elif errmsg and allow_access:
            msg = '[Incorrect Behavior]: Station [%s] is allowed but %s' % (self.sta_wifi_mac_addr, errmsg)
            self.errmsg = msg
        elif not errmsg and not allow_access:
            msg = '[Incorrect Behavior]: Station [%s] is not allowed but still connected to wlan %s successfully'
            msg = msg % (self.sta_wifi_mac_addr, wlan_conf['ssid'])
            self.errmsg = msg
        elif not errmsg and allow_access:
            msg = '[Correct Behavior]: Station [%s] is allowed and connected to wlan %s successfully'
            msg = msg % (self.sta_wifi_mac_addr, wlan_conf['ssid'])
        else:
            msg = ''

        logging.info(msg)

    # Clean up

    def _moveAPstoDefaultWlanGroups(self):
        for ap in self.testbed.components['AP']:
            ap_mac = ap.base_mac_addr
            support_radio = lib.zd.ap.get_supported_radio(self.zd, ap_mac)
            for radio in support_radio:
                lib.zd.ap.assign_to_wlan_group(self.zd, ap_mac, radio, 'Default')

