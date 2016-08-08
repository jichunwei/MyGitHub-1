# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: Vlan_Configuration class tests ability of queuing traffic when streaming with the given conditions.
    Author: Tam Nguyen
    Prerequisite (Assumptions about the state of the testbed/DUT):
    1. Build under test is loaded on the AP

    Required components: RuckusAP, StationLinuxPC
    Test parameters:        {'active_ap':'ip address of the tested AP',
                             'local_station':'ip address of local station',
                             'remote_station':'ip address of remote station',
                             'vlan_name':'name of a vlan',
                             'vlan_id':'id of a vlan',
                             'vlan_id_clone':'id of cloned vlan',
                             'vlan_id_change':'new ID of a vlan',
                             'vlan_swap':'id of a swapped vlan',
                             'eth_native_add':'Bool value. Decide if adding an Ethernet untagged port to a VLAN',
                             'eth_tagged_add':'Bool value. Decide if adding an Ethernet tagged port to a VLAN',
                             'wlan_native_add':'Bool value. Decide if adding a native wlan to a VLAN',
                             'eth_native_rem':'Bool value. Decide if removing an Ethernet untagged port out of a VLAN',
                             'eth_tagged_rem':'Bool value. Decide if removing an Ethernet tagged port out of a VLAN',
                             'wlan_native_rem':'Bool value. Decide if removing a native wlan out of a VLAN',
                             'max_vlan':'Bool value. Decide if creating maximum vlans on the AP',
                             'rem_vlan':'Bool value. Decide if removing a VLAN out of the AP',
                             'status_port':'Used to verify port status after removing/adding'}

    Result type: PASS/FAIL/N/A

    Results: PASS: if all the above criteria are satisfied.
             FAIL: If one of the above criteria is not satisfied.

    Messages: If FAIL the test script returns a message related to the criterion that is not satisfied.

    Test procedure:
    1. Config:
        - Look for the active AP, active adapter and local station and remote station in the testbed.
        - Save the current Encryption information on the active AP
    2. Test:
        - Turn on svcp interface on the active AP and active adapter
        - Verify connections between AP and adapter to make sure that adapter associate to the AP successfully
        - Create/change Vlan configuration option on the AP with information get from test parameters.
        - Verify by pinging

    3. Cleanup:
        - Remove all vlans
        - Return the previous Encryption configuration for the AP
        - Down svcp interface on the AP and adapter
"""


import time
import logging
import tempfile
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.Ratutils import *
import libIPTV_TestConfig as tconfig
import libIPTV_TestMethods as tmethod

class Vlan_Configuration(Test):
    required_components = ['RuckusAP', 'StationLinuxPC']
    parameter_description = {'active_ap':'ip address of the tested AP',
                             'local_station':'ip address of local station',
                             'remote_station':'ip address of remote station',
                             'vlan_name':'name of a vlan',
                             'vlan_id':'id of a vlan',
                             'vlan_id_clone':'id of cloned vlan',
                             'vlan_id_change':'new ID of a vlan',
                             'vlan_swap':'id of a swapped vlan',
                             'eth_native_add':'Bool value. Decide if adding an Ethernet untagged port to a VLAN',
                             'eth_tagged_add':'Bool value. Decide if adding an Ethernet tagged port to a VLAN',
                             'wlan_native_add':'Bool value. Decide if adding a native wlan to a VLAN',
                             'eth_native_rem':'Bool value. Decide if removing an Ethernet untagged port out of a VLAN',
                             'eth_tagged_rem':'Bool value. Decide if removing an Ethernet tagged port out of a VLAN',
                             'wlan_native_rem':'Bool value. Decide if removing a native wlan out of a VLAN',
                             'max_vlan':'Bool value. Decide if creating maximum vlans on the AP',
                             'rem_vlan':'Bool value. Decide if removing a VLAN out of the AP',
                             'status_port':'Used to verify port status after removing/adding'}
    def config(self, conf):
        self._defineTestParams(conf)
        self._getStations(conf)
        self._get_ip_addrs(conf)
        self._getActiveAP(conf)
        self._getADConfig(conf)
        self._saveConfig()

        self.net_prefix = '192.168'
        self.ip_vlan = "%s.%s.%s" % (self.net_prefix,
                                     str(self.local_sta_ip_addr.split('.')[-2]),
                                     self.vlan_id)

    def test(self):
        self._cfg_wlan(self.wlan_if)
        self._cfg_wlan(self.wlan_if, False)

        logging.info("Turn on svcp interface on this adapter")
        self.remote_station.set_ruckus_ad_state(self.ad_config, 'up', 'wlan0')

        if int(self.ap_channel) >= 52 and int(self.ap_channel) <= 140:
            dfs_info = self.active_ap.get_dfs_info(self.wlan_if)
            if dfs_info['enable']:
                start_time = time.time()
                while time.time() - start_time < dfs_info['cactime']:
                    bssid = tmethod.getBSSID(self.active_ap, self.wlan_if)
                    if bssid != "00:00:00:00:00:00": break
        time.sleep(2)
        tmethod.verifyStaConnection(self.local_station,
                                    self.local_sta_ip_addr, self.remote_sta_ip_addr)

        # Adding a new vlan
        if self.vlan_add: return self._addVLAN()

        # Verify vlan name
        if self.vlan_name: return self._verifyVlanName()

        # Clone VLAN
        if self.vlan_id_clone: return self._cloneVLAN()

        # Change VLAN ID
        if self.vlan_id_change: return self._changeVLANID()

        # Add tagged port
        if self.eth_tagged_add: return self._addTaggedPort()

        # Add untagged port
        if self.eth_native_add: return self._addNativePort()

        # Remove tagged port
        if self.eth_tagged_rem: return self._remTaggedPort()

        # Remove untagged port
        if self.eth_native_rem: return self._remNativePort()

        # Swap VLAN
        if self.vlan_swap: return self._swapVLAN()

        # Add native wlan
        if self.wlan_native_add: return self._addNativeWlan()

        # Remove native wlan
        if self.wlan_native_rem: return self._remNativeWlan()

        # Create max VLANs
        if self.max_vlan: return self._createMaxVlan()

        # Remove VLAN
        if self.rem_vlan: return self._remove_vlan()

        if self.status_port: return self._checkPortStatus()

    def cleanup(self):
        if self.active_ap:
            if self.ctrl_ap_ifname:
                if self.status_port:
                    eth_list = self.inactive_port + " " + self.active_port
                    for eth in eth_list.split(' '):
                        self.active_ap.set_vlan('1', 'port %s' % eth, 'add')
                else:
                    self.active_ap.set_vlan('1', 'port %s' % self.active_port, 'add')
                self.active_ap.ip_addr = self.ap_cur_ip_addr

            if self.wlan_native_rem:
                self.active_ap.set_vlan('1', 'wlan %s' % self.wlan_if_num, 'add')

            logging.info("Return the previous encryption for AP")
            self.active_ap.cfg_wlan(self.current_ap_encryption)

            logging.info("Down %s interface on the active AP" % self.wlan_if)
            self.active_ap.set_state(self.wlan_if, 'down')
            time.sleep(2)

            logging.info("Remove all VLANs in the AP")
            self.active_ap.remove_all_vlan()

            if self.ctrl_ap_ifname:
                # Reboot AP to remove all sub bridge interfaces that related to created VLANs
                self.active_ap.reboot()
                time.sleep(5)
                self.active_ap.login() # re-login after reboot

        if self.remote_station and self.local_station:
            if self.vlan_inf:
                logging.info("Return all previous configuration for local station")
                self.local_station.rem_vlan(self.vlan_inf)
                self.local_station.set_ip_addr(self.interface_vlan, self.local_sta_ip_addr)

            if self.vlan_id_change or self.vlan_swap:
                self.local_station.set_route('add', self.testbed.sta_wifi_subnet['network'],
                                            self.testbed.sta_wifi_subnet['subnet_mask'],
                                            self.interface_vlan)
            if self.ctrl_ap_ifname:
                self.local_station.rem_vlan(self.ctrl_ap_ifname)

            logging.info("Down svcp interface on the active Adapter")
            self.remote_station.set_ruckus_ad_state(self.ad_config, 'down', 'wlan0')

        logging.info("---------- FINISH ----------")

    def _getActiveIntfEthAP(self):
        active_int = None
        eth_interface_info = self.active_ap.get_all_eth_interface()
        for interface in eth_interface_info:
            if interface['status'] == 'up':
                active_int = interface['interface']
        active_int = self._getIntfNum(active_int)
        return active_int

    def _getInactiveIntfEthAP(self):
        eth_list = self.active_ap.get_all_eth_interface()
        temp = []
        for eth in eth_list:
            if self._getIntfNum(eth['interface']) != self.active_port:
                temp.append(str(self._getIntfNum(eth['interface'])))
        inactive_port = " ".join(temp)

        return inactive_port

    def _getIntfNum(self, interface):
        pat_interface = "([0-9]+$)"
        num = -1
        inf_obj = re.search(pat_interface, interface)
        if inf_obj: num = int(inf_obj.group(1))
        else: raise Exception("Wrong interface name")
        return str(num)

    def _getStations(self, conf):
        # Find exactly stations
        station_list = self.testbed.components['Station']
        self.remote_station = tconfig.getStation(conf['remote_station'], station_list)
        self.local_station = tconfig.getStation(conf['local_station'], station_list)

    def _saveConfig(self):
        logging.info("Save encryption information")
        self.current_ap_encryption = self.active_ap.get_encryption(self.wlan_if)
        self.current_ap_encryption['wlan_if'] = self.wlan_if

    def _defineTestParams(self, conf):
        logging.info('conf: %s' % pformat(conf))
        self.remote_station = None
        self.local_station = None
        self.active_ap = None
        self.ad_config = {}
        self.ctrl_ap_ifname = None

        self.vlan_id = conf['vlan_id']
        self.wlan_if = conf['wlan_if']
        self.wlan_if_num = self._getIntfNum(self.wlan_if)
        self.ap_channel = conf['ap_channel']

        if conf.has_key('vlan_add'):
            self.vlan_add = conf['vlan_add']
        else: self.vlan_add = False

        if conf.has_key('vlan_name'):
            self.vlan_name = conf['vlan_name']
        else: self.vlan_name = ''

        if conf.has_key('vlan_id_change'):
            self.vlan_id_change = conf['vlan_id_change']
        else: self.vlan_id_change = ''

        if conf.has_key('vlan_id_clone'):
            self.vlan_id_clone = conf['vlan_id_clone']
        else: self.vlan_id_clone = ''

        if conf.has_key('vlan_swap'):
            self.vlan_swap = conf['vlan_swap']
        else: self.vlan_swap = ''

        if conf.has_key('eth_native_add'):
            self.eth_native_add = conf['eth_native_add']
        else: self.eth_native_add = False

        if conf.has_key('eth_tagged_add'):
            self.eth_tagged_add = conf['eth_tagged_add']
        else: self.eth_tagged_add = False

        if conf.has_key('wlan_native_add'):
            self.wlan_native_add = conf['wlan_native_add']
        else: self.wlan_native_add = False

        if conf.has_key('eth_native_rem'):
            self.eth_native_rem = conf['eth_native_rem']
        else: self.eth_native_rem = False

        if conf.has_key('eth_tagged_rem'):
            self.eth_tagged_rem = conf['eth_tagged_rem']
        else: self.eth_tagged_rem = False

        if conf.has_key('wlan_native_rem'):
            self.wlan_native_rem = conf['wlan_native_rem']
        else: self.wlan_native_rem = False

        if conf.has_key('max_vlan'):
            self.max_vlan = conf['max_vlan']
        else: self.max_vlan = False

        if conf.has_key('rem_vlan'):
            self.rem_vlan = conf['rem_vlan']
        else: self.rem_vlan = False

        if conf.has_key('status_port'):
            self.status_port = conf['status_port']
        else: self.status_port = False

        self.timeout = "60"
        self.mgmt_vlan_id = "200"
        self.ctrl_ap_ip_addr = "192.168.200.200"
        self.ap_mgmt_vlan_ip_addr = "192.168.200.1"
        self.new_local_ip_addr = '1.1.1.1'
        self.vlan_inf = ''

    def _get_ip_addrs(self, conf):

        error_msg = "Can not find nay ip address belongs to subnet %s" % self.testbed.sta_wifi_subnet['network']

        self.ap_ip_addr = self.testbed.getAPIpAddrBySymName(conf['active_ap'])
        self.ad_ip_addr = self.testbed.getAdIpAddrBySymName(conf['active_ad'])

        # Find the ip address of interface that connected to the adapter on the local station and remote station
        self.local_sta_ip_addr, self.interface_vlan = tconfig.getLinuxIpAddr(self.local_station,
                                                                            self.testbed.sta_wifi_subnet, True)
        self.remote_sta_ip_addr = tconfig.getLinuxIpAddr(self.remote_station,
                                                        self.testbed.sta_wifi_subnet)

        if not self.local_sta_ip_addr or not self.remote_sta_ip_addr:
            raise Exception("[Linux STAs]: %s" % error_msg)

    def _getADConfig(self, conf):

        logging.info("Get active adapter configuration information")
        self.ad_config = tconfig.getADConfig(self.testbed,
                                     conf['active_ad'],
                                     self.testbed.ad_list)

    def _getActiveAP(self, conf):
        logging.info("Find the active AP object")
        self.active_ap = tconfig.getTestbedActiveAP(self.testbed,
                                            conf['active_ap'],
                                            self.testbed.components['AP'],
                                            self.ap_channel,
                                            self.wlan_if)

        logging.info("Remove all VLANs out of the active AP")
        self.active_ap.remove_all_vlan()
        self.active_port = self._getActiveIntfEthAP()
        self.inactive_port = self._getInactiveIntfEthAP()

    def _cfg_wlan(self, wlan_if, on_ap = True):
        wlan_cfg = dict(auth="open",
                        encryption="none",
                        ssid='VLAN_%s' % wlan_if,
                        wlan_if='%s' % wlan_if)
        if on_ap:
            logging.info("Configure a WLAN with SSID %s on the active AP" % wlan_cfg['ssid'])
            self.active_ap.cfg_wlan(wlan_cfg)
        else:
            ad_wlan_cfg = wlan_cfg.copy()
            ad_wlan_cfg['wlan_if'] = 'wlan0'
            logging.info("Configure a WLAN with SSID %s on Active Adapter" % wlan_cfg['ssid'])
            self.remote_station.cfg_wlan(self.ad_config, ad_wlan_cfg)

    def _defineVlanParams(self, native_wlan = '', vlan_name = '', eth_native_port = '', eth_tagged_port = '', vlan_id = ''):
        if not vlan_id: vlan_id = self.vlan_id

        vlan_cfg = dict(vlan_id=vlan_id)
        if native_wlan: vlan_cfg['native_wlan'] = native_wlan
        if vlan_name: vlan_cfg['vlan_name'] = vlan_name
        if eth_native_port: vlan_cfg['eth_native_port'] = eth_native_port
        if eth_tagged_port: vlan_cfg['eth_tagged_port'] = eth_tagged_port

        return vlan_cfg

    def _checkVlanInfo(self, vlanid):
        vlan_info_ap = None
        vlan_info = self.active_ap.get_vlan_info()
        for info in vlan_info:
            if (info['vlan_id'] == vlanid): vlan_info_ap = info
        return vlan_info_ap

    def _checkSimilarVlan (self, vlan1, vlan2):
        for key in vlan1.keys():
            if key != 'vlan_name' and key != 'vlan_id':
                if vlan1[key] != vlan2[key]:
                    return False
        return True

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

    def _addVLAN(self):
        vlan_cfg = self._defineVlanParams(native_wlan=self.wlan_if_num,
                                          eth_tagged_port=self.active_port,
                                          eth_native_port=self.inactive_port)

        logging.info("Add a new vlan with following information: %s" %
                     self._getVlanDebugMsg(vlan_cfg, False))
        self.active_ap.create_vlan(vlan_cfg)

        logging.info("Verify that VLAN %s is created successfully" % vlan_cfg['vlan_id'])
        # Check vlan information in AP
        vlan_info_conf = self._checkVlanInfo(self.vlan_id)
        if not vlan_info_conf:
            return ["FAIL", "Could not create a vlan"]
        else:
            for key in vlan_cfg.keys():
                for val in vlan_cfg[key]:
                    if not val in vlan_info_conf[key]:
                        logging.debug(self._getVlanDebugMsg(vlan_info_conf))
                        return ["FAIL", "The information of created VLAN [%s] is not correct" % self.vlan_id]
        logging.info("Create a VLAN with basic information successfully")
        return ["PASS", ""]

    def _verifyVlanName(self):
        logging.info("Setting VLAN name")
        vlan_cfg = self._defineVlanParams(native_wlan=self.wlan_if_num,
                                          vlan_name=self.vlan_name)
        self.active_ap.create_vlan(vlan_cfg)

        vlan_info_conf = self._checkVlanInfo(self.vlan_id)
        if vlan_info_conf['vlan_name'] != self.vlan_name:
            logging.debug("[VLAN %s]: Expected VLAN name: %s" % (self.vlan_id, self.vlan_name))
            logging.debug("[VLAN %s]: Received VLAN name: %s" % (self.vlan_id, vlan_info_conf['vlan_name']))
            return ["FAIL", "VLAN name is not set correctly"]

        logging.info("Setting VLAN name sucessfully")
        return ["PASS", ""]

    def _cloneVLAN(self):

        vlan_cfg = self._defineVlanParams(native_wlan=self.wlan_if_num,
                                          eth_native_port=self.inactive_port,
                                          eth_tagged_port=self.active_port)
        logging.info("Create a VLAN on the AP with following info: %s" %
                     self._getVlanDebugMsg(vlan_cfg, False))
        self.active_ap.create_vlan(vlan_cfg)

        logging.info("Clone VLAN %s to VLAN %s" % (self.vlan_id, self.vlan_id_clone))
        self.active_ap.clone_vlan(self.vlan_id_clone, self.vlan_id)

        logging.info("Verify that information of all VLANs is still correct after cloning")
        vlan_info_conf = self._checkVlanInfo(self.vlan_id)
        vlan_info_clone = self._checkVlanInfo(self.vlan_id_clone)

        if not vlan_info_clone:
            return ["FAIL", "Can not clone VLAN [%s] from VLAN [%s]" % (self.vlan_id_clone, self.vlan_id)]

        if not vlan_info_conf:
            return ["FAIL", "VLAN [%s] disappears after cloning to VLAN [%s]" %
                    (self.vlan_id, self.vlan_id_clone)]

        # Check the differnce between 2 Vlan.
        return self._checkClonedVlanInfo(vlan_info_conf, vlan_info_clone)

    def _checkClonedVlanInfo(self, old_vlan, cloned_vlan):

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
            for port in num_of_ports.split():
                if not port in cloned_vlan['eth_tagged_port'].split():
                    logging.debug(self._getVlanDebugMsg(cloned_vlan))
                    return ["FAIL", "[Cloned VLAN %s]: number of cloned eth ports are incorrect" %
                            cloned_vlan['vlan_id']]

            for wlan in num_of_wlans.split():
                if not wlan in cloned_vlan['tagged_wlan']:
                    logging.debug(self._getVlanDebugMsg(cloned_vlan))
                    return ["FAIL", "[Cloned VLAN %s]: number of cloned wlans are incorrect" %
                            cloned_vlan['vlan_id']]

        else: return ["FAIL", "Could not clone Ethernet ports/WLANs for VLAN [%s]" % cloned_vlan['vlan_id']]
        return ["PASS", ""]

    def _createVLANOnStation(self, ping=True, vlan_id = ''):
        if not vlan_id: vlan_id = self.vlan_id
        logging.info("On Local station: change IP address from %s to %s" %
                     (self.local_sta_ip_addr, self.new_local_ip_addr))
        self.local_station.set_ip_addr(self.interface_vlan, self.new_local_ip_addr)

        # Create VLAN on Test Engine
        logging.info("On local station: create VLAN %s" % vlan_id)
        self.vlan_inf = self.local_station.add_vlan(self.interface_vlan,
                                                   vlan_id, self.ip_vlan)
        if ping:
            logging.info("Verify that stations on VLAN [%s] can ping each other" % vlan_id)
            tmethod.verifyStaConnection(self.local_station, self.ip_vlan, self.remote_sta_ip_addr)

    def _changeVLANID(self):

        vlan_cfg = self._defineVlanParams(native_wlan=self.wlan_if_num,
                                          eth_tagged_port=self.active_port)
        logging.info("Create a VLAN on the AP with following info: %s" %
                     self._getVlanDebugMsg(vlan_cfg, False))
        self.active_ap.create_vlan(vlan_cfg)

        # Create Vlan on test engine
        self._createVLANOnStation()

        # Change VLAN ID on Test Engine
        self.local_station.rem_vlan(self.vlan_inf)
        self.vlan_inf = self.local_station.add_vlan(self.interface_vlan,
                                                   self.vlan_id_change,
                                                   self.ip_vlan)

        logging.info("On AP, Change VLAN ID from [%s] to [%s]" % (self.vlan_id, self.vlan_id_change))
        vlan_info_conf = self._checkVlanInfo(self.vlan_id)
        self.active_ap.change_vlan(self.vlan_id, self.vlan_id_change)
        vlan_info_change = self._checkVlanInfo(self.vlan_id_change)

        logging.info("Verify VLAN information after changing ID")
        if not vlan_info_change:
            return ["FAIL", "Could not change ID of VLAN [%] to [%]" % (self.vlan_id, self.vlan_id_change)]

        # Check if difference of Vlan after change.
        if not self._checkSimilarVlan(vlan_info_conf, vlan_info_change):
            return ["FAIL", "Information of VLAN [%s] is not correct after changing its ID to [%s]" %
                    (self.vlan_id, self.vlan_id_change)]
        logging.info("Change VLAN ID successfully")

        self.local_station.set_route('del', self.testbed.sta_wifi_subnet['network'],
                                    self.testbed.sta_wifi_subnet['subnet_mask'], self.interface_vlan)

        logging.info("Verify that stations on VLAN [%s] can ping each other" % self.vlan_id_change)
        tmethod.verifyStaConnection(self.local_station, self.ip_vlan, self.remote_sta_ip_addr)

        return ["PASS", ""]

    def _addTaggedPort(self):
        vlan_cfg = self._defineVlanParams(native_wlan=self.wlan_if_num)
        logging.info("Create a VLAN on the AP with following info: %s" %
                     self._getVlanDebugMsg(vlan_cfg, False))
        self.active_ap.create_vlan(vlan_cfg)

        # Create Vlan on test engine
        self._createVLANOnStation(False)

        logging.info("Add tagged port [%s] to VLAN [%s]" % (self.active_port, self.vlan_id))
        self.active_ap.set_vlan(self.vlan_id, 'port %s' % self.active_port, 'add', 'Yes')

        add_ok = True
        vlan_info_conf = self._checkVlanInfo(self.vlan_id)
        if vlan_info_conf.has_key('eth_tagged_port'):
            if not self.active_port in vlan_info_conf['eth_tagged_port']:
                logging.debug(self._getVlanDebugMsg(vlan_info_conf))
                add_ok = False
        else: add_ok = False
        if not add_ok:
            return ["FAIL", "Could not add tagged port to the VLAN %s" % self.vlan_id]

        logging.info(self._getVlanDebugMsg(vlan_info_conf))
        logging.info("Add Ethernet tagged port [%s] to VLAN [%s] succesffully" %
                     (self.active_port, self.vlan_id))

        logging.info("Check Ping from stations in VLAN %s through tagged port" % self.vlan_id)
        tmethod.verifyStaConnection(self.local_station, self.ip_vlan, self.remote_sta_ip_addr)

        return ["PASS", ""]

    def _addNativePort(self):
        # Add management VLAN for AP with tagged port, so Test Engine can control AP via this VLAN
        self._addMgmtVlan()

        vlan_cfg = self._defineVlanParams(native_wlan=self.wlan_if_num)
        logging.info("Create a VLAN on the AP with following info: %s" %
                     self._getVlanDebugMsg(vlan_cfg, False))
        self.active_ap.create_vlan(vlan_cfg)

        logging.info("Add Ethernet untagged port [%s] to VLAN %s" % (self.active_port, self.vlan_id))
        self.active_ap.set_vlan(self.vlan_id, 'port %s' % self.active_port, 'add')

        vlan_info_conf = self._checkVlanInfo(self.vlan_id)
        add_ok = True
        if vlan_info_conf.has_key('eth_native_port'):
            if not self.active_port in vlan_info_conf['eth_native_port']:
                logging.debug(self._getVlanDebugMsg(vlan_info_conf))
                add_ok = False
        else: add_ok = False
        if not add_ok:
            return ["FAIL", "Could not add untagged port to the VLAN %s" % self.vlan_id]

        logging.info(self._getVlanDebugMsg(vlan_info_conf))
        logging.info("Add Ethernet untagged port [%s] to VLAN [%s] succesffully" %
                     (self.active_port, self.vlan_id))

        logging.info("Check Ping from stations through untagged port")
        tmethod.verifyStaConnection(self.local_station, self.local_sta_ip_addr, self.remote_sta_ip_addr)
        return ["PASS", ""]

    def _remTaggedPort(self):

        vlan_cfg = self._defineVlanParams(native_wlan=self.wlan_if_num,
                                          eth_tagged_port=self.active_port)
        logging.info("Create a VLAN on the AP with following info: %s" %
                     self._getVlanDebugMsg(vlan_cfg, False))
        self.active_ap.create_vlan(vlan_cfg)

        # Configure VLAN on the TestEngine
        self._createVLANOnStation()

        logging.info("Remove tagged port [%s] out of VLAN [%s]" % (self.active_port, self.vlan_id))
        self.active_ap.set_vlan(self.vlan_id, 'port %s' %self.active_port, 'del', tag = 'Yes')

        vlan_info_conf = self._checkVlanInfo(self.vlan_id)
        if vlan_info_conf.has_key('eth_tagged_port'):
            if self.active_port in vlan_info_conf['eth_tagged_port']:
                logging.debug(self._getVlanDebugMsg(vlan_info_conf))
                return ["FAIL", "Could not removing tagged port out of VLAN %s" % self.vlan_id]

        logging.info(self._getVlanDebugMsg(vlan_info_conf))
        logging.info("Remove Ethernet tagged port [%s] out of VLAN [%s] succesffully" %
                     (self.active_port, self.vlan_id))

        logging.info("Verify that traffic from VLAN %s can not go" % self.vlan_id)
        tmethod.verifyStaConnection(self.local_station, self.ip_vlan, self.remote_sta_ip_addr, 5000, False)
        return ["PASS", ""]

    def _addMgmtVlan (self):
        ap_net = get_network_address(self.ap_ip_addr)
        ctrl_ap_ip, self.ctrl_ap_ifname = tconfig.getLinuxIpAddr(self.local_station, ap_net, True)
        self.ap_cur_ip_addr = self.ap_ip_addr
        self.ctrl_ap_ifname = self.local_station.add_vlan(self.ctrl_ap_ifname,
                                                         self.mgmt_vlan_id,
                                                         self.ctrl_ap_ip_addr)
        self.active_ap.create_vlan(dict(vlan_id=self.mgmt_vlan_id,
                                       eth_tagged_port=self.active_port))
        res, msg = self.active_ap.add_ip_to_brd_intf("br0.%s" % self.mgmt_vlan_id, self.ap_mgmt_vlan_ip_addr)
        if not res:
            raise Exception(msg)
        # From now, TestEngine will telnet to AP by new ip_addr
        self.ap_cur_ip_addr = self.active_ap.ip_addr
        self.active_ap.ip_addr = self.ap_mgmt_vlan_ip_addr

    def _remNativePort(self):
        # Add management VLAN for AP with tagged port, so Test Engine can control AP via this VLAN
        self._addMgmtVlan()

        vlan_cfg = self._defineVlanParams(native_wlan=self.wlan_if_num,
                                          eth_native_port=self.active_port)
        logging.info("Create a VLAN on the AP with following info: %s" %
                     self._getVlanDebugMsg(vlan_cfg, False))
        self.active_ap.create_vlan(vlan_cfg)

        logging.info("Check Ping from stations through untagged port")
        tmethod.verifyStaConnection(self.local_station, self.local_sta_ip_addr, self.remote_sta_ip_addr)

        logging.info("Remove untagged port [%s] out of VLAN [%s]" % (self.active_port, self.vlan_id))
        self.active_ap.set_vlan(self.vlan_id, 'port %s' % self.active_port, 'del')

        # Check Vlan after removing untagged port
        vlan_info_conf_check = self._checkVlanInfo(self.vlan_id)
        if vlan_info_conf_check.has_key('eth_native_port'):
            if self.active_port in vlan_info_conf_check['eth_native_port']:
                logging.debug(self._getVlanDebugMsg(vlan_info_conf_check))
                return ["FAIL", "Untagged port still exists after being removed"]

        logging.info(self._getVlanDebugMsg(vlan_info_conf_check))
        logging.info("Remove Ethernet untagged port [%s] out of VLAN [%s] succesffully" %
                     (self.active_port, self.vlan_id))

        logging.info("Verify ping after removing untagged port out of VLAN %s" % self.vlan_id)
        tmethod.verifyStaConnection(self.local_station, self.local_sta_ip_addr, self.remote_sta_ip_addr, 5000, False)

        return ["PASS", ""]

    def _swapVLAN(self):
        vlan_cfg = self._defineVlanParams(native_wlan=self.wlan_if_num,
                                          eth_tagged_port=self.active_port)
        vlan_cfg_swap = self._defineVlanParams(eth_native_port=self.inactive_port,
                                          eth_tagged_port=self.active_port, vlan_id=self.vlan_swap)
        logging.info("Create VLAN %s and VLAN %s on the AP" % (self.vlan_id, self.vlan_swap))
        self.active_ap.create_vlan(vlan_cfg)
        self.active_ap.create_vlan(vlan_cfg_swap)

        logging.info(self._getVlanDebugMsg(vlan_cfg))
        logging.info(self._getVlanDebugMsg(vlan_cfg_swap))

        # Create Vlan on test engine
        self._createVLANOnStation()

        logging.info("Swap VLAN [%s] with VLAN [%s]" % (self.vlan_id, self.vlan_swap))
        vlan_info_conf = self._checkVlanInfo(self.vlan_id)
        self.active_ap.swap_vlan(self.vlan_swap, self.vlan_id)
        vlan_info_swap = self._checkVlanInfo(self.vlan_swap)
        # Check Vlan after swap.
        if not self._checkSimilarVlan(vlan_info_conf, vlan_info_swap):
            return ["FAIL", "Information of VLAN is not correct after swapping"]

        # Change VLAN ID on Test Engine
        self.local_station.rem_vlan(self.vlan_inf)
        self.vlan_inf = self.local_station.add_vlan(self.interface_vlan,
                                                   self.vlan_swap,
                                                   self.ip_vlan)
        self.local_station.set_route('del', self.testbed.sta_wifi_subnet['network'],
                                    self.testbed.sta_wifi_subnet['subnet_mask'], self.interface_vlan)
        logging.info("Verify that now stations in VLAN [%s] can talk each other" % self.vlan_swap)
        tmethod.verifyStaConnection(self.local_station, self.ip_vlan, self.remote_sta_ip_addr)

        return ["PASS", ""]

    def _addNativeWlan(self):
        vlan_cfg = self._defineVlanParams(eth_tagged_port=self.active_port)
        logging.info("Create a VLAN on the AP with following info: %s" %
                     self._getVlanDebugMsg(vlan_cfg, False))
        self.active_ap.create_vlan(vlan_cfg)

        # Create VLAN on TestEngine
        self._createVLANOnStation(False)

        msg = "Verify that stations in VLAN [%s] can not talk each other " % self.vlan_id
        msg += "because there's no WLAN interface added to this VLAN"
        logging.info(msg)
        tmethod.verifyStaConnection(self.local_station, self.ip_vlan, self.remote_sta_ip_addr, 5000, False)

        logging.info("Add native wlan to the VLAN [%s]" % self.vlan_id)
        self.active_ap.set_vlan(self.vlan_id, 'wlan %s' % self.wlan_if_num, 'add')
        time.sleep(10)

        vlan_info_add_wlan = self._checkVlanInfo(self.vlan_id)
        add_ok = True
        if vlan_info_add_wlan.has_key('native_wlan'):
            if not self.wlan_if_num in vlan_info_add_wlan['native_wlan']:
                logging.info(self._getVlanDebugMsg(vlan_info_add_wlan))
                add_ok = False
        else: add_ok = False
        if not add_ok:
            return ["FAIL", "Could not add native wlan to the VLAN %s" % self.vlan_id]

        logging.info(self._getVlanDebugMsg(vlan_info_add_wlan))
        logging.info("Add native wlan to VLAN [%s] succesffully" % self.vlan_id)

        logging.info("Verify that stations in VLAN [%s] can ping each other" % self.vlan_id)
        tmethod.verifyStaConnection(self.local_station, self.ip_vlan, self.remote_sta_ip_addr)

        return ["PASS", ""]

    def _remNativeWlan(self):
        vlan_cfg = self._defineVlanParams(native_wlan=self.wlan_if_num,
                                          eth_tagged_port=self.active_port)
        logging.info("Create a VLAN on the AP with following info: %s" %
                     self._getVlanDebugMsg(vlan_cfg, False))
        self.active_ap.create_vlan(vlan_cfg)

        # Create VLAN on Test Engine
        self._createVLANOnStation(True)

        logging.info("Remove native wlan out of VLAN [%s]" % self.vlan_id)
        self.active_ap.set_vlan(self.vlan_id, 'wlan %s' % self.wlan_if_num, 'del')

        vlan_info_remgmt_vlan = self._checkVlanInfo(self.vlan_id)
        if vlan_info_remgmt_vlan.has_key('native_wlan'):
            if self.wlan_if_num in vlan_info_remgmt_vlan['native_wlan']:
                logging.debug(self._getVlanDebugMsg(vlan_info_remgmt_vlan))
                return ["FAIL", "Could not remove native wlan out of VLAN"]

        logging.info(self._getVlanDebugMsg(vlan_info_remgmt_vlan))
        logging.info("Remove native wlan out of VLAN [%s] succesffully" % self.vlan_id)

        msg = "Verify that stations in VLAN [%s] can not talk each other " % self.vlan_id
        msg += "because WLAN is removed out of the VLAN"
        logging.info(msg)
        tmethod.verifyStaConnection(self.local_station, self.ip_vlan, self.remote_sta_ip_addr, 5000, False)

        return ["PASS", ""]

    def _createMaxVlan(self):

        max_vlan = len(self.active_ap.get_wlan_info_dict())
        logging.info("Create maximum VLANs on the AP (%d VLANs)" % max_vlan)
        tested_vlan_id = ''
        i=0
        while (i < max_vlan):
            wlan = 'wlan %s' %i
            vlan_id = str(10+i)
            wlan_if_num = self._getIntfNum("wlan%s" % i)
            vlan_cfg = dict(vlan_id=vlan_id,
                            native_wlan=wlan_if_num,
                            eth_tagged_port=self.active_port)
            logging.info('vlan_cfg: %s' % pformat(vlan_cfg))
            self.active_ap.create_vlan(vlan_cfg)

            vlan_check = self._checkVlanInfo(vlan_id)
            if not vlan_check:
                return ["FAIL", "Could not create VLAN %s with wlan%s" % (vlan_id, i)]
            logging.info("Create a VLAN with following information successfully: %s" %
                         self._getVlanDebugMsg(vlan_check, False))
            if self.wlan_if_num == wlan_if_num: tested_vlan_id = vlan_id
            i = i + 1

        logging.info("Add maximun VLANs to the AP successfully")
        # Make sure that traffic can go through VLAN
        logging.info("Pick up a VLAN %s then verify ping traffic" % tested_vlan_id)
        self._createVLANOnStation(True, tested_vlan_id)
        return ["PASS", ""]

    def _remove_vlan(self):
        vlan_cfg = self._defineVlanParams(native_wlan=self.wlan_if_num,
                                          eth_tagged_port=self.active_port)
        logging.info("Create a VLAN on the AP with following info: %s" %
                     self._getVlanDebugMsg(vlan_cfg, False))
        self.active_ap.create_vlan(vlan_cfg)

        # Configure VLAN on the TestEngine
        self._createVLANOnStation()

        logging.info("Remove VLAN %s out of the AP" % self.vlan_id)
        self.active_ap.remove_vlan(self.vlan_id)

        check_vlan = self._checkVlanInfo(self.vlan_id)
        if check_vlan:
            return ["FAIL", "VLAN %s still exists after being removed" % self.vlan_id]

        logging.info("Verify that stations from VLAN %s can not talk each other anymore" % self.vlan_id)
        tmethod.verifyStaConnection(self.local_station, self.ip_vlan, self.remote_sta_ip_addr, 5000, False)
        return ["PASS", ""]

    def _checkPortStatus(self):
        msg, eth_port_list = '', self.inactive_port + " " + self.active_port
        self._addMgmtVlan()

        vlan_cfg = self._defineVlanParams(native_wlan=self.wlan_if_num,
                                          eth_native_port=eth_port_list)
        self.active_ap.create_vlan(vlan_cfg)

        logging.info("Add tagged port to the VLAN %s" % self.active_port)
        self.active_ap.set_vlan(self.vlan_id, 'port %s' %self.active_port, 'del',)
        self.active_ap.set_vlan(self.vlan_id, 'port %s' %self.active_port, 'add', 'Yes')

        # Check vlan info before remove tagged port
        vlan_info_conf = self._checkVlanInfo(self.vlan_id)
        logging.info(self._getVlanDebugMsg(vlan_info_conf))

        logging.info("Remove tagged port that has just added")
        self.active_ap.set_vlan(self.vlan_id, 'port %s' %self.active_port, 'del', 'Yes')

        # Verify status of all Ethernet ports again after removing tagged port
        vlan_info_conf_rem = self._checkVlanInfo(self.vlan_id)
        if vlan_info_conf_rem.has_key('eth_native_port'):
            if vlan_info_conf['eth_native_port'] != vlan_info_conf_rem['eth_native_port']:
                msg = "Status of Ethernet native ports change after removing tagged port"
        else:
            msg = "Ethernet native ports disappear after removing tagged port"
        if msg:
            return ("FAIL", msg)
        return ["PASS", msg]
