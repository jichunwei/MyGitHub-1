"""
Description: Test ZoneDirector SNMP WebUI Configuration

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'ZoneDirector'
   Test parameters: 'snmp_agent_cfg': 'a dictionary of SNMP Agent configuration'
                    'snmp_trap_cfg' : 'a dictionary of SNMP Trap configuration'
                    'max_len'       : 'maximum characters support for SNMP settings fields'

   Result type: PASS/FAIL
   Results: PASS: the valid configuration can apply to ZD correctly
            FAIL: - the valid configuration can't apply to ZD.
                  - the valid configuration can apply to ZD.

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Save current SNMP settings on ZD

   2. Test:
       - Test Enable SNMP Agent
       - Test Disable SNMP Agent
       - Test Edit SNMP Agent Contact Field (test valid length, maximum support length, exceed maximum support length)
       - Test Edit SNMP Location Field (test valid length, maximum support length, exceed maximum support length)
       - Test Edit SNMP RO Community Field (test valid length, maximum support length, exceed maximum support length)
       - Test Edit SNMP RW Community Field (test valid length, maximum support length, exceed maximum support length)

   3. Cleanup:
       - Restore SNMP settings on ZD
"""

import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.LinuxPC import *
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.zd import snmp_hlp as snmphlp


class ZD_SNMP_WebUI(Test):
    required_components = ['Station', 'ZoneDirector']
    parameter_description = {'snmp_agent_cfg': 'a dictionary of SNMP Agent configuration',
                           'snmp_trap_cfg': 'a dictionary of SNMP Trap configuration',
                           'max_len': 'maximum characters support for SNMP settings fields'
                          }

    def config(self, conf):
        self._cfgInitTestParams(conf)
        self._cfgSaveSNMPSettings()

    def test(self):
        # test SNMP Agent WebUI Configuration
        self._testEnableSNMPAgent()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._testDisableSNMPAgent()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._testEditSNMPAgentField('contact')
        if self.errmsg: return ("FAIL", self.errmsg)
        self._testEditSNMPAgentField('location')
        if self.errmsg: return ("FAIL", self.errmsg)
        self._testEditSNMPAgentField('ro_community')
        if self.errmsg: return ("FAIL", self.errmsg)
        self._testEditSNMPAgentField('rw_community')
        if self.errmsg: return ("FAIL", self.errmsg)

        # test SNMP Trap WebUI Configuration
        self._testEnableSNMPTrap()
        if self.errmsg: return
        self._testDisableSNMPTrap()
        if self.errmsg: return
        self._testEditTrapServerIDField()
        if self.errmsg: return

        self.passmsg = "ZD SNMP WebUI works properly"
        return ("PASS", self.passmsg)

    def cleanup(self):
        self._cfgRestoreSNMPSettings()

#
# Config()
#
    def _cfgInitTestParams(self, conf):
        self.conf = dict(ping_timeout_ms = 10000,
                         check_status_timeout = 90,
                         check_wlan_timeout = 45,
                         pause = 2.0,
                         max_len = 32)

        self.conf.update(conf)
        if not self.conf.has_key('snmp_agent_cfg'):
            self.conf['snmp_agent_cfg'] = dict(enabled = True,
                                               contact = "support@ruckuswireless.com",
                                               location = "880 West Maude Avenue Suite 16",
                                               ro_community = "public",
                                               rw_community = "private")

        if not self.conf.has_key('snmp_trap_cfg'):
            self.conf['snmp_trap_cfg'] = dict(enabled = True,
                                               server_ip = "192.168.0.252")

        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
        self.current_snmp_agent_cfg = ""
        self.current_snmp_trap_cfg = ""

    def _cfgSaveSNMPSettings(self):
        # backup SNMP for restore in cleanup
        self.current_snmp_agent_cfg = lib.zd.sys.get_snmp_agent_info(self.zd)
        self.current_snmp_trap_cfg = lib.zd.sys.get_snmp_trap_info(self.zd)

#
# test()
#
    def _testConfiguring(self):
        self._testEnableSNMP()
        if self.errmsg: return
        self._testDisableSNMP()
        if self.errmsg: return
        self._testEditContactField()
        if self.errmsg: return

    def _testEnableSNMPAgent(self):
        snmp_test_cfg = self.conf['snmp_agent_cfg'].copy()
        snmp_test_cfg['enabled'] = True
        lib.zd.sys.set_snmp_agent_info(self.zd, snmp_test_cfg)
        snmp_info = lib.zd.sys.get_snmp_agent_info(self.zd)
        if not snmp_info['enabled']:
            self.errmsg = "Can't enable SNMP"

    def _testDisableSNMPAgent(self):
        snmp_test_cfg = self.conf['snmp_agent_cfg'].copy()
        snmp_test_cfg['enabled'] = False
        lib.zd.sys.set_snmp_agent_info(self.zd, snmp_test_cfg)
        snmp_info = lib.zd.sys.get_snmp_agent_info(self.zd)
        if snmp_info['enabled']:
            self.errmsg = "Can't disable SNMP"

    def _testEditSNMPAgentField(self, field_name):
        snmp_test_cfg = self.conf['snmp_agent_cfg'].copy()
        snmp_test_cfg[field_name] = utils.make_random_string(self.conf['max_len'] - 1)
        logging.info("Test edit %s field with valid value: %s" % (field_name, snmp_test_cfg[field_name]))
        lib.zd.sys.set_snmp_agent_info(self.zd, snmp_test_cfg)
        snmp_info = lib.zd.sys.get_snmp_agent_info(self.zd)
        if snmp_info[field_name] != snmp_test_cfg[field_name]:
            self.errmsg = "Fail to edit %s field" % field_name
            return

        snmp_test_cfg = self.conf['snmp_agent_cfg'].copy()
        if field_name == 'contact' or field_name == 'location':
            snmp_test_cfg[field_name] = utils.make_random_string(64)
        else:
            snmp_test_cfg[field_name] = utils.make_random_string(self.conf['max_len'])
        logging.info("Test edit %s field with maximum value: %s" % (field_name, snmp_test_cfg[field_name]))
        lib.zd.sys.set_snmp_agent_info(self.zd, snmp_test_cfg)
        snmp_info = lib.zd.sys.get_snmp_agent_info(self.zd)
        if snmp_info[field_name] != snmp_test_cfg[field_name]:
            self.errmsg = "Fail to edit %s field with maximum length support" % field_name
            return

        snmp_test_cfg = self.conf['snmp_agent_cfg'].copy()
        if field_name == 'contact' or field_name == 'location':
            snmp_test_cfg[field_name] = utils.make_random_string(74)
        else:
            snmp_test_cfg[field_name] = utils.make_random_string(self.conf['max_len'] + 10)
        logging.info("Test edit %s field with exceed maximum value: %s" % (field_name, snmp_test_cfg[field_name]))
        lib.zd.sys.set_snmp_agent_info(self.zd, snmp_test_cfg)
        snmp_info = lib.zd.sys.get_snmp_agent_info(self.zd)
        if snmp_info[field_name] == snmp_test_cfg[field_name]:
            self.errmsg = "Zone Director allows configure with exceed maximum value support"
            return


    def _testEnableSNMPTrap(self):
        snmp_test_cfg = self.conf['snmp_trap_cfg'].copy()
        snmp_test_cfg['enabled'] = True
        lib.zd.sys.set_snmp_trap_info(self.zd, snmp_test_cfg)
        snmp_info = lib.zd.sys.get_snmp_trap_info(self.zd)
        if not snmp_info['enabled']:
            self.errmsg = "Can't enable SNMP trap"

    def _testDisableSNMPTrap(self):
        snmp_test_cfg = self.conf['snmp_trap_cfg'].copy()
        snmp_test_cfg['enabled'] = False
        lib.zd.sys.set_snmp_trap_info(self.zd, snmp_test_cfg)
        snmp_info = lib.zd.sys.get_snmp_trap_info(self.zd)
        if snmp_info['enabled']:
            self.errmsg = "Can't disable SNMP trap"

    def _testEditTrapServerIDField(self):
        snmp_test_cfg = self.conf['snmp_trap_cfg'].copy()
        logging.info("Test edit trap server ID with valid field: %s" % snmp_test_cfg['server_ip'])
        lib.zd.sys.set_snmp_trap_info(self.zd, snmp_test_cfg)
        snmp_info = lib.zd.sys.get_snmp_trap_info(self.zd)
        if snmp_test_cfg['server_ip'] != snmp_info['server_ip']:
            self.errmsg = "Can't edit SNMP Server ID Field"

        snmp_test_cfg = self.conf['snmp_trap_cfg'].copy()
        snmp_test_cfg['server_ip'] = utils.make_random_string(self.conf['max_len'])
        logging.info("Test edit trap server ID with invalid field: %s" % snmp_test_cfg['server_ip'])

        lib.zd.sys.set_snmp_trap_info(self.zd, snmp_test_cfg)
        snmp_info = lib.zd.sys.get_snmp_trap_info(self.zd)
        if self.conf['snmp_trap_cfg']['server_ip'] != snmp_info['server_ip']:
            self.errmsg = "Zone Director allow invalid IP Address format in SNMP Server ID Field"

#
# cleanup()
#
    def _cfgRestoreSNMPSettings(self):
        if self.current_snmp_agent_cfg:
            lib.zd.sys.set_snmp_agent_info(self.zd, self.current_snmp_agent_cfg)
        if self.current_snmp_trap_cfg:
            lib.zd.sys.set_snmp_trap_info(self.zd, self.current_snmp_trap_cfg)
