# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: The test script support to test create, clone, edit, remove and delete an L3 ACL policy.
Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters:
            'target_station': the target station IP address
            'active_ap': the symbolic name of the active ap
            'testcase': the testcase description. Ex: 'clone-acl', 'create-max-l3-acls'
            'max_entries': maximum number of ACL or Rules in an ACL,
                          only need in create max num of ACLs or max num of Rules.

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
             + If testcase is 'create-max-l3-acl': verify create max ACL policy
             + If testcase is 'create-max-rule-entries': create an ACL with max num of Rules
             + Or create an ACL (allowing the target station access to)
        - Apply the ACL to the WLAN and verify if the behavior is correct.
        - If testcase is 'delete-an-inuse-acl': verify if we could not delete an in used ACL
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
from RuckusAutoTest.components.ZoneDirectorCLI import ZoneDirectorCLI

class ZD_L3ACL_Option(Test):
    required_components = []
    test_parameters = {}

    def config(self, conf):
        self._initTestParameters(conf)
        self._cfgZoneDirector()
        self._cfgActiveAP()
        self._cfgTargetStation()
        self._updateTestParameters()

    def test(self):
        self._createL3ACL()

        if self.testcase == 'create-max-l3-acls':
            self._testCreateMaxL3ACLs()
            if self.errmsg: return ('FAIL', self.errmsg)

        if self.testcase == 'create-max-rule-entries':
            self._testVerifyCreateMaxRuleEntries()
            if self.errmsg: return ('FAIL', self.errmsg)

        self._testVerifyL3ACLFunctionality()
        if self.errmsg: return ('FAIL', self.errmsg)

        if self.testcase == 'remove-acl-out-a-wlan':
            self._testVerifyRemoveAnACLFromWLAN()
            if self.errmsg: return ('FAIL', self.errmsg)

        if self.testcase == 'delete-an-inuse-acl':
            self._testVerifyDeleteAnInUseACL()
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
        self.zd_cli = self.testbed.components['ZoneDirectorCLI']
        self.active_ap = None
        self.target_station = None

        self.test_wlan_conf = {'ssid':'TestingWLAN', 'auth':'open', 'encryption':'none'}
        self.test_l3acl_conf = {'name':'TestingACL', 'description': '', 'default_mode': 'deny-all', 'rules': []}
        self.test_wlan_group_name = 'TestingWLANGroup'
        self.test_l3acl_conf_list = []
        self.test_rule_list = []
        self.testing_l3acl = self.test_l3acl_conf.copy()
        self.non_acl_setting = 'No ACLs'
        self.check_status_timeout = 180
        self.negative_check_status_timeout = 20
        self.break_time = 2
        self.dest_ip = '192.168.0.252'

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
        self.wlan_id = self.zd_cli.get_wlan_id(self.test_wlan_conf['ssid'])
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

    def _applyL3ACLToWLAN(self, wlan_name, acl_name):
        logging.info('Apply the ACL policy "%s" to the WLAN "%s"' % (acl_name, wlan_name))
        lib.zd.wlan.edit_wlan(self.zd, wlan_name, {'l3_l4_acl_name': acl_name})

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

    def _defineMaxACLConf(self, max_num = 32):
        default = {'name': '', 'description': '', 'default_mode': 'deny-all', 'rules': []}
        acl_conf_list = []
        for idx in range(0, max_num, 2):
            idx_num = idx + 1
            for action in ['allow-all', 'deny-all']:
                acl_conf = default.copy()
                acl_conf.update({'name': 'L3 ACL %02d' % idx_num, 'default_mode': action})
                acl_conf_list.append(acl_conf)
                idx_num += 1
        return acl_conf_list
    #@auth:yuyanan @since:2014-11-17 bug:zf-10190
    def _defineMaxRuleEntries(self, max_num = 32):
        # Create list of max_num - 3 rule configurations
        from copy import deepcopy
        tmp_rule = {'dst_addr':''} 
        rule_list = []
        for i in range(0, max_num - 3):# Each of L3 ACL policy have 3 default rule already
            rule = deepcopy(tmp_rule)
            rule['dst_addr'] = '1.1.1.%s/24'%str(i+1)
            rule_list.append(rule)
        return rule_list

    def _updateTestParameters(self):
        self.test_l3acl_conf.update({'rules': []})
        if self.testcase == 'create-max-l3-acls':
            self.test_l3acl_conf_list = self._defineMaxACLConf(self.conf['max_entries'])
        if self.testcase == 'create-max-rule-entries':
            self.test_rule_list = self._defineMaxRuleEntries(self.conf['max_entries'])

    # Testing
    def _createL3ACL(self):
        if self.testcase == 'create-max-l3-acls': return
        lib.zd.ac.create_l3_acl_policy(self.zd, self.test_l3acl_conf)

    def _testCreateMaxL3ACLs(self):
        # Create maximum number of ACL policies
        try:
            lib.zd.ac.create_multi_l3_acl_policies(self.zd, self.test_l3acl_conf_list)
        except Exception, e:
            self.errmsg = e.message
            logging.info(self.errmsg)
            return

        # Check the total ACL policies are created on Zone Director
        expect_acl_name_list = [acl_conf['name'] for acl_conf in self.test_l3acl_conf_list]
        acl_name_list = lib.zd.ac.get_all_l3_acl_policies(self.zd)

        if not acl_name_list == expect_acl_name_list:
            diff_list = [acl_name for acl_name in expect_acl_name_list if acl_name not in acl_name_list]
            self.errmsg = '%d L3 ACL policies are created but not %s' % (len(acl_name_list), repr(diff_list))
            return

        # Verify if all ACL policy work correct behavior
        error_at_acl_policy = []
        for acl in self.test_l3acl_conf_list:
            logging.info("Remove all WLANs from the station")
            self.target_station.remove_all_wlan()

            logging.info('Verify the behavior of the ACL %s' % repr(acl))
            self._applyL3ACLToWLAN(self.test_wlan_conf['ssid'], acl['name'])
            self._verifyStationAssociation(self.test_wlan_conf, acl['default_mode'])
            if self.errmsg:
                error_at_acl_policy.append(acl['name'])
                self.errmsg = None

        if error_at_acl_policy:
            self.errmsg = '%d ACLs are created successfully but the behavior did not work well at %s'
            self.errmsg = self.errmsg % (len(self.test_l3acl_conf_list), repr(error_at_acl_policy))
            return

        self.passmsg = '%d L3 ACL policies are created successfully' % len(self.test_l3acl_conf_list)

    def _testVerifyCreateMaxRuleEntries(self):
        # Edit the existing ACL policy to add max num of Mac client entries
        lib.zd.ac.edit_l3_acl_policy(self.zd, self.test_l3acl_conf['name'], {'rules':self.test_rule_list})

        # Check the mac entry list of ACL policy
        acl_info_on_zd = lib.zd.ac.get_l3_acl_policy_cfg(self.zd, self.test_l3acl_conf['name'])
        rule_list = acl_info_on_zd['rules']

        # By default there are 2 rules existed on each of ACL policy. So the the list of rule on zd webui
        # will have 2 more than the expected list.
        if (len(rule_list) - len(self.test_rule_list)) != 2:
            self.errmsg = 'Only %s rules are created instead of %s'
            self.errmsg = self.errmsg % (len(rule_list) - 2, len(self.test_rule_list))

        self.passmsg = '%d Rule entries are added successfully' % len(rule_list)

    def _testVerifyL3ACLFunctionality(self):
        if self.testcase in ['create-max-l3-acls', 'create-max-rule-entries']: return

        logging.info('Verify the behavior of the ACL %s' % repr(self.testing_l3acl))
        self._applyL3ACLToWLAN(self.test_wlan_conf['ssid'], self.testing_l3acl['name'])

        self._verifyL3ACLConfiguration(self.testing_l3acl['name'])
        if self.errmsg: return

        self._verifyStationAssociation(self.test_wlan_conf, self.testing_l3acl['default_mode'])
        if self.errmsg: return

        self.passmsg = 'The ACL policy works correct behavior'

    def _testVerifyRemoveAnACLFromWLAN(self):
        logging.info('Remove the ACL policy out of WLAN "%s"' % self.test_wlan_conf['ssid'])
        lib.zd.wlan.edit_wlan(self.zd, self.test_wlan_conf['ssid'], {'l3_l4_acl_name': self.non_acl_setting})

        # Verify if the client could access to WLAN after the ACL policy is removed
        self._verifyStationAssociation(self.test_wlan_conf, 'allow-all')
        if self.errmsg:
            self.errmsg = '[Incorrect behavior] The ACL policy is removed but %s' % self.errmsg
            logging.info(self.errmsg)
            return

        # Verify if the ACL policy could be delete without any problem
        self._verifyDeleteL3ACL(True)
        if self.errmsg:
            self.errmsg = '[Incorrect behavior] The ACL policy is removed but %s' % self.errmsg
            logging.info(self.errmsg)
            return

        self.passmsg = 'The ACL policy is removed out the WLAN %s successfully' % (self.test_wlan_conf['ssid'])

    def _testVerifyDeleteAnInUseACL(self):
        # The test ACL policy still be used by the test WLAN, it could be not deleted
        self._verifyDeleteL3ACL(False)
        if self.errmsg:
            msg = '[Incorrect behavior] The ACL policy is used by WLAN "%s" but %s'
            msg = msg % (self.test_wlan_conf['ssid'], self.errmsg)
            logging.info(self.errmsg)
            return

        # Remove the ACL policy out of WLAN, it could be deleted
        logging.info('Remove the ACL policy out of WLAN "%s"' % self.test_wlan_conf['ssid'])
        lib.zd.wlan.edit_wlan(self.zd, self.test_wlan_conf['ssid'], {'l3_l4_acl_name': self.non_acl_setting})

        self._verifyDeleteL3ACL(True)
        if self.errmsg:
            self.errmsg = '[Incorrect behavior] The ACL policy is removed but %s' % self.errmsg
            logging.info(self.errmsg)
            return

        self.passmsg = 'The delete ACL option worked well'

    def _verifyL3ACLConfiguration(self, acl_name):
        """
        Verify the configuration of the policy are the same on ZD WedUI, ZD CLI and AP CLI
        """
        acl_conf_on_zd_webui = lib.zd.ac.get_l3_acl_policy_cfg(self.zd, acl_name)
        acl_list_on_zd_cli = self.zd_cli.get_l3_acl_cfg()
        acl_conf_on_zd_cli = {}
        for acl_conf in acl_list_on_zd_cli:
            if acl_conf['name'] == acl_name:
                acl_conf_on_zd_cli = acl_conf
                break
        if not acl_conf_on_zd_cli:
            self.errmsg = 'The ACL "%s" configuration is not applied to the ZD CLI' % acl_name
            return
        acl_id = acl_conf_on_zd_cli['id']

        try:
            acl_conf_on_ap_cli = self.active_ap.get_l3_acl_cfg('%s-%s' % (self.wlan_id, acl_id))
        except Exception, e:
            if 'There is no information about the policy' in e.message:
                self.errmsg = e.message
                return
            else:
                raise

        # Compare between ZD WebUI and ZD CLI
        result, msg = self._compareACLConfBetweenOnZDWebUIAndUnderCLI(acl_conf_on_zd_webui, acl_conf_on_zd_cli)
        if not result:
            self.errmsg = msg
            return

        # Compare between ZD WebUI and AP CLI
        result, msg = self._compareACLConfBetweenOnZDWebUIAndUnderCLI(acl_conf_on_zd_webui, acl_conf_on_ap_cli)
        if not result:
            self.errmsg = msg
            return

    def _compareACLConfBetweenOnZDWebUIAndUnderCLI(self, acl_conf_on_webui, acl_conf_on_cli):
        """
        """
        convert_mode_value = {'Pass':'allow-all', 'Block':'deny-all'}
        if convert_mode_value[acl_conf_on_cli['default_mode']] != acl_conf_on_webui['default_mode']:
            errmsg = 'The "Default mode" under CLI is "%s" is not appropriate with "%s" on WebUI'
            logging.info(errmsg)
            return (False, errmsg)

        return self._compareRulesBetweenOnZDWebUIAndUnderCLI(acl_conf_on_webui['rules'], acl_conf_on_cli['rules'])

    def _compareRulesBetweenOnZDWebUIAndUnderCLI(self, rules_on_webui, rules_on_cli):
        """
        """
        if len(rules_on_webui) != len(rules_on_cli):
            errmsg = 'There are %s rules be set on WebUI but only %s be applied to CLI'
            errmsg = errmsg % (len(rules_on_webui), len(rules_on_cli))
            return (False, errmsg)
        dict_of_rules_on_webui = {}
        dict_of_rules_on_cli = {}

        for rule in rules_on_webui:
            dict_of_rules_on_webui['%s' % rule['order']] = rule

        for rule in rules_on_cli:
            dict_of_rules_on_cli['%s' % rule['order']] = rule

        for order in dict_of_rules_on_webui.keys():
            rule_on_cli = dict_of_rules_on_cli[order]
            rule_on_webui = dict_of_rules_on_webui[order]
            self._updateRuleValue(rule_on_cli)
            if rule_on_cli['dst_addr'] != rule_on_webui['dst_addr']:
                errmsg = '[Rule %s]: The destination address on CLI is "%s" but "%s" on WebUI'
                errmsg = errmsg % (order, rule_on_cli['dst_addr'], rule_on_webui['dst_addr'])
                return (False, errmsg)
            if rule_on_cli['dst_port'] != rule_on_webui['dst_port']:
                errmsg = '[Rule %s]: The destination port on CLI is "%s" but "%s" on WebUI'
                errmsg = errmsg % (order, rule_on_cli['dst_port'], rule_on_webui['dst_port'])
                return (False, errmsg)
            if rule_on_cli['action'] != rule_on_webui['action']:
                errmsg = '[Rule %s]: The action on CLI is "%s" but "%s" on WebUI'
                errmsg = errmsg % (order, rule_on_cli['action'], rule_on_webui['action'])
                return (False, errmsg)
            if rule_on_cli['protocol'] not in rule_on_webui['protocol']:
                errmsg = '[Rule %s]: The protocol on CLI is "%s" but "%s" on WebUI'
                errmsg = errmsg % (order, rule_on_cli['protocol'], rule_on_webui['protocol'])
                return (False, errmsg)

        return (True, '')

    def _updateRuleValue(self, rule_conf):
        if rule_conf['dst_addr'] == '0.0.0.0/0':
            rule_conf['dst_addr'] = 'Any'
        if rule_conf['dst_port'] == '0':
            rule_conf['dst_port'] = 'Any'
        if rule_conf['protocol'] == '255':
            rule_conf['protocol'] = 'Any'
        rule_conf['action'] = {'Pass':'Allow', 'Block':'Deny'}[rule_conf['action']]

    def _verifyDeleteL3ACL(self, allow_delete = True):
        # The test ACL policy still be used by the test WLAN, it could be not deleted
        try:
            lib.zd.ac.delete_l3_acl_policy(self.zd, self.testing_l3acl['name'])
            if not allow_delete:
                self.errmsg = 'The ACL "%s" is deleted' % self.testing_l3acl['name']

        except Exception, e:
            if 'could not be deleted' in e.message:
                if allow_delete:
                    self.errmsg = '[Incorrect behavior] %s' % e.message
                    logging.info(self.errmsg)
                else:
                    logging.info('[Correct behavior] %s' % e.message)
            else:
                raise

    def _verifyStationAssociation(self, wlan_conf, policy = 'deny-all'):
        # We need verify that client could access to network but could not ping when default mode is 'deny-all',
        # or client could ping when default mode id 'allow-all'
        allow_ping = {'allow-all': True, 'deny-all': False}[policy]

        errmsg = tmethod.assoc_station_with_ssid(self.target_station, wlan_conf, self.check_status_timeout)
        if errmsg:
            self.errmsg = errmsg
            return

        val, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout)
        if not val:
            self.errmsg = val2
            return

        if allow_ping:
            self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.dest_ip)
        else:
            self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.dest_ip)

    # Clean up

    def _moveAPstoDefaultWlanGroups(self):
        for ap in self.testbed.components['AP']:
            ap_mac = ap.base_mac_addr
            support_radio = lib.zd.ap.get_supported_radio(self.zd, ap_mac)
            for radio in support_radio:
                lib.zd.ap.assign_to_wlan_group(self.zd, ap_mac, radio, 'Default')

