# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: The test script support to test edit an L3 ACL rule.
Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters:
            'target_station': the target station IP address
            'active_ap': the symbolic name of the active ap
            'testing_rule': the configuration of the rule will be test
            'new_rule_conf': the new configuration will be edited on the testing rule

   Result type: PASS/FAIL/ERROR
   Results:

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
        - Clean up the testing environment by remove all non default configuration on ZD,
        target station, and active AP.
        - Create an Open None WLAN

   2. Test:
        - Create ACL with the testing rule, apply to WLAN and verify:
            + The ACL configuration is applied to the ZD CLI
            + The ACL working well
        - Edit the testing rule follow the new configuration input, and verify:
            + The ACL configuration is applied to the ZD CLI
            + The ACL working well

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

class ZD_L3ACL_Rule_Editing(Test):
    required_components = []
    test_parameters = {}

    def config(self, conf):
        self._initTestParameters(conf)
        self._cfgZoneDirector()
        self._cfgTargetStation()
        self._updateTestParameters()

    def test(self):
        self._createL3ACL()

        self._testVerifyL3ACLFunctionality()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testEditingL3ACLRule()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testVerifyL3ACLFunctionality()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        logging.info("Remove all configuration on the Zone Director")
        lib.zd.wgs.remove_wlan_groups(self.zd)
        lib.zd.wlan.delete_all_wlans(self.zd)
        lib.zd.ac.delete_all_l3_acl_policies(self.zd)

        # Remove all wlan profiles on target station
        if self.target_station:
            self.target_station.remove_all_wlan()

    # Configuration
    def _initTestParameters(self, conf):
        self.conf = {}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.zd_cli = self.testbed.components['ZoneDirectorCLI']
        self.target_station = None

        self.test_wlan_conf = {'ssid':'TestingWLAN', 'auth':'open', 'encryption':'none'}
        self.test_l3acl_conf = {'name':'TestingACL', 'description': '', 'default_mode': 'deny-all', 'rules': []}
        self.testing_l3acl = self.test_l3acl_conf.copy()
        self.check_status_timeout = 180
        self.negative_check_status_timeout = 20
        self.break_time = 2
        self.dest_ip = '192.168.0.252'
        self.testing_rule = conf['testing_rule']
        self.new_rule_conf = conf['new_rule_conf']

        self.errmsg = ''
        self.passmsg = ''

    def _cfgZoneDirector(self):
        logging.info('Remove all configuration on the Zone Director')
        lib.zd.wgs.remove_wlan_groups(self.zd)
        lib.zd.wlan.delete_all_wlans(self.zd)
        lib.zd.ac.delete_all_l3_acl_policies(self.zd)

        logging.info('Create WLAN "%s" for testing' % self.test_wlan_conf['ssid'])
        lib.zd.wlan.create_wlan(self.zd, self.test_wlan_conf)
        self.wlan_id = self.zd_cli.get_wlan_id(self.test_wlan_conf['ssid'])

    def _applyL3ACLToWLAN(self, wlan_name, acl_name):
        logging.info('Apply the ACL policy "%s" to the WLAN "%s"' % (acl_name, wlan_name))
        lib.zd.wlan.edit_wlan(self.zd, wlan_name, {'l3_l4_acl_name': acl_name})

    def _cfgTargetStation(self):
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                                                           , self.testbed.components['Station']
                                                           , check_status_timeout = self.check_status_timeout
                                                           , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _updateTestParameters(self):
        self.test_l3acl_conf.update({'rules': [self.testing_rule]})

    # Testing
    def _createL3ACL(self):
        lib.zd.ac.create_l3_acl_policy(self.zd, self.test_l3acl_conf)
        # By default each L3/L4 ACL have 2 rules that allow all dns (order 1) and dhcp (order 2) traffics.
        # So the new rule be add with order from 3
        rule_conf_on_zd = lib.zd.ac.get_l3_acl_policy_cfg(self.zd, self.test_l3acl_conf['name'])['rules']
        self.original_rule_conf = {}
        for rule in rule_conf_on_zd:
            if rule['order'] == '3':
               self.original_rule_conf = rule
               self.expected_rule = rule

    def _testEditingL3ACLRule(self):
        lib.zd.ac.edit_l3_acl_rule(self.zd, self.test_l3acl_conf['name'], '3', self.new_rule_conf)
        edited_rule_conf_on_zd = lib.zd.ac.get_l3_acl_policy_cfg(self.zd, self.test_l3acl_conf['name'])['rules']
        self.edited_rule_conf = {}
        order = '3' if not self.new_rule_conf.has_key('order') else self.new_rule_conf['order']
        for rule in edited_rule_conf_on_zd:
            if rule['order'] == order:
               self.edited_rule_conf = rule
               self.expected_rule = rule

        # Verify the Rule information on WebUI to make sure it is changed
        for option in self.new_rule_conf.keys():
            if self.new_rule_conf[option] not in self.edited_rule_conf[option]:
                self.errmsg = 'The %s of rule [%s] is not be changed as expected [%s]'
                self.errmsg = self.errmsg % (option, self.edited_rule_conf[option], self.new_rule_conf[option])
                return

    def _testVerifyL3ACLFunctionality(self):
        logging.info('Verify the behavior of the ACL %s' % repr(self.testing_l3acl))
        self._applyL3ACLToWLAN(self.test_wlan_conf['ssid'], self.testing_l3acl['name'])

        self._verifyL3ACLConfiguration(self.testing_l3acl['name'])
        if self.errmsg: return

        self._verifyStationAssociation(self.test_wlan_conf)
        if self.errmsg: return

        self.passmsg = 'The ACL policy works correct behavior'

    def _verifyL3ACLConfiguration(self, acl_name):
        """
        Verify the configuration of the policy are the same on ZD WedUI, ZD CLI and AP CLI
        """
        acl_conf_on_zd_webui = lib.zd.ac.get_l3_acl_policy_cfg(self.zd, acl_name)
        acl_list_on_zd_cli = self.zd_cli.get_l3_acl_cfg()
        for acl_conf in acl_list_on_zd_cli:
            if acl_conf['name'] == acl_name:
                acl_conf_on_zd_cli = acl_conf
                break
        acl_id = acl_conf_on_zd_cli['id']

        # Compare between ZD WebUI and ZD CLI
        result, msg = self._compareACLConfBetweenOnZDWebUIAndUnderCLI(acl_conf_on_zd_webui, acl_conf_on_zd_cli)
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

    def _verifyStationAssociation(self, wlan_conf):
        # We need verify that client could access to network but could not ping when default mode is 'deny-all',
        # or client could ping when default mode id 'allow-all'
        errmsg = tmethod.assoc_station_with_ssid(self.target_station, wlan_conf, self.check_status_timeout)
        if errmsg:
            self.errmsg = errmsg
            return

        val, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout)
        if not val:
            self.errmsg = val2
            return
