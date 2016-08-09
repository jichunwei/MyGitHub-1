# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: RSM_CLI class verifies the get/set commands at CLI
    Author: Tam Nguyen
    Prerequisite (Assumptions about the state of the testbed/DeviceUnderTest):
    1. Build under test is loaded on the AP

    Required components: RuckusAP
    Test parameters: {'active_ap': 'ip address of active ap'}

    Result type: PASS/FAIL/N/A

    Results: PASS: if all the above criteria are satisfied.
             FAIL: If one of the above criteria is not satisfied.
             N/A: If the test procedure need to run on specific customer ID

    Messages: If FAIL the test script returns a message related to the criterion that is not satisfied.

    Test procedure:
    1. Config:
        - Look for the active AP in the testbed.
    2. Test:
        - Go through each set command in each group and configure AP based on that command
        - Go through each get command that corresponding with set command and verify that we can get/set any commands
        on the AP correctly
    3. Cleanup:
        - Reset factory the AP to clean the all configuration

NOTE:
    . from 9.0 set/get bonjour commands of System group is not available so
    ignore verifying it
"""

import time
import logging
import tempfile
from pprint import pformat

from RuckusAutoTest.models import Test
import libIPTV_TestConfig as tconfig
from RuckusAutoTest.common.Ratutils import *
from RuckusAutoTest.common.utils import kbps_to_mbps

class RSM_CLI(Test):
    required_components = ['RuckusAP']

    def config(self, conf):
        self.ap_ip_addr = self.testbed.getAPIpAddrBySymName(conf['active_ap'])
        logging.info("Find the active AP object")
        self.active_ap = tconfig.getTestbedActiveAP(self.testbed, conf['active_ap'],
                                                    self.testbed.components['AP'], "", "")

        if conf.has_key('aclgroup'):
            self.aclgroup = conf['aclgroup']
        else: self.aclgroup = False

        if conf.has_key('systemgroup'):
            self.systemgroup = conf['systemgroup']
        else: self.systemgroup = False

        if conf.has_key('qosgroup'):
            self.qosgroup = conf['qosgroup']
        else: self.qosgroup = False

        if conf.has_key('vlangroup'):
            self.vlangroup = conf['vlangroup']
            self.active_port = self._getActiveIntfEthAP()
        else: self.vlangroup = False

        if conf.has_key('shaper'):
            self.shaper = conf['shaper']
        else: self.shaper = False

        if conf.has_key('radiogroup'):
            self.radiogroup = conf['radiogroup']
            self.is5GHz = conf['is5GHz']
        else: self.radiogroup = False

        # Info file
        file_info = r'RuckusAutoTest/common/RSM_InfoFile.inf'
        self.info = load_config_file(file_info)
        self.wlan_if = self.info['wlan_if']
        self.version = self.active_ap.get_version()

    def test(self):
        if self.qosgroup:
            logging.info("Get/get commands in qosgroup")
            return self._qosgroup()

        if self.radiogroup:
            logging.info("Get/set commands in radiogroup")
            return self._radiogroup()

        if self.systemgroup:
            logging.info("Get/set commands in systemgroup")
            return self._systemgroup()

        if self.vlangroup:
            logging.info("Get/set commands in vlangroup")
            return self._vlangroup()

        if self.aclgroup:
            logging.info("Get/set commands in ACL group")
            return self._aclgroup()

        if self.shaper:
            logging.info("Get/set commands in Shaper group")
            return self._shaper()

    def cleanup(self):
        logging.info("Reset factory AP to clear all configuration")
        self.active_ap.set_factory()
        time.sleep(3)

    def _shaper(self):
        error_msg = ''
        logging.info(
            'Set shaper (uplink, downlink): (%s, %s) to AP' %
            (self.info['shaper_uplink'], self.info['shaper_downlink'])
        )
        res = self.active_ap.set_shaper(self.wlan_if, self.info['shaper_downlink'],
                                       self.info['shaper_uplink'])
        ok = False
        if res:
            shaper_info = self.active_ap.get_shaper(
                self.active_ap.get_ssid(self.wlan_if)
            )
            logging.info('Get shaper_info from AP: %s' % pformat(shaper_info))
            if 'disable' in shaper_info:
                error_msg = "** Can not enable shaper. "
            else:
                if kbps_to_mbps(shaper_info['down'], False) != \
                    kbps_to_mbps(self.info['shaper_downlink'], False):
                    error_msg += "** Shaper: Downlink preset incorrect. "
                else: ok = True
                if kbps_to_mbps(shaper_info['up'], False) != \
                    kbps_to_mbps(self.info['shaper_uplink'], False):
                    error_msg += "** Shaper: Uplink preset incorrect. "
                else: ok = True
        else:
            error_msg += "** Shaper is not configurable. "
        if ok: logging.info("[Shaper]: Configure shaper for %s successfully" % self.wlan_if)

        if error_msg: return ["FAIL", error_msg]
        return ["PASS", ""]

    def _aclgroup(self):
        error_msg = ''
        if self.info['aclgroup_action'] == 'allow': txt = 'white-list'
        else: txt = "black-list"
        acl_entry = [self.info['aclgroup_entry_1'],
                     self.info['aclgroup_entry_2']
        ]
        acl_action = self.info['aclgroup_action']

        logging.info("[ACL Group]: Create a %s ACL on %s" % (txt, self.wlan_if))
        self.active_ap.set_acl(self.wlan_if, acl_action, acl_entry)

        # Get ACL
        acl_info = self.active_ap.get_acl(self.wlan_if)

        ok = True
        for acl in acl_info['acl_entry']:
            if not acl in acl_entry:
                ok = False
                break
        if not ok:
            error_msg += "** ACL entry: incorrect"
        if acl_info['action'] != self.info['aclgroup_action']:
            error_msg += "** ACL policy: incorrect. "

        if error_msg: return ["FAIL", error_msg]
        return ["PASS", ""]

    def _vlangroup(self):
        error_msg = ''

        # Create a new vlan
        vlan_cfg = dict(vlan_id=self.info['vlangroup_vlan_id'],
                        vlan_name=self.info['vlangroup_vlan_name'],
                        eth_tagged_port=self.active_port,
                        native_wlan=self.info['vlangroup_wlan_native']
        )
        logging.info("[Vlan Group]: Create a VLAN with following information: %s" %
                     self._getVlanDebugMsg(vlan_cfg, False))
        self.active_ap.create_vlan(vlan_cfg)
        time.sleep(2)

        vlan_info = self.active_ap.get_vlan_info()
        found = False
        for vlan in  vlan_info:
            if vlan['vlan_id'] == self.info['vlangroup_vlan_id']:
                for key in vlan.keys():
                    if vlan_cfg[key] != vlan[key]:
                        error_msg += "** Create New VLAN: %s incorrect. " % key
                found = True
                break
        if not found:
            error_msg += "** Can not create a new VLAN. "
        else: logging.info("[Vlan Group]: Create a new VLAN succesfully")

        # Verify cloning vlan function
        logging.info("[Vlan Group]: Clone a VLAN")
        self.active_ap.clone_vlan(self.info['vlangroup_vlan_clone_id'], self.info['vlangroup_vlan_id'])
        vlan_info = self.active_ap.get_vlan_info()
        old_vlan = {}
        cloned_vlan = {}
        for vlan in vlan_info:
            if vlan['vlan_id'] == self.info['vlangroup_vlan_clone_id']:
                cloned_vlan = vlan.copy()
            if vlan['vlan_id'] == self.info['vlangroup_vlan_id']:
                old_vlan = vlan.copy()
        if not cloned_vlan:
            error_msg += "** Can not clone VLAN %s to VLAN %s. " % (self.info['vlangroup_vlan_id'],
                                                                    self.info['vlangroup_vlan_clone_id'])
        else:
            num_of_ports = ""
            num_of_wlans = ""
            clone_eth_ok = True
            clone_wlan_ok = True
            if old_vlan.has_key('eth_native_port'):
                if cloned_vlan.has_key('eth_native_port') or not cloned_vlan.has_key('eth_tagged_port'):
                    clone_eth_ok = False
                else:
                    if old_vlan.has_key('eth_tagged_port'):
                        num_of_ports = old_vlan['eth_native_port'] + " " + old_vlan['eth_tagged_port']
                    else:
                        num_of_ports = old_vlan['eth_native_port']
            else:
                if old_vlan.has_key('eth_tagged_port'):
                    num_of_ports = old_vlan['eth_tagged_port']
                else:
                    if cloned_vlan.has_key('eth_tagged_port') or cloned_vlan.has_key('eth_native_port'):
                        clone_eth_ok = False

            if old_vlan.has_key('native_wlan'):
                if cloned_vlan.has_key('native_wlan') or not cloned_vlan.has_key('tagged_wlan'):
                    clone_wlan_ok = False
                else: num_of_wlans = old_vlan['native_wlan']

            if clone_wlan_ok and clone_eth_ok:
                finish_clone = True
                for port in num_of_ports.split():
                    if not port in cloned_vlan['eth_tagged_port'].split():
                        error_msg += '** Cloned VLAN: number of cloned eth ports are incorrect. '
                        finish_clone = False

                for wlan in num_of_wlans.split():
                    if not wlan in cloned_vlan['tagged_wlan']:
                        error_msg += '** Cloned VLAN: number of cloned wlans are incorrect. '
                        finish_clone = False
                if finish_clone:
                    logging.info("[Vlan Group]: Clone VLAN successfully")
            else: error_msg += '** Clone VLAN is ok but information of Ethernet ports/WLANs is not correct. '

        # Verify changing vlan id
        logging.info("[Vlan Group]: Change VLAN ID")
        self.active_ap.change_vlan(self.info['vlangroup_vlan_id'], self.info['vlangroup_new_vlan_id'])
        vlan_info = self.active_ap.get_vlan_info()
        changed_vlan = {}
        for vlan in vlan_info:
            if vlan['vlan_id'] == self.info['vlangroup_new_vlan_id']:
                changed_vlan = vlan.copy()
                break
        if not changed_vlan:
            error_msg += "** Can not change VLAN ID. "
        else:
            finish_change = True
            for key in old_vlan.keys():
                if key != 'vlan_id':
                    if old_vlan[key] != changed_vlan[key]:
                        error_msg += "** Although VLAN ID is changed correctly, but new vlan info is incorrect. "
                        finish_change = False
            if finish_change:
                logging.info("[Vlan Group]: Change VLAN ID successfully")

        # Verify swapping vlan
        logging.info("[Vlan Group]: Swap VLAN")
        old_vlan_info = self.active_ap.get_vlan_info()
        for old_vlan in old_vlan_info:
            if old_vlan['vlan_id'] == self.info['vlangroup_vlan_clone_id']:
                old_vlan_1 = old_vlan.copy()
            elif old_vlan['vlan_id'] == self.info['vlangroup_new_vlan_id']:
                old_vlan_2 = old_vlan.copy()

        self.active_ap.swap_vlan(self.info['vlangroup_new_vlan_id'], self.info['vlangroup_vlan_clone_id'])
        new_vlan_info = self.active_ap.get_vlan_info()
        swap_ok = True

        for new_vlan in new_vlan_info:
            if new_vlan['vlan_id'] == self.info['vlangroup_vlan_clone_id']:
                new_vlan_1 = new_vlan.copy()
            if new_vlan['vlan_id'] == self.info['vlangroup_new_vlan_id']:
                new_vlan_2 = new_vlan.copy()

        for key in new_vlan_1.keys():
            if key != 'vlan_id':
                if new_vlan_1[key] != old_vlan_2[key]:
                    swap_ok = False
                    break
        for key in new_vlan_2.keys():
            if key != 'vlan_id':
                if new_vlan_2[key] != old_vlan_1[key]:
                    swap_ok = False
                    break
        if not swap_ok: error_msg += '** Can not swap VLAN. '
        else: logging.info("[Vlan Group]: Swap VLAN successfully")

        logging.info("[Vlan Group]: Change Management VLAN ID")
        cur_ap_basemac = self.active_ap.get_base_mac()
        old_vlan_info = self.active_ap.get_vlan_info()
        old_mgmt_vlan = {}
        for vlan in old_vlan_info:
            if vlan['vlan_id'] == '1':
                old_mgmt_vlan = vlan.copy()
                break
        self.active_ap.change_vlan('1', self.info['vlangroup_mgmt_vlan'])
        time.sleep(2)
        new_vlan_info = self.active_ap.get_vlan_info()
        new_mgmt_vlan = {}
        found = False
        for vlan in new_vlan_info:
            if vlan['vlan_id'] == self.info['vlangroup_mgmt_vlan']:
                new_mgmt_vlan = vlan.copy()
                found = True
                break
        if not found:
            error_msg += '** Can not change mgmt VLAN. '
        else:
            passed = True
            for key in new_mgmt_vlan.keys():
                if key != 'vlan_id':
                    if old_mgmt_vlan[key] != new_mgmt_vlan[key]:
                        error_msg += '** Although MGMT VLAN ID is changed correctly but %s is not correct. ' % key.upper()
                        passed = False
            if passed:
                logging.info("[Vlan Group]: Change ID of Management VLAN successfully")

            logging.info("[Vlan Group]: Verify Base Mac of AP after changing MGMT VLAN")
            ap_basemac = self.active_ap.get_base_mac()
            if cur_ap_basemac.lower() != ap_basemac.lower():
                error_msg += "** After changing MGMT VLAN, AP base MAC is changed, too. "
            else: logging.info("BaseMac does not change after changing MGMT VLAN")

        if error_msg: return ["FAIL", error_msg]
        return ["PASS", ""]

    def _getVlanDebugMsg(self, vlan_cfg, txt=True):
        if txt:
            msg = "VLAN %s Information:" % vlan_cfg['vlan_id']
        else: msg = "VLAN ID: %s " % vlan_cfg['vlan_id']
        if vlan_cfg.has_key('vlan_name'):
            msg += "--- Name: %s" % vlan_cfg['vlan_name']
        if vlan_cfg.has_key('native_wlan'):
            msg += " --- Native wlan: %s" % vlan_cfg['native_wlan']
        if vlan_cfg.has_key('eth_native_port'):
            msg += " --- Untagged port: %s" % vlan_cfg['eth_native_port']
        if vlan_cfg.has_key('eth_tagged_port'):
            msg += " --- Tagged port: %s" % vlan_cfg['eth_tagged_port']
        return msg

    def _systemgroup(self):
        error_msg = ''
        # not support bonjour command from 9.0
        if self.version < '9.0':
            logging.info("[System Group]: %s Bonjour service" % self.info['systemgroup_bonjour'])
            bj = self.active_ap.set_bonjour(self.info['systemgroup_bonjour'])

        logging.info("[System Group]: Set Device Location")
        dl = self.active_ap.set_dev_location(self.info['systemgroup_device_location'])

        logging.info("[System Group]: Set Device Name")
        dn = self.active_ap.set_device_name(self.info['systemgroup_device_name'])

        logging.info("[System Group]: Set DHCPC Option 60")
        dhcpc = self.active_ap.set_dhcpc(self.info['systemgroup_dhcpc_opt60'])

        # sometimes cannot set dns right after set dhcpc, have to sleep a moment
        time.sleep(3)
        logging.info("[System Group]: Set Primary DNS")
        self.active_ap.set_dns(self.info['systemgroup_dns_ip_addr1'])

        logging.info("[System Group]: Configure Ethernet Monitor Period")
        ethmon = self.active_ap.set_eth_mon(self.info['systemgroup_eth_mon'])

        # Set fw settings
        fw_cfg = dict(control=self.info['systemgroup_fw_control'],
                      host=self.info['systemgroup_fw_host'],
                      proto=self.info['systemgroup_fw_proto'],
                      user=self.info['systemgroup_fw_user'],
                      password=self.info['systemgroup_fw_pass'],
        )
        logging.info("[System Group]: Configure FW settings")
        self.active_ap.change_fw_setting(fw_cfg)

        logging.info("[System Group]: %s HTTP" % self.info['systemgroup_http'])
        http = self.active_ap.set_http(self.info['systemgroup_http'])

        logging.info("[System Group]: %s HTTPS" % self.info['systemgroup_https'])
        https = self.active_ap.set_http(self.info['systemgroup_https'])

        logging.info("[System Group]: %s Internal Heater" % self.info['systemgroup_internal_heater'])
        ih = self.active_ap.set_internal_heater(self.info['systemgroup_internal_heater'])

        snmp_cfg = dict(manager=self.info['systemgroup_snmp_ip'],
                        ro_community=self.info['systemgroup_snmp_rw_community'],
                        rw_community=self.info['systemgroup_snmp_ro_community']
        )
        logging.info("[System Group]: Configure SNMP Settings")
        self.active_ap.set_snmp(snmp_cfg)

        snmp_acl_cfg = dict(status=self.info['systemgroup_snmp_acl_status'],
                            add_entry=True,
                            acl_entry=[self.info['systemgroup_snmp_acl_entry_1'],
                                       self.info['systemgroup_snmp_acl_entry_2']]
        )
        logging.info("[System Group]: Configure SNMP-ACL Settings")
        self.active_ap.set_snmp_acl(snmp_acl_cfg)
        time.sleep(3)

        logging.info("[System Group]: Configure Syslog Settings")
        syslog_cfg = dict(status=self.info['systemgroup_syslog_status'],
                          server_ip=self.info['systemgroup_syslog_ipv4'],
                          server_port=self.info['systemgroup_syslog_port'],
                          level_network=self.info['systemgroup_syslog_network'],
                          level_local=self.info['systemgroup_syslog_local']
        )
        self.active_ap.set_syslog_info(syslog_cfg)

        logging.info("[System Group]: Set timeout")
        self.active_ap.set_timeout(int(self.info['systemgroup_timeout']))

        tr069_cfg = [dict(url=self.info['systemgroup_tr069_url']),
                     dict(interval=self.info['systemgroup_tr069_intval']),
                     dict(acs_user=self.info['systemgroup_tr069_user']),
                     dict(acs_pass=self.info['systemgroup_tr069_pass']),
                     dict(cpe_user=self.info['systemgroup_tr069_digest_user']),
                     dict(cpe_pass=self.info['systemgroup_tr069_digest_pass'])
        ]
        tr069_desc = ["URL",
                      "Periodic inform Interval",
                      "CPE-calls-ACS Username",
                      "CPE-calls_ACS Password",
                      "ACS-calls-CPE Username",
                      "ACS-calls-CPE Password"
        ]
        tr069_res = []
        for cfg in tr069_cfg:
            logging.info("[System Group]: Configure TR069 %s" % tr069_desc[tr069_cfg.index(cfg)])
            tr069_res.append(self.active_ap.set_tr069(cfg))
            time.sleep(1)

        logging.info("[System Group]: Configure Model Display")
        md = self.active_ap.set_model_display(self.info['systemgroup_model_display'])

        logging.info("[System Group]: Configure NTP server")
        self.active_ap.set_ntp('server', self.info['systemgroup_ntp_server_ip_addr'])

        logging.info("[System Group]: %s SSH" % self.info['systemgroup_ssh_status'])
        self.active_ap.set_ssh(self.info['systemgroup_ssh_status'])

        logging.info("[System Group]: %s PoE Out status" % self.info['systemgroup_poeout'])
        poe = self.active_ap.set_poe_out(self.info['systemgroup_poeout'])

        logging.info("[System Group]: Configure remote management method")
        self.active_ap.set_remote_mgmt(self.info['systemgroup_remote_mgmt_option'])

        logging.info("[System Group]: %s Aerosct support settings" % self.info['systemgroup_aerosct_status'])
        aerosct = self.active_ap.set_aerosct(self.info['systemgroup_aerosct_status'])

        logging.info("Verify Get commands in System Group after setting")
                # not support bonjour command from 9.0
        if self.version < '9.0':
            if bj:
                if self.info['systemgroup_bonjour'] in self.active_ap.get_bonjour():
                    logging.info("[System Group]: %s Bonjour service successfully" % self.info['systemgroup_bonjour'])
                else: error_msg += "** Bonjour status: incorrect. "
            else: error_msg += "** Bonjour service is not configurable. "

        if dl:
            if self.info['systemgroup_device_location'] != self.active_ap.get_dev_location():
                error_msg += "** Device Location: incorrect. "
            else: logging.info("[System Group]: Device Location is set correctly")
        else: error_msg += "** Device Location is not configurable. "

        if dn:
            if self.info['systemgroup_device_name'] != self.active_ap.get_device_name():
                error_msg += "** Device Name: incorrect. "
            else: logging.info("[System Group]: Device Name is set correctly")
        else: error_msg += "** Device Name is not configurable. "

        if dhcpc:
            if self.info['systemgroup_dhcpc_opt60'] != self.active_ap.get_dhcpc():
                error_msg += "** DHCPC Option 60: incorrect. "
            else: logging.info("[System Group]: Set DHCPC Option 60 correctly")
        else: error_msg += "** DHCPC Option 60 is not configurable. "

        dns = self.active_ap.get_dns()['ip_addr1']
        time.sleep(1)
        if self.info['systemgroup_dns_ip_addr1'] != dns:
            error_msg += "** Primary DNS Ip Address: incorrect; Expect: %s. "\
                         "Actual: %s. " % \
                         (self.info['systemgroup_dns_ip_addr1'], dns)
        else: logging.info("[System Group]: Configure Primary DNS successfully")

        if ethmon:
            if self.active_ap.get_eth_mon() != self.info['systemgroup_eth_mon']:
                error_msg += "** Ethernet Monitor Period: incorrect. "
            else: logging.info("[System Group]: Configure Ethernet Monitor Period successfully")
        else: error_msg += "** Ethernet Monitor Period is not configurable. "

        logging.info("[System Group]: Verify FW Settings")
        fw_info = self.active_ap.get_fw_upgrade_setting()
        for key in fw_cfg.keys():
            if key == 'proto':
                fw_info[key] = fw_info[key].lower()
                fw_cfg[key] = fw_cfg[key].lower()
            if fw_info[key] != fw_cfg[key]:
                error_msg += "** FW Setting: %s incorrect. " % key.upper()
            else: logging.info("[System Group]: FW Settings: configure %s correctly" % key.upper())

        if http:
            if self.info['systemgroup_http'] in self.active_ap.get_http():
                logging.info("[System Group]: %s HTTP successfully" % self.info['systemgroup_http'])
            else: error_msg += "** HTTP status: incorrect. "
        else: error_msg += "** HTTP is not configurable. "

        if https:
            if self.info['systemgroup_https'] in self.active_ap.get_http():
                logging.info("[System Group]: %s HTTPS successfully" % self.info['systemgroup_https'])
            else: error_msg += "** HTTPS status: incorrect. "
        else: error_msg += "** HTTPS is not configurable. "

        if ih:
            if self.info['systemgroup_internal_heater'] in self.active_ap.get_internal_heater():
                logging.info("[System Group]: %s Internal heater successfully" %
                             self.info['systemgroup_internal_heater'])
            else: error_msg += "** Internal Heater: incorrect. "
        else: error_msg += "** Internal Heater is not configurable. "

        logging.info("[System Group]: Verify SNMP Settings")
        snmp_info = self.active_ap.get_snmp()
        for key in snmp_info.keys():
            if not snmp_cfg.has_key(key):
                error_msg += "** SNMP does not have %s option" % key.upper()
            else:
                if snmp_info[key] != snmp_cfg[key]:
                    error_msg += "** SNMP: %s option incorrect. " % key.upper()
                else: logging.info("[System Group]: Configure SNMP %s correctly" % key.upper())

        snmp_acl_info = self.active_ap.get_snmp_acl()
        if snmp_acl_info['status'] == 'disable':
            error_msg += '** Can not enable SNMP-ACL status. '
        else:
            for entry in snmp_acl_info['acl_entry']:
                if not entry in snmp_acl_cfg['acl_entry']:
                    error_msg += 'SNMP-ACL: can not add entry %s. ' % entry
                else: logging.info("[System Group]: Add entry %s for SNMP-ACL succesfully" % entry)

        logging.info("[System Group]: Verify Syslog Settings")
        syslog_info = self.active_ap.get_syslog_info()
        for key in syslog_info.keys():
            if syslog_info[key] != syslog_cfg[key]:
                error_msg += "** Syslog: %s incorrect. " % key.upper()
            else: logging.info("[System Group]: Set Syslog %s option correctly" % key.upper())

        if self.info['systemgroup_timeout'] != self.active_ap.get_timeout():
            error_msg += "** Timeout: incorrect. "
        else: logging.info("[System Group]: Set timeout successfully")

        logging.info("[System Group]: Verify TR069 settings")
        tr069_info = self.active_ap.get_tr069()

        for i in range(len(tr069_res)):
            if tr069_res[i]:
                for key in tr069_cfg[i].keys():
                    if tr069_info[key] != tr069_cfg[i][key]:
                        error_msg += "** TR069 %s option: incorrect. " % tr069_desc[i]
                    else: logging.info("[System Group]: Configure TR069 %s successfully" % tr069_desc[i])
            else: error_msg += "** TR069 %s option is not configurable. " % tr069_desc[i]

        if md:
            if self.active_ap.get_model_display() != self.info['systemgroup_model_display']:
                error_msg += "** Model Display: incorrect. "
            else: logging.info("[System Group]: Set Model-Display successfully")
        else: error_msg += "** Model Display is not configurable . "

        if self.active_ap.get_ntp()['active_server'] != self.info['systemgroup_ntp_server_ip_addr']:
            error_msg += "** NTP Server: incorrect. "
        else: logging.info("[System Group]: Configure NTP server successfully")

        if not self.info['systemgroup_ssh_status'] in self.active_ap.get_ssh():
            error_msg += "** SSH status: incorrect. "
        else: logging.info("[System Group]: %s SSH successfully" % self.info['systemgroup_ssh_status'])

        if poe:
            if self.info['systemgroup_poeout'] in self.active_ap.get_poe_out():
                logging.info("[System Group]: %s PoE Out successfully" % self.info['systemgroup_poeout'])
            else: error_msg += "** PoE Out status: incorrect. "
        else: error_msg += "** PoE Out is not configurable. "

        remote_mgmt_info = self.active_ap.get_remote_mgmt()
        for key, value in remote_mgmt_info.iteritems():
            if remote_mgmt_info['remote_mgmt'] != self.info['systemgroup_remote_mgmt_option']:
                error_msg += "** Type of Remote MGMT: incorrect. "
                break
        else: logging.info("[System Group]: Select Remote Management method correctly")

        if aerosct:
            if self.info['systemgroup_aerosct_status'] in self.active_ap.get_aerosct():
                logging.info("[System Group]: %s Aerosct support settings succesfully" %
                             self.info['systemgroup_aerosct_status'])
            else: error_msg += "** Aerosct status: incorrect. "
        else: error_msg += "** Aerosct status is not configurable. "

        if error_msg:
            logging.info(error_msg)
            return ["FAIL", error_msg]
        return ["PASS", ""]

    def _qosgroup(self):
        media = self.info['qosgroup_media_type']
        error_msg = ''

        # Setting
        logging.info("[QoS Group]: Set heuristics configuration")
        classify_octet_count = self.info['qosgroup_heuristics_classify_octet']
        noclassify_octet_count = self.info['qosgroup_heuristics_nocalssify_octet']
        ipg_min = self.info['qosgroup_heuristics_ipg_min']
        ipg_max = self.info['qosgroup_heuristics_ipg_max']
        pktlen_min = self.info['qosgroup_heuristics_pktlen_min']
        pktlen_max = self.info['qosgroup_heuristics_pktlen_max']


        hrts_clsf_res = self.active_ap.set_heuristics_cfg(media, cfg_classify = True,
                                                           octet_count = classify_octet_count)
        hrts_noclsf_res = self.active_ap.set_heuristics_cfg(media, cfg_noclassify = True,
                                                             octet_count = noclassify_octet_count)
        hrts_pktgap_res = self.active_ap.set_heuristics_cfg(media, cfg_pktgap = True,
                                                             min_value = ipg_min,
                                                             max_value = ipg_max)
        hrts_pktlen_res = self.active_ap.set_heuristics_cfg(media, cfg_pktlen = True,
                                                             min_value = pktlen_min,
                                                             max_value = pktlen_max)

        logging.info("[QoS Group]: Set ToS classify values")
        try:
            self.active_ap.set_tos_values(media, self.info['qosgroup_tos_classify_value'], True)
            tos_clfy_value = True
        except: tos_clfy_value = False

        logging.info("[QoS Group]: Set ToS marking values")
        try:
            self.active_ap.set_tos_values(media, self.info['qosgroup_tos_marking_value'], False)
            tos_mark_value = True
        except: tos_mark_value = False

        logging.info("[QoS Group]: Set Directed Threshold")
        directed_thres = self.active_ap.set_directed_threshold(self.wlan_if, self.info['qosgroup_directed_threshold'])

        logging.info("[QoS Group]: Set consecutive TX failures")
        txfail_thres = self.active_ap.set_qos_threshold('txFailThreshold', self.info['qosgroup_txfailthreshold'])

        logging.info("[QoS Group]: Set Query Interval")
        query_res = self.active_ap.set_query_interval(self.info['qosgroup_query_interval'])

        logging.info("[QoS Group]: %s QoS Aging Mechanism" % self.info['qosgroup_aging'])
        aging_res = self.active_ap.set_qos_aging(self.info['qosgroup_aging'])

        # Set qos option in a specific interface
        qos_opts = ['classification',
                    'heuristics udp',
                    'directed multicast',
                    'igmp', 'mld',
                    'tos classify'
        ]
        status = [self.info['qosgroup_classification'],
                  self.info['qosgroup_heuristics_status'],
                  self.info['qosgroup_directed_multicast'],
                  self.info['qosgroup_igmp_snooping'],
                  self.info['qosgroup_mld_snooping'],
                  self.info['qosgroup_tos_classify']
        ]
        boollist = []
        for s in status:
            if 'disable' in s: boollist.append(False)
            else: boollist.append(True)

        qos_opts_res = []
        for opt in qos_opts:
            logging.info("[QoS Group]: %s %s on interface %s" %
                         (status[qos_opts.index(opt)], opt.upper(), self.wlan_if))
            try:
                self.active_ap.set_qos_cfg_option(self.wlan_if, opt, boollist[qos_opts.index(opt)])
                qos_opts_res.append(True)
            except: qos_opts_res.append(False)
            time.sleep(1)

        # Add filter matching rules
        filter_action = self.info['qosgroup_filter_action']
        layer = ['4', '3', '2']
        proto = ['udp', 'ip', 'mac']
        value = [self.info['qosgroup_layer4_port'],
                 self.info['qosgroup_layer3_ip'],
                 self.info['qosgroup_layer2_mac']
        ]
        filt_res = []
        for i in range(len(proto)):
            logging.info("[QoS Group]: Add L%s port matching filter" % layer[i])
            try:
                self.active_ap.add_port_matching_rule(self.wlan_if, proto[i],
                                                   filter_action, value[i],
                                                   True, media, layer[i])
                filt_res.append(True)
            except: filt_res.append(False)
            time.sleep(1)

        query_opts = [True, False]
        igmp_name = ["IGMP", "MLD"]
        query_status = [self.info['qosgroup_igmp_query_sta'],
                  self.info['qosgroup_mld_query_sta']
        ]
        ver = [self.info['qosgroup_igmp_query_ver'],
               self.info['qosgroup_mld_query_ver']
        ]
        query_res = []
        for i in range(len(query_opts)):
            logging.info("[QoS Group]: %s %s Query %s" % (query_status[i], igmp_name[i], ver[i]))
            query_res.append(self.active_ap.set_igmp_query(ver[i], query_status[i], query_opts[i]))

        # Getting
        logging.info("Verify Get commands in QoS Group after setting")

        # Verify heuristics
        hrst_cfg = self.active_ap.get_heuristics_cfg()
        hrts_ok = False
        if hrts_clsf_res:
            if hrst_cfg['classify'][media] != classify_octet_count:
                error_msg += "** Heuristics classify octet count is not correct. "
            else: hrts_ok = True
        else: error_msg += "** Heuristics classify octet count is not configurable. "

        if hrts_noclsf_res:
            if hrst_cfg['noclassify'][media] != noclassify_octet_count:
                error_msg += "** Heuristics noclassify octet count is not correct. "
            else: hrts_ok = True
        else: error_msg += "** Heuristics noclassify octet count is not configurable. "

        if hrts_pktgap_res:
            if hrst_cfg['packet_gap'][media] != [ipg_min, ipg_max]:
                error_msg += "** Heuristics packet gap is not correct. "
            else: hrts_ok = True
        else: error_msg += "** Heuristics packet gap is not configurable. "

        if hrts_pktlen_res:
            if hrst_cfg['packet_len'][media] != [pktlen_min, pktlen_max]:
                error_msg += "** Heuristics packet len is not correct. "
            else: hrts_ok = True
        else: error_msg += "** Heuristics packet length is not configurable"

        if hrts_ok: logging.info("[QoS Group]: Heuristics configuration is set correctly")

        # ToS values
        if tos_clfy_value:
            if self.active_ap.get_tos_values(True)[media] != self.info['qosgroup_tos_classify_value']:
                error_msg += "** ToS Classify value is not correct"
            else: logging.info("[QoS Group]: ToS Classify value is set correctly")
        else: error_msg += "** ToS classify value is not configurable. "

        if tos_mark_value:
            if self.active_ap.get_tos_values(False)[media] != self.info['qosgroup_tos_marking_value']:
                error_msg += "** ToS Marking value is not correct"
            else: logging.info("[QoS Group]: ToS marking value is set correctly")
        else: error_msg += "** ToS Marking value is not configurable. "

        # Threshold
        if directed_thres:
            if self.active_ap.get_directed_threshold(self.wlan_if) != self.info['qosgroup_directed_threshold']:
                error_msg += "** Directed Broadcast Threshold: incorrect. "
            else: logging.info("[QoS Group]: Directed Broadcast Threshold is set correctly")
        else: error_msg += "** Directed Broadcast Threshold is not configurable. "

        if txfail_thres:
            if self.active_ap.get_qos_threshold('txFailThreshold') != self.info['qosgroup_txfailthreshold']:
                error_msg += "** Tx Threshold Failure: incorrect. "
            else: logging.info("[QoS Group]: TxThresholdFailure is set correctly")
        else: error_msg += "** TxThresholdFailure is not configurable. "

        if query_res:
            query_int = self.active_ap.get_query_interval()
            if query_int != self.info['qosgroup_query_interval']:
                error_msg += "** Query Interval: incorrect. "
            else: logging.info("Query Interval is set correctly")
        else: error_msg += "Query Interval is not configurable. "

        if aging_res:
            buf = self.active_ap.get_qos_aging()
            if not self.info['qosgroup_aging'] in buf.lower():
                error_msg += "** QoS Aging is not correct. "
            else: logging.info("[QoS Group]: QoS Aging is set correctly")
        else: error_msg += "QoS Aging is not configurable. "

        # QoS Options
        qos = self.active_ap.get_qos_cfg_option(self.wlan_if)
        qos_after_set = [qos['classification'],
                         qos['udp_heuristic_classification'],
                         qos['directed_multicast'],
                         qos['igmp_snooping_mode'],
                         qos['mld_snooping_mode'],
                         qos['tos_classification']
        ]

        for i in range(len(qos_opts)):
            if qos_opts_res[i]:
                if not status[i] in qos_after_set[i].lower():
                    error_msg += "** Can not %s QoS option '%s'. " % (status[i], qos_opts[i].upper())
                else: logging.info("[QoS Group]: option %s is %sd correctly" % (qos_opts[i].upper(), status[i]))
            else:
                error_msg += "QoS option '%s' is not configurable. " % qos_opts[i]

        # Port matching filter
        fltr_rules_after_set = self.active_ap.get_port_matching_rule(self.wlan_if)
        print fltr_rules_after_set
        for i in range(len(proto)):
            if filt_res[i]:
                for rule in fltr_rules_after_set:
                    if rule['proto'] == proto[i]:
                        if not value[i] in rule['filter_value']:
                            error_msg += "** L%s General Filter: incorrect. " % layer[i]
                        else: logging.info("[QoS Group]: L%s General Filter is set correctly" % layer[i])
                        break
            else:
                error_msg += "** L%s General Filter is not configurable. " % layer[i]

        for i in range(len(igmp_name)):
            if query_res[i]:
                tmp = self.active_ap.get_igmp_query(query_opts[i])
                for key in tmp.keys():
                    if key.lower() == ver[i]:
                        if not query_status[i] in tmp[key].lower():
                            error_msg += "** Can not %s %s Query. " % (query_status[i], igmp_name[i])
                        else: logging.info("[QoS Group]: %s Query is set correctly" % igmp_name[i])
                        break
            else: error_msg += "** %s General Query is not configurable. " % igmp_name[i]

        # Result
        if error_msg: return ["FAIL", error_msg]

        logging.info("Get/Set Commands in QoS Group successfully")
        return ["PASS", ""]

    def _radiogroup(self):
        error_msg = ""
        logging.info("[Radio Group]: Set System Operation Mode")
        system_set_res = self.active_ap.set_system(self.info['radiogrp_system'],
                                                  self.wlan_if)
        if system_set_res:
            system_get_res = self.active_ap.get_system(self.wlan_if)
            if system_get_res.lower() != self.info['radiogrp_system']:
                error_msg += "** System Operation Mode: incorrect. "
            else: logging.info("[Radio Group]: System Operation Mode is set correctly")
        else: error_msg += "** System Operation Mode is not configurable. "

        logging.info("[Radio Group]: %s AP-BRIDGE" % self.info['radiogroup_ap_bridge'])
        apBr_set_res = self.active_ap.set_ap_bridge(self.wlan_if, self.info['radiogroup_ap_bridge'])

        logging.info("[Radio Group]: %s Auto Provisioning" % self.info['radiogroup_autoprov'])
        autoprov = self.active_ap.set_auto_prov(self.info['radiogroup_autoprov'])

        logging.info("[Radio Group]: Set Beacon Interval")
        bc_int = self.active_ap.set_beacon_interval(self.wlan_if, self.info['radiogroup_beacon_intval'])

        logging.info("[Radio Group]: Configure Channel for %s" % self.wlan_if)
        self.active_ap.set_channel(self.wlan_if, self.info['radiogroup_channel'])

        logging.info("[Radio Group]: %s TKIP Counter Measure" % self.info['radiogroup_countermeasure'])
        cter_measure = self.active_ap.set_counter_measure(self.info['radiogroup_countermeasure'], self.wlan_if)

        logging.info("[Radio Group]: Configure Country Code for AP to %s" % self.info['radiogroup_ctrycode'])
        self.active_ap.set_country_code(self.info['radiogroup_ctrycode'])

        logging.info("[Radio Group]: %s Country Information Element" % self.info['radiogroup_countryie'])
        ctryie = self.active_ap.set_country_ie(self.wlan_if, self.info['radiogroup_countryie'])

        logging.info("[Radio Group]: Configure CWMIN-ADAPT status")
        cwmin_adapt = self.active_ap.set_cwmin_adapt(self.info['radiogroup_cwmin_adapt'], self.wlan_if)

        logging.info("[Radio Group]: Configure channel width mode")
        cwmode = self.active_ap.set_cw_mode(self.wlan_if, self.info['radiogroup_cwmode'])

        logging.info("[Radio Group]: Configure DTIM period")
        dtim = self.active_ap.set_dtim_period(self.wlan_if, self.info['radiogroup_dtim_period'])

        logging.info("[Radio Group]: %s invisible capability" % self.info['radiogroup_invisible'])
        inv = self.active_ap.set_invisible(self.wlan_if, self.info['radiogroup_invisible'])

        logging.info("[Radio Group]: Configure Encryption")
        encrpt_cfg = dict(wlan_if=self.wlan_if,
                          key_string=self.info['radiogroup_keystring'],
                          encryption=self.info['radiogroup_encryption'],
                          auth=self.info['radiogroup_auth'],
                          wpa_ver=self.info['radiogroup_wpa_ver']
                          )
        self.active_ap.cfg_wlan(encrpt_cfg)

        logging.info("[Radio Group]: Configure RxChainMask")
        rx_mask = self.active_ap.set_rx_chain_mask(self.wlan_if, self.info['radiogroup_rxchainmask'])

        logging.info("[Radio Group]: Configure TxChainMask")
        tx_mask = self.active_ap.set_tx_chain_mask(self.wlan_if, self.info['radiogroup_txchainmask'])

        logging.info("[Radio Group]: Configure LegacyTxChainMask")
        legacy_mask = self.active_ap.set_legacy_tx_chain_mask(self.wlan_if, self.info['radiogroup_legacytxchainmask'])

        logging.info("[Radio Group]: Configure SSID")
        self.active_ap.set_ssid(self.wlan_if, self.info['radiogroup_ssid'])

        logging.info("[Radio Group]: %s SSID Supression" % self.info['radiogroup_ssid_suppress'])
        ssid_suppres = self.active_ap.set_ssid_supress(self.wlan_if, self.info['radiogroup_ssid_suppress'])

        logging.info("[Radio Group]: %s %s" % (self.info['radiogroup_state'], self.wlan_if.upper()))
        self.active_ap.set_state(self.wlan_if, self.info['radiogroup_state'])

        logging.info("[Radio Group]: Set RTS-THR")
        rts_thr = self.active_ap.set_rts_thr(self.wlan_if, self.info['radiogroup_rts_thr'])

        logging.info("[Radio Group]: Set rescan settings")
        rescan_cfg = {'min': self.info['radiogroup_rescan_min'],
                      'exp': self.info['radiogroup_rescan_exp'],
                      'max':self.info['radiogroup_rescan_max']}
        self.active_ap.set_rescan_ap(self.wlan_if, rescan_cfg)

        logging.info("[Radio Group]: %s Voice Call Detection" % self.info['radiogroup_vodetect'])
        vodetect = self.active_ap.set_vo_detect(self.wlan_if, self.info['radiogroup_vodetect'])

        logging.info("[Radio Group]: Set Transmit Power")
        self.active_ap.set_tx_power(self.wlan_if, self.info['radiogroup_txpower'])

        logging.info("[Radio Group]: Set WDS mode")
        wds = self.active_ap.set_wds_mode(self.wlan_if, self.info['radiogroup_wds_mode'])

        logging.info("[Radio Group]: Set the %s description" % self.wlan_if)
        wlan_txt = self.active_ap.set_wlan_text(self.wlan_if, self.info['radiogroup_wlantext'])

        logging.info("[Radio Group]: %s WMM" % self.info['radiogroup_wmm'])
        self.active_ap.set_wmm(self.wlan_if, self.info['radiogroup_wmm'])

        logging.info("[Radio Group]: Configure MQ Class to Priority Mapping")
        self.active_ap.set_class2_mq_prio(self.wlan_if,
                                       self.info['radiogroup_mqclass2pri_voice'],
                                       self.info['radiogroup_mqclass2pri_video'],
                                       self.info['radiogroup_mqclass2pri_be'],
                                       self.info['radiogroup_mqclass2pri_bk'])

        logging.info("[Radio Group]: %s Dynamic VLAN Mode" % self.info['radiogroup_dvlan'])
        dvlan = self.active_ap.set_dvlan(self.wlan_if, self.info['radiogroup_dvlan'])

        if self.version < '9.0':
            logging.info("[Radio Group]: Set Fragmentation Threshold")
            frag_thr = self.active_ap.set_frag_thr(self.wlan_if, self.info['radiogroup_frag_thr'])

        logging.info("[Radio Group]: Set Fixed-rate")
        self.active_ap.set_fixed_rate(self.wlan_if, self.info['radiogroup_fixed_rate'])

        logging.info("[Radio Group]: Set 802.11h status")
        res_80211h = self.active_ap.set_11h_status(self.wlan_if, self.info['radiogroup_11h_status'])

        logging.info("[Radio Group]: Set the allowed maximum assoc ID")
        maxaid = self.active_ap.set_max_aid(self.wlan_if, self.info['radiogroup_max_aid'])

        logging.info("[Radio Group]: Configure min rate")
        minrate = self.active_ap.set_min_rate(self.wlan_if, self.info['radiogroup_minrate'])

        logging.info("[Radio Group]: Configure Distance")
        dis = self.active_ap.set_distance(self.wlan_if, self.info['radiogroup_distance'])

        logging.info("[Radio Group]: Set protection mode for 11b/11g")
        protmode = self.active_ap.set_prot_mode(self.wlan_if, self.info['radiogroup_prot_mode'])

        logging.info("[Radio Group]: Set Band Steering Threshold")
        bs_thr = self.active_ap.set_band_steering_thr(self.wlan_if, self.info['radiogroup_bandsteering'])

        # Set current MQ for wlan
        qtime_info = self.info['radiogroup_mq_qtime'].split()
        credit = self.info['radiogroup_mq_credit'].split()
        maxpkts_info = self.info['radiogroup_mq_maxpkts'].split()
        mq_opts = [dict(pscredit=self.info['radiogroup_mq_pscredit']),
                   dict(qtime=dict(voice=qtime_info[0],
                                   video=qtime_info[1],
                                   data=qtime_info[2],
                                   background=qtime_info[3])),
                   dict(credit=dict(bclient=credit[1],
                                    gclient=credit[0])),
                   dict(maxpkts=dict(voice=maxpkts_info[0],
                                     video=maxpkts_info[1],
                                     data=maxpkts_info[2],
                                     background=maxpkts_info[3]))
        ]
        mq_desc = ["Power-Save Credit", "Pkt Queue Time", "Credit for B/G Client", "Max Pkts"]
        mq_res = []

        for opt in mq_opts:
            logging.info("[Radio Group]: Configure MQ %s option" % mq_desc[mq_opts.index(opt)])
            mq_res.append(self.active_ap.set_mq(self.wlan_if, **opt))

        event_opts = ['assoc', 'auth', 'crc', 'obss', 'rssi', 'vid-drop', 'vo-drop']
        event_desc = ['association', 'authentication',
                      'crc', 'Other BSS', 'RSSI',
                      'Video Drop', 'Voice Drop'
        ]
        event_period = [self.info['radiogroup_event_assoc_period'],
                        self.info['radiogroup_event_auth_period'],
                        self.info['radiogroup_event_crc_period'],
                        self.info['radiogroup_event_obss_period'],
                        self.info['radiogroup_event_rssi_period'],
                        self.info['radiogroup_event_vid_drop_period'],
                        self.info['radiogroup_event_vo_drop_period']
        ]
        event_thr = [self.info['radiogroup_event_assoc_thr'], '',
                     self.info['radiogroup_event_crc_thr'],
                     self.info['radiogroup_event_obss_thr'],
                     self.info['radiogroup_event_rssi_thr'],
                     self.info['radiogroup_event_vid_drop_thr'],
                     self.info['radiogroup_event_vo_drop_thr']
        ]
        event_res = []

        for i in range(len(event_opts)):
            logging.info("[Radio Group]: Set period/threshold for %s event" % event_desc[i].upper())
            event_res.append(self.active_ap.set_event(self.wlan_if, event_opts[i],
                                                     event_period[i], event_thr[i]))

        # Set Autoconfig
        atcf_value = dict(nasid_sel=self.info['radiogroup_atcf_nasidsel'],
                          ssid_sel=self.info['radiogroup_atcf_ssidsel'],
                          ssid_prefix=self.info['radiogroup_atcf_ssidpre'],
                          weplen=self.info['radiogroup_atcf_weplen'],
                          wpalen=self.info['radiogroup_atcf_wpalen']
        )

        logging.info("[Radio Group]: Autoconfig Options")
        self.active_ap.set_auto_cfg(self.wlan_if, **atcf_value)

        # Set DFS
        if self.version < '9.0' and self.is5GHz:
            logging.info("[Radio Group]: %s DFS" % self.info['radiogroup_dfs_status'])
            dfs_sta = self.active_ap.set_dfs(self.wlan_if, self.info['radiogroup_dfs_status'])

            dfs_value = [self.info['radiogroup_dfs_cactime'],
                         self.info['radiogroup_dfs_notime'],
                         self.info['radiogroup_dfs_blkchans']
            ]
            dfs_opts = ['cactime', 'notime', 'blkchans']
            dfs_desc = ["CAC time", "Non-Occupancy time", "Channel Block"]
            dfs_opts_res = []
            for i in range(len(dfs_value)):
                logging.info("[Radio Group]: Configure DFS %s option" % dfs_desc[i])
                dfs_opts_res.append(self.active_ap.set_dfs(self.wlan_if, dfs_opts[i], dfs_value[i]))

        logging.info("Verify get commands in RADIO group after setting")
        if apBr_set_res:
            if not self.info['radiogroup_ap_bridge'] in self.active_ap.get_ap_bridge(self.wlan_if):
                error_msg += "** AP-BRIDGE status: incorrect. "
            else: logging.info("[Radio Group]: %s AP-Bridge successfully" %
                               self.info['radiogroup_ap_bridge'])
        else: error_msg += "** AP-BRIDGE command is not configurable. "

        if autoprov:
            if not self.info['radiogroup_autoprov'] in self.active_ap.get_auto_prov():
                error_msg += "** AutoProvision status: incorrect. "
            else: logging.info("[Radio Group]: %s AutoProvision successfully" %
                               self.info['radiogroup_autoprov'])
        else: error_msg += "** AutoProvision command is not configurable. "

        if bc_int:
            if int(self.info['radiogroup_beacon_intval']) != self.active_ap.get_beacon_interval(self.wlan_if):
                error_msg += "** Beacon Interval: incorrect. "
            else: logging.info("[Radio Group]: Beacon interval is set correctly")
        else: error_msg += "** Beacon Interval is not configurable. "

        if self.active_ap.get_channel(self.wlan_if)[0] != int(self.info['radiogroup_channel']):
            error_msg += "** Channel: incorrect. "
        else: logging.info("[Radio Group]: configure channel for %s successfully" % self.wlan_if)

        if cter_measure:
            if not self.info['radiogroup_countermeasure'] in self.active_ap.get_counter_measure(self.wlan_if):
                error_msg += "** TKIP Counter Measure: incorrect. "
            else: logging.info("[Radio Group]: %s TKIP Counter Measure correctly" %
                               self.info['radiogroup_countermeasure'])
        else: error_msg += "** TKIP Counter Measure is not configurable. "

        # Get countrycode
        if self.active_ap.get_country_code() != self.info['radiogroup_ctrycode']:
            error_msg += "** CountryCode: incorrect. "
        else: logging.info("[Radio Group]: Configure Countrycode for Ap successfully")

        if ctryie:
            if self.active_ap.get_country_ie(self.wlan_if) != self.info['radiogroup_countryie']:
                error_msg += "** CountryIE: Incorrect. "
            else: logging.info('[Radio Group]: %s Country Information Element successfully' %
                               self.info['radiogroup_countryie'])
        else: error_msg += "** CountryIE is not configurable. "

        if cwmin_adapt:
            if not self.info['radiogroup_cwmin_adapt'] in self.active_ap.get_cwmin_adapt(self.wlan_if):
                error_msg += "** CWMIN-ADAPT: incorrect. "
            else: logging.info("[Radio Group]: Configure CWMIN-ADAPT status correctly")
        else: error_msg += "** CWMIN-ADAPT is not configurable. "

        if cwmode:
            if self.info['radiogroup_cwmode'] != self.active_ap.get_cw_mode(self.wlan_if):
                error_msg += "** CWMODE: incorrect. "
            else: logging.info("[Radio Group]: Configure cwmode correctly")
        else: error_msg += "** CWMODE is not configurable. "

        if dtim:
            if self.info['radiogroup_dtim_period'] != self.active_ap.get_dtim_period(self.wlan_if):
                error_msg += "** DTIM Period: incorrect. "
            else: logging.info("[Radio Group]: Configure DTIM Period successfully")
        else: error_msg += "** DTIM Period is not configurable. "

        if inv:
            if not self.info['radiogroup_invisible'] in self.active_ap.get_invisible(self.wlan_if):
                error_msg += "** Invisible Capability status: incorrect. "
            else: logging.info("[Radio Group]: %s invisible capability successfully" %
                               self.info['radiogroup_invisible'])
        else: error_msg += "** Invisible Capability is not configurable. "

        # Verify Encryption
        encrpt_info = self.active_ap.get_encryption(self.wlan_if)
        del encrpt_cfg['wlan_if']
        encrpt_pass = True
        for key in encrpt_cfg.keys():
            if encrpt_cfg[key] != encrpt_info[key]:
                error_msg += "** Encryption: %s incorrect. " % key
                encrpt_pass = False
        if encrpt_pass:
            logging.info("[Radio Group]: Configure Encryption for %s successfully" % self.wlan_if)


        # Verify event setting
        tmp = self.active_ap.get_event(self.wlan_if)
        event_after_set = []
        if tmp.has_key('assoc'): event_after_set.append(tmp['assoc'])
        else: event_after_set.append(list())
        if tmp.has_key('auth'): event_after_set.append(tmp['auth'])
        else: event_after_set.append(list())
        if tmp.has_key('crc'): event_after_set.append(tmp['crc'])
        else: event_after_set.append(list())
        if tmp.has_key('obss'): event_after_set.append(tmp['obss'])
        else: event_after_set.append(list())
        if tmp.has_key('rssi'): event_after_set.append(tmp['rssi'])
        else: event_after_set.append(list())
        if tmp.has_key('video_drop'): event_after_set.append(tmp['video_drop'])
        else: event_after_set.append(list())
        if tmp.has_key('voice_drop'): event_after_set.append(tmp['voice_drop'])
        else: event_after_set.append(list())

        for i in range(len(event_opts)):
            if event_res[i]:
                ok = True
                if type(event_after_set[i]) == str:
                    if event_after_set[i] != event_period[i]: ok = False
                elif event_after_set[i] != [event_thr[i], event_period[i]]:
                    ok = False

                if not ok: error_msg += "** %s Event: incorrect. " % event_desc[i]
                else: logging.info("[Radio Group]: Configure %s Event successfully" % event_desc[i].upper())
            else: error_msg += "** %s Event is not configurable. " % event_desc[i]

        if rx_mask:
            rxchainmask = self.active_ap.get_rx_chain_mask(self.wlan_if)
            if self.info['radiogroup_rxchainmask'] != rxchainmask:
                error_msg += "** RxChainMask: incorrect. "
            logging.info("[Radio Group]: Configure RxChainMask correctly")
        else: error_msg += "** RxChainMask is not configurable. "

        if tx_mask:
            if self.info['radiogroup_txchainmask'] != self.active_ap.get_tx_chain_mask(self.wlan_if):
                error_msg += "** TxChainMask: incorrect. "
            logging.info("[Radio Group]: Configure TxChainMask correctly")
        else: error_msg += "** TxChainMask is not configurable. "

        if legacy_mask:
            if self.info['radiogroup_legacytxchainmask'] != self.active_ap.get_legacy_tx_chain_mask(self.wlan_if):
                error_msg += "** LegacyTxChainMask: incorrect. "
            logging.info("[Radio Group]: Configure LegacyTxChainMask correctly")
        else: error_msg += "** LegacyTxChainMask is not configurable. "

        if self.active_ap.get_ssid(self.wlan_if) != self.info['radiogroup_ssid']:
            error_msg += "** SSID: incorrect. "
        else: logging.info("[Radio Group]: Configure SSID correctly")

        if ssid_suppres:
            if self.info['radiogroup_ssid_suppress'] in self.active_ap.get_ssid_suppress(self.wlan_if):
                logging.info("[Radio Group]: %s ssid supression succesfully" %
                             self.info['radiogroup_ssid_suppress'])
            else: error_msg += "SSID Suppression: incorrect. "
        else: error_msg += "SSID Supression is not configurable. "

        if self.active_ap.get_state(self.wlan_if) != self.info['radiogroup_state']:
            error_msg += "** Can not %s %s" % (self.info['radiogroup_state'], self.wlan_if.upper())
        else: logging.info("[Radio Group]: %s %s successfully" % (self.info['radiogroup_state'], self.wlan_if))

        if rts_thr:
            if self.info['radiogroup_rts_thr'] != self.active_ap.get_rts_thr(self.wlan_if):
                error_msg += "** RTS-THR: incorrect. "
            else: logging.info("[Radio Group]: configure RTS-THR correctly")
        else: error_msg += "** RTS-THR is not configurable. "

        rescan_info = self.active_ap.get_rescan_ap(self.wlan_if)
        if rescan_info != -1:
            rescan_ok = True
            for key in rescan_cfg.keys():
                if rescan_cfg[key] != rescan_info[key]:
                    rescan_ok = False
                    error_msg += "** Rescan: %s incorrect. " % key
            if rescan_ok:
                logging.info("[Radio Group]: Set rescan settings correctly")
        else: error_msg += 'Rescan options is not configurable. '

        if vodetect:
            if self.info['radiogroup_vodetect'] in self.active_ap.get_vo_detect(self.wlan_if):
                logging.info("[Radio Group]: Set Voice Call Detection Mode correctly")
            else: error_msg += "** Voice Call Detection: incorrect. "
        else: error_msg += "** Voice Call Detection is not configurable. "

        if self.active_ap.get_tx_power(self.wlan_if) != self.info['radiogroup_txpower']:
            error_msg += "** TxPower: incorrect. "
        else: logging.info("[Radio Group]: Set TxPower correctly")

        if wds:
            if not self.info['radiogroup_wds_mode'] in self.active_ap.get_wds_mode(self.wlan_if):
                error_msg += "** WDS Mode: incorrect. "
            else: logging.info("[Radio Group]: Set WDS mode succesfully")
        else: error_msg += "** WDS Mode is not configurable. "

        if wlan_txt:
            if self.active_ap.get_wlan_text(self.wlan_if) != self.info['radiogroup_wlantext']:
                error_msg += "** Wlan Description: incorrect. "
            else: logging.info("[Radio Group]: Configure wlan description successfully")
        else: error_msg += "** Wlan Description is not configurable. "

        if self.active_ap.get_wmm(self.wlan_if) != self.info['radiogroup_wmm']:
            error_msg += "** WMM status: incorrect. "
        else: logging.info("[Radio Group]: Set WMM correctly")

        class2mqpri_info = self.active_ap.get_class_2_mq_prio(self.wlan_if)
        if class2mqpri_info:
            if class2mqpri_info['voice'] != self.info['radiogroup_mqclass2pri_voice']:
                error_msg += "** Voice MQ Class To Priority Mapping: incorrect. "
            if class2mqpri_info['video'] != self.info['radiogroup_mqclass2pri_video']:
                error_msg += "** Video MQ Class To Priority Mapping: incorrect. "
            if class2mqpri_info['data'] != self.info['radiogroup_mqclass2pri_be']:
                error_msg += "** Data MQ Class To Priority Mapping: incorrect. "
            if class2mqpri_info['bk'] != self.info['radiogroup_mqclass2pri_bk']:
                error_msg += "BK MQ Class To Priority Mapping: incorrect. "
        else:
            error_msg += "** Can not get class2mqpri information. "

        if dvlan:
            if self.info['radiogroup_dvlan'] in self.active_ap.get_dvlan(self.wlan_if):
                logging.info("[Radio Group]: %s Dynamic VLAN Mode successfully" %
                             self.info['radiogroup_dvlan'])
            else: error_msg += "** Dynamic VLAN status: incorrect. "
        else: error_msg += "** Dynamic VLAN Mode is not configurable. "

        if self.version < '9.0':
            if frag_thr:
                if self.info['radiogroup_frag_thr'] != self.active_ap.get_frag_thr(self.wlan_if):
                    error_msg += "** Fragmentation Threshold: incorrect. "
                else: logging.info("[Radio Group]: Set Fragmentation Threshold correctly")
            else: error_msg += "** Fragmentation Threshold is not configurable. "

        fixed_rate_res = self.active_ap.get_fixed_rate(self.wlan_if)
        if fixed_rate_res.has_key('rate'):
            if fixed_rate_res['rate'] != self.info['radiogroup_fixed_rate']:
                error_msg += "** FixedRate: incorrect. "
            else: logging.info("[Radio Group]: Configure Fixed Rate for wlan interfaces successfully")
        else: error_msg += "** FixedRate is not configurable. "

        if res_80211h:
            if self.info['radiogroup_11h_status'] != self.active_ap.get_11h_status(self.wlan_if):
                error_msg += "** 802.11h status: incorrect. "
            else: logging.info("[Radio Group]: Configure 802.11h status successfully")
        else: error_msg += "** 802.11h status is not configurable. "

        if maxaid:
            if self.info['radiogroup_max_aid'] != self.active_ap.get_max_aid(self.wlan_if):
                error_msg += "** MaxAid: incorrect. "
            else: logging.info("[Radio Group]: Set the allowed maximum assoc ID succesffully")
        else: error_msg += "** MaxAid is not configurable. "

        if minrate:
            if self.info['radiogroup_minrate'] != self.active_ap.get_min_rate(self.wlan_if):
                error_msg += "** MinRate: incorrect. "
            else: logging.info("[Radio Group]: Configure min rate value suscessfully")
        else: error_msg += "** Min rate is not configurable. "

        if protmode:
            if self.info['radiogroup_prot_mode'] != self.active_ap.get_prot_mode(self.wlan_if):
                error_msg += "** Protection Mode: incorrect. "
            else: logging.info("[Radio Group]: Set protection mode for 11b/11g successfully")
        else: error_msg += "** Protection Mode is not configurable. "

        if bs_thr:
            if self.info['radiogroup_bandsteering'] != self.active_ap.get_band_steering_thr(self.wlan_if):
                error_msg += "** Band Steering Threshold: incorrect. "
            else: logging.info("[Radio Group]: Configure Band Steering Threshold successfully")
        else: error_msg += "** Band Steering Threshold is not configurable. "

        self.active_ap.clear_mqstats(self.wlan_if)
        mq_stats = self.active_ap.get_mqstats_def(self.wlan_if)
        ok = True
        for key, value in mq_stats.iteritems():
            if int(value):
                ok = False
                error_msg += "** Default MQ Stats: %s queue is not empty. " % key
                break
        if ok: logging.info("[Radio Group]: Clear Default MQ successfully")

        # Verify MQ result
        mq_after_set = self.active_ap.get_mq(self.wlan_if)
        for i in range(len(mq_opts)):
            if mq_res[i]:
                ok = True
                tmp = mq_opts[i]
                for key in tmp.keys():
                    if key == 'pscredit':
                        if tmp[key] != mq_after_set[key]:
                            error_msg += "** MQ %s: incorrect. " % mq_desc[i]
                            ok = False
                    else:
                        for key_opt in tmp[key].keys():
                            if tmp[key][key_opt] != mq_after_set[key][key_opt]:
                                error_msg += "** MQ %s ==> %s: incorrect. " % (mq_desc[i], key_opt.upper())
                                ok = False
                if ok:
                    logging.info("[Radio Group]: MQ %s options are set correctly" % mq_desc[i])
            else:
                error_msg += "** MQ %s option is not configurable. " % mq_desc[i]

        atcf_after_set = self.active_ap.get_auto_cfg(self.wlan_if)
        if not atcf_after_set:
            error_msg += "** Can not enable Autoconfig for %s on AP" % self.wlan_if
        else:
            for key in atcf_after_set.keys():
                if atcf_after_set[key] != atcf_value[key]:
                    error_msg += "** Autconfig option %s: incorrect. " % key.upper()
                else: logging.info("[Radio Group]: Autoconfig: configure %s successfully" % key.upper())

        # Verify DFS config
        if self.version < '9.0' and self.is5GHz:
            dfs_after_set = self.active_ap.get_dfs_info(self.wlan_if)
            tmp = [dfs_after_set['cactime'], dfs_after_set['notime'], dfs_after_set['blkchans']]
            for i in range(len(dfs_opts_res)):
                if dfs_opts_res[i]:
                    if tmp[i] != dfs_value[i]:
                        error_msg += "** DFS %s: incorrect. " % dfs_desc[i]
                    else: logging.info("[Radio Group]: configure DFS %s correctly" % dfs_desc[i])
                else: error_msg += "** DFS %s option is not configurable. " % dfs_desc[i]

            if dfs_sta:
                ok = True
                if self.info['radiogroup_dfs_status'] == 'enable':
                    if not dfs_after_set['enable']: ok = False
                else:
                    if dfs_after_set['enable']: ok = False

                if not ok: error_msg += "** Can not %s DFS status. " % self.info['radiogroup_dfs_status']
                else: logging.info("[Radio Group]: %s DFS status successfully")

            else: error_msg += "** DFS status is not configurable. "

        if dis:
            if self.active_ap.get_distance(self.wlan_if) != self.info['radiogroup_distance']:
                error_msg += "** Distance: incorrect. "
            else: logging.info("[Radio Group]: Set distance correctly")
        else: error_msg += "** Distance is not configurable. "

        if error_msg: return ["FAIL", error_msg]
        return ["PASS", ""]

    def _getActiveIntfEthAP(self):
        active_int = None
        eth_interface_info = self.active_ap.get_all_eth_interface()
        for interface in eth_interface_info:
            if interface['status'] == 'up':
                active_int = interface['interface']
        active_int = self._getIntfNum(active_int)
        return active_int

    def _getIntfNum(self, interface):
        pat_interface = "([0-9]+$)"
        num = -1
        inf_obj = re.search(pat_interface, interface)
        if inf_obj: num = int(inf_obj.group(1))
        else: raise Exception("Wrong interface name")
        return str(num)

