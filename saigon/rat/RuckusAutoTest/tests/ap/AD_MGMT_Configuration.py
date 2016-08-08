# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: AD_MGMT_Configuration class tests the changing of SSID/Encryption method from adapter WebUI as well as
getting device status of adapter from its WebUI.
    Author: Tam Nguyen
    Prerequisite (Assumptions about the state of the testbed/DeviceUnderTest):

    1. Build under test is loaded on the AP
    Required components: RuckusAP, StationLinuxPC, StationWinPC
    Test parameters: {'active_ap': 'ip address of the tested AP',
                      'active_ad': 'ip address of the tested adapter',
                      'ip': 'ip address to ping. This is the ip address of station behind the AP',
                      'remote_win_sta': 'ip address of Windows PC',
                      'remote_linux_sta': 'ip address of remote station behind the active adapter',
                      'change_ssid': 'This is the bool value used to determine if the script changes ssid value or not',
                      'verify_status': 'This is the bool value used to determine if the script will verify status or
                                        change configuration on the adapter'}

    Result type: PASS/FAIL
    Results: PASS: Verify that device status shown on the adapter WebUI is the same as the one shown at CLI.
                   And verify that after changing SSID/Encryption method on the adapter WebUI, on the active AP,
                   the adapter can associate to the AP successfully.
             FAIL: If one of the above criteria is not safisfied.

    Messages: If FAIL the test script returns a message related to the criterion that is not satisfied.

    Test procedure:
    1. Config:
        - Look for the active AP, active adapter and target station and remote station in the testbed.
        - Save the current link-local management configuration on the active AP and active adapter
        - If test script is changing SSID value for adapters and AP, save the current SSID of these devices
        - If test script is changing encryption method for adapters and AP, save the current encryption method
        of these devices
    2. Test:
        - Turn off all wlans on non-active APs
        - Enable link-local management on the active AP and active adapter
        - Turn on svcp interface on the active AP and adapters
        - Verify connections between AP and adapters to make sure that adapters associate to the AP successfully
        - If verify_status is True:
            + Get device status of adapter from its WebUI and compare them with the one shows on CLI.
            Verify that that information is the same.
            + Configure/view Home Setting Protection from adapter WebUI
        - If verify_status is False:
            + if change_ssid is True:
                - Change SSID of active adapter from its WebUI. Verify that SSID changed from here successfully
                - Change SSID for the AP and remaining adapter so that their SSID is the same as the one configured
                on WebUI of the active adapter
                - Verify connection between AP and active adapter again to make sure that adapter can associate to the AP
                successfully after changing SSID from its WebUI
            + If change_ssid is False:
                - Change encryption method of active adapter from its WebUI. Verify that encryption method is
                changed successfully
                - Change encryption method for the AP and remaining adapter so that their encryption method is
                the same as the onne configured on WebUI of the active adapter
                - Verify connection between AP and active adapter again to make sure that adapter can associate to the AP
                successfully after changing encryption method from its WebUI
    3. Cleanup:
        - Return the previous configuration of link-local management on the AP and AD
        - Down svcp interface on the AP and adapters
        - If verify_status is True, return the previous Home Setting Protection status for the active adapter
        from its WebUI
        - If change_ssid is True, return the previous SSID for adapters and AP
        - If change_ssid is False, return the previous encryption method for adapters and AP

    How is it tested:
        - Change SSID for only active adapter from its WebUI, the script should return FAIL and report
        that the active adapter does not associate to the AP after change SSID.
        - Change encryption method for only active adapter from its WebUI, the script should return FAIL and report that
        the active adapter does not associate to the AP after change encryption method.
"""

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.Ratutils import *
from libIPTV_TestConfig import *
from libIPTV_TestMethods import *

class AD_MGMT_Configuration(Test):
    required_components = ['RuckusAP', 'StationLinuxPC', 'StationWinPC']
    parameter_description = {'active_ap': 'ip address of the tested AP',
                             'active_ad': 'ip address of tested adapter',
                             'passive_ad': 'ip address of the adapter in front of windows station',
                             'ip': 'ip address to ping. This is the ip address of station behind the AP',
                             'remote_linux_sta': 'ip address of remote station behind the active adapter',
                             'remote_win_sta': 'ip address of windows station',
                             'change_ssid': 'This is the bool value used to determine if the script changes \
                                                ssid value or not',
                             'verify_status': 'This is the bool value used to determine if the script will verify \
                                              status or change configuration on the adapter'}
    def config(self, conf):

        self._defineTestParams(conf)
        self._getStations(conf)

        logging.info("Find the active AP object")
        self.active_ap = getTestbedActiveAP(self.testbed, conf['active_ap'], self.testbed.components['AP'],
                                            self.ap_channel, self.wlan_if)

        self._get_ip_addrs(conf)
        self._getADConfig(conf)

        # Define configuration information for adapter WebUI
        self.active_ad_webui_config = self.active_ad_config.copy()
        self.active_ad_webui_config['browser_type'] = self.browser_type
        del self.active_ad_webui_config['ip_addr']
        if self.verify_status:
            self.active_ad_webui_config['username'] = "admin"
            self.active_ad_webui_config['password'] = 'password'

        logging.info("Save the current link-local management configuration on the active AP and active AD")
        self.cur_ap_sta_mgmt = self.active_ap.get_sta_mgmt(self.wlan_if)
        self.cur_ad_sta_mgmt = self.remote_linux_sta.get_ad_sta_mgmt(self.active_ad_config, 'wlan0')

        if not self.verify_status:
            if self.change_ssid:
                logging.info("Save the current SSID configured on the adapter %s" % self.active_ad_ip_addr)
                self.cur_ssid = self.remote_linux_sta.get_ad_ssid(self.active_ad_config, 'wlan0')
                self.new_ssid = "IPTV_ADAPTER_MGMT"
            else:
                logging.info("Save the current encryption configuration on the adapter %s" % self.active_ad_ip_addr)
                self.cur_encryption = self.remote_linux_sta.get_ad_encryption(self.active_ad_config, 'wlan0')
                self.new_encryption = {'auth':'PSK', 'encryption':'AES', 'key_string':'1234567890', 'wpa_ver':'WPA2'}

    def test(self):

        logging.info("Enable http and https service on the AP %s" % self.ap_ip_addr)
        self.active_ap.set_http_status(True)
        self.active_ap.set_https_status(True)

        wlan_cfg = dict(auth="open",
                        encryption="none",
                        ssid='IPTV_%s' % self.wlan_if,
                        wlan_if='%s' % self.wlan_if)
        logging.info("Configure a WLAN with SSID %s on the active AP" % wlan_cfg['ssid'])
        self.active_ap.cfg_wlan(wlan_cfg)

        ad_wlan_cfg = wlan_cfg.copy()
        ad_wlan_cfg['wlan_if'] = 'wlan0'
        logging.info("Configure a WLAN with SSID %s  on the active adapter" % wlan_cfg['ssid'])
        self.remote_linux_sta.cfg_wlan(self.active_ad_config, ad_wlan_cfg)
        self.remote_win_sta.cfg_wlan(self.passive_ad_conf, ad_wlan_cfg)

        logging.info("Turn on the svcp interface on adapters")
        self.remote_linux_sta.set_ruckus_ad_state(self.active_ad_config, 'up', 'wlan0')
        self.remote_win_sta.set_ruckus_ad_state(self.passive_ad_conf, 'up', 'wlan0')

        # Check connectivity
        verifyStaConnection(self.remote_linux_sta, self.linux_sta_ip_addr, self.ip_addr)

        # Add  one more IP address to the windows station
        subnet_tmp = get_network_address(self.video_ip_addr)
        win_ip_tmp = ".".join(subnet_tmp.split('.')[:-1]) + "." + self.win_sta_ip_addr.split('.')[-1]
        mask_tmp = get_subnet_mask(self.video_ip_addr, False)

        msg = "Add an IP address that belongs to subnet %s on the station %s. " % (subnet_tmp, self.win_sta_ip_addr)
        msg += "So that this station can access to AP WebUI"
        logging.info(msg)

        self.remote_win_sta.verify_if(self.win_sta_ip_addr)
        if_info = self.remote_win_sta.get_if_info()

        if_name = ""
        for key, value in if_info.iteritems():
            for item in value:
                if item['addr'] == self.win_sta_ip_addr:
                    if_name = key
                    break
        self.remote_win_sta.add_ip_if(if_name, win_ip_tmp, mask_tmp)
        verifyStaConnection(self.remote_win_sta, self.win_sta_ip_addr, self.video_ip_addr)

        logging.info("Enable link-local management on the active AP %s" % self.ap_ip_addr)
        self.active_ap.set_sta_mgmt(self.wlan_if, True)

        # Enable sta-mgmt feature on the adapter
        logging.info("Enable link-local management on the active adapter %s" % self.active_ad_ip_addr)
        self.remote_linux_sta.set_ad_sta_mgmt(self.active_ad_config, 'wlan0', True)
        time.sleep(2)

        logging.info("Verify that STA-Management on the adapter is enabled and is in active state")
        res, msg = verifyStaMGMT(None, self.remote_linux_sta, self.check_status_timeout, self.active_ad_config)
        if res == "FAIL":
            return [res, msg]

        if not self.verify_status:
            if self.change_ssid:
                res = self._changeSSID(self.new_ssid, False)
                if res[0] == "FAIL":
                    return res
            else:
                res = self._changeEncryption(self.new_encryption, False)
                if res[0] == "FAIL":
                    return res
        else:
            logging.info("Verify that device status shown on the adapter WebUI is the same as the one configured at CLI")

            port = 25400 + getAID(self.active_ap, self.active_ad_ip_addr, self.active_ad_mac, self.check_status_timeout)
            url = "http://%s:%d" % (self.video_ip_addr, port)
            self.active_ad_webui_config['url'] = url
            status_res = self.remote_win_sta.get_ad_device_status_web_ui(self.active_ad_webui_config)
            time.sleep(5)

            if self.ad_model.lower() == "vf7111":
                ad_mac = self.remote_linux_sta.get_ad_base_mac(self.active_ad_config)
            else:
                ad_mac = self.active_ad_mac
            if status_res['mac'].lower() != ad_mac.lower():
                logging.debug("MAC address shown on WebUI: %s" % status_res['mac'].lower())
                logging.debug("MAC address shown on CLI: %s" % ad_mac.lower())
                return ["FAIL", "Mac address shown WebUI is not the same as the one shown on CLI"]

            serial_num = self.remote_linux_sta.get_ad_serial_num(self.active_ad_config)
            if status_res['serial_num'].lower() != serial_num.lower():
                logging.debug("Serial number shown on WebUI: %s" % status_res['serial_num'].lower())
                logging.debug("Serial number shown on CLI: %s" % serial_num.lower())
                return ["FAIL", "Serial number shown on WebUI is not the same as the one shown on CLI"]

            version = self.remote_linux_sta.get_ad_version(self.active_ad_config)
            if status_res['version'].lower() != version.lower():
                logging.debug("Software version shown on the WebUI: %s" % status_res['version'].lower())
                logging.debug("Software version shown on CLI: %s" % version.lower())
                return ["FAIL", "Software version shown on WebUI is not the same as the one shown on CLI"]

            logging.info("Verify status of Home Setting Protection")
            self.home_protection = status_res['home_protection']
            temp_config = self.active_ad_webui_config.copy()
            temp_config['username'] = self.active_ad_config['username']
            temp_config['password'] = self.active_ad_config['password']
            if not self.home_protection:
                logging.info("Home Setting Protection is in Disabled status now")
                logging.info("Verify that station can see Home login information from WebUI by Super user")
                res = self.remote_win_sta.get_ad_home_login_info(temp_config)
                if not res or not res.has_key('username') or not res.has_key('password'):
                    msg = "Station does not see Home login information when login to "
                    msg += "adapter WebUI by Super user while Home Setting Protection is disabled"
                    return ["FAIL", msg]

                logging.info("Try to enable this feature from WebUI of adapter %s" % self.active_ad_ip_addr)
                self.remote_win_sta.set_ad_home_protection_web_ui(self.active_ad_webui_config, True)
                time.sleep(3)

                logging.info("Home Setting Protection is in Enabled status now")
                logging.info("Verify that station can not see Home login information from WebUI by Super user")
                res = self.remote_win_sta.get_ad_home_login_info(temp_config)
                if res:
                    msg = "Station can see Home login information when login to "
                    msg += "adapter WebUI by Super user while Home Setting Protection is enabled"
                    return ["FAIL", msg]
            else:
                logging.info("Home Setting Protection is in Enabled status now")
                logging.info("Verify that station can not see Home login information from WebUI by Super user")
                res = self.remote_win_sta.get_ad_home_login_info(temp_config)
                if res:
                    msg = "Station can see Home login information when login to "
                    msg += "adapter WebUI by Super user while Home Setting Protection is enabled"
                    return ["FAIL", msg]

                logging.info("Try to disable this feature from WebUI of adapter %s" % self.active_ad_ip_addr)
                self.remote_win_sta.set_ad_home_protection_web_ui(self.active_ad_webui_config, False)
                time.sleep(3)

                logging.info("Home Setting Protection is in Disabled status now")
                logging.info("Verify that station can see Home login information from WebUI by Super user")
                res = self.remote_win_sta.get_ad_home_login_info(temp_config)
                if not res or not res.has_key('username') or not res.has_key('password'):
                    msg = "Station does not see Home login information when login to "
                    msg += "adapter WebUI by Super user while Home Setting Protection is disabled"
                    return ["FAIL", msg]

        return ["PASS", ""]

    def cleanup(self):
        if self.remote_win_sta and self.remote_linux_sta and self.active_ap and self.active_ad_config and \
        self.passive_ad_conf:
            if self.verify_status:
                if self.home_protection:
                    logging.info("Return the previous Home Setting Protection status for active adapter %s" %
                                 self.active_ad_ip_addr)
                    self.remote_win_sta.set_ad_home_protection_web_ui(self.active_ad_webui_config, self.home_protection)
                    time.sleep(3)
            else:
                if self.change_ssid:
                    res, msg = self._changeSSID(self.cur_ssid, True)
                    if res == "FAIL":
                        raise Exception(msg)
                else:
                    res, msg = self._changeEncryption(self.cur_encryption, True)
                    if res == "FAIL":
                        raise Exception(msg)

            logging.info("Remove ip address out of the interface that connecting to adapter %s" % self.passive_ad_ip_addr)
            self.remote_win_sta.verify_if(self.win_sta_ip_addr)

            logging.info("Return the previous sta-mgmt status of AP %s" % self.ap_ip_addr)
            self.active_ap.set_sta_mgmt(self.wlan_if, self.cur_ap_sta_mgmt['enable'])

            logging.info("Return the previous sta-mgmt on the active adapter %s" % self.active_ad_ip_addr)
            self.remote_linux_sta.set_ad_sta_mgmt(self.active_ad_config, 'wlan0', self.cur_ad_sta_mgmt['enable'])

            logging.info("Turn off svcp interface on the adapter %s" % self.passive_ad_ip_addr)
            self.remote_win_sta.set_ruckus_ad_state(self.passive_ad_conf, 'down', 'wlan0')

            logging.info("Turn off svcp interface on the active AP %s" % self.ap_ip_addr)
            self.active_ap.set_state(self.wlan_if, 'down')

            logging.info("Turn off the svcp interface on the active adapter %s" % self.active_ad_ip_addr)
            self.remote_linux_sta.set_ruckus_ad_state(self.active_ad_config, 'down', 'wlan0')

            logging.info("---------- FINISH ----------")

    def _changeSSID(self, new_ssid, return_ssid = False):
        """
        This function uses to change SSID value for adapter or AP
        @param new_ssid: new ssid value
        @return_ssid: this is the bool value used to define logging message
        """
        if not return_ssid:
            logging.info("Change SSID of active adapter %s to %s via adapter WebUI" %
                         (self.active_ad_ip_addr, new_ssid))

            port = 25400 + getAID(self.active_ap, self.active_ad_ip_addr, self.active_ad_mac, self.check_status_timeout)
            url = "http://%s:%d" % (self.video_ip_addr, port)
            self.active_ad_webui_config['url'] = url
            if self.ad_model.lower() == "vf7111":
                self.remote_win_sta.set_ad_ssid_web_ui(self.active_ad_webui_config, new_ssid, True)
            else:
                self.remote_win_sta.set_ad_ssid_web_ui(self.active_ad_webui_config, new_ssid, False)
            time.sleep(5)

            logging.info("Verify that SSID of the active adapter %s is changed successfully" % self.active_ad_ip_addr)
            get_ssid = self.remote_linux_sta.get_ad_ssid(self.active_ad_config, 'wlan0')
            if get_ssid != new_ssid:
                logging.debug("Correct SSID --------> %s" % new_ssid)
                logging.debug("Current SSID --------> %s" % get_ssid)
                return ["FAIL", "The SSID is not correct when changing it from adapter WebUI"]
            logging.info("Change SSID from adapter WebUI successfully")

        else:
            logging.info("Return the previous SSID (%s) for the adapter %s" % (new_ssid, self.active_ad_ip_addr))
            self.remote_linux_sta.set_ad_ssid(self.active_ad_config, 'wlan0', new_ssid)

        if not return_ssid:
            logging.info("Change SSID of video network on the active AP %s to %s" %
                     (self.ap_ip_addr, new_ssid))
        else:
            logging.info("Return the previous SSID (%s) for the active AP %s" % (new_ssid, self.ap_ip_addr))
        self.active_ap.set_ssid(self.wlan_if, new_ssid)

        if not return_ssid:
            logging.info("Change SSID on the adapter %s to %s" % (self.passive_ad_ip_addr, new_ssid))
        else:
            logging.info("Return the previous SSID (%s) for the adapter %s" % (new_ssid, self.passive_ad_ip_addr))
        self.remote_win_sta.set_ad_ssid(self.passive_ad_conf, 'wlan0', new_ssid)

        logging.info("Verify that after chaning SSID, adapters can associate to the AP %s successfully" %
                     self.ap_ip_addr)
        # Verify connectivity between active adapter and active AP
        try:
            verifyStaConnection(self.remote_linux_sta, self.linux_sta_ip_addr, self.ip_addr)
        except Exception, e:
            return ["FAIL", "Adapter %s does not associate to the active AP %s after changing SSID value" %
                    (self.active_ad_ip_addr, self.ap_ip_addr)]

        # Verify connectivity between remote adapter and active AP
        try:
            verifyStaConnection(self.remote_win_sta, self.win_sta_ip_addr, self.video_ip_addr)
        except Exception, e:
            return ["FAIL", "Adapter %s does not associate to the active AP %s after changing SSID value" %
                    (self.passive_ad_ip_addr, self.ap_ip_addr)]

        return ["PASS", ""]

    def _changeEncryption(self, new_encryption, return_encryption):
        """
        This function uses to change encryption method for adapter or AP
        @param new_encryption: new encryption method should be changed to
        @param return_encryption: This is the bool value used to define logging messages
        """
        if not return_encryption:
            logging.info("Change encryption method for active adapter %s WebUI" % self.active_ad_ip_addr)
            msg = "auth ---> %s, encryption ---> %s, " % (new_encryption['auth'], new_encryption['encryption'])
            msg += "wpa_ver ---> %s, key_string ---> %s" % (new_encryption['wpa_ver'], new_encryption['key_string'])
            logging.info("New encryption information: %s" % msg)

            port = 25400 + getAID(self.active_ap, self.active_ad_ip_addr, self.active_ad_mac, self.check_status_timeout)
            url = "http://%s:%d" % (self.video_ip_addr, port)
            self.active_ad_webui_config['url'] = url
            if self.ad_model.lower() == "vf7111":
                self.remote_win_sta.set_ad_encryption_web_ui(self.active_ad_webui_config, new_encryption, True)
            else:
                self.remote_win_sta.set_ad_encryption_web_ui(self.active_ad_webui_config, new_encryption, False)
            time.sleep(5)

            logging.info("Verify that encryption method of the active adapter %s is changed successfully" %
                         self.active_ad_ip_addr)
            res = self.remote_linux_sta.get_ad_encryption(self.active_ad_config, 'wlan0')

            if res['auth'] != new_encryption['auth'] or res['encryption'] != new_encryption['encryption']:
                msg = "auth ---> %s, encryption ---> %s, " % (res['auth'], res['encryption'])
                logging.debug("Current encryption method: %s" % res)
                return ["FAIL", "The encryption method is not correct when changing it from WebUI"]
            logging.info("Change encryption method from adapter WebUI successfully")

        else:
            logging.info("Return the previous encryption configuration for the active adapter %s" %
                         self.active_ad_ip_addr)
            new_encryption['wlan_if'] = self.wlan_if
            self.remote_linux_sta.cfg_wlan(self.active_ad_config, new_encryption)

        if not return_encryption:
            msg = "Change encryption method for the active AP %s. " % self.ap_ip_addr
            msg += "So that it is the same as the one configured on the adapter %s" % self.active_ad_ip_addr
            logging.info(msg)
        else:
            logging.info("Return the previous encryption configuration for the AP %s" % self.ap_ip_addr)
        new_encryption['wlan_if'] = self.wlan_if
        self.active_ap.cfg_wlan(new_encryption)

        if not return_encryption:
            msg = "Change encryption method for the adapter %s. " % self.passive_ad_ip_addr
            msg += "So that it is the same as the one configured on the adapter %s" % self.active_ad_ip_addr
            logging.info(msg)
        else:
            logging.info("Return the previous encryption configuration for the AP %s" % self.passive_ad_ip_addr)
        self.remote_win_sta.cfg_wlan(self.passive_ad_conf, new_encryption)

        logging.info("Verify that after changing encryption method, adapters can associate to the AP %s successfully" %
                     self.ap_ip_addr)
        # Verify connectivity between active adapter and active AP
        try:
            verifyStaConnection(self.remote_linux_sta, self.linux_sta_ip_addr, self.ip_addr)
        except Exception, e:
            return ["FAIL", "Adapter %s does not associate to the active AP %s after changing encryption method" %
                    (self.active_ad_ip_addr, self.ap_ip_addr)]

        # Verify connectivity between remote adapter and active AP
        try:
            verifyStaConnection(self.remote_win_sta, self.win_sta_ip_addr, self.video_ip_addr)
        except Exception, e:
            return ["FAIL", "Adapter %s does not associate to the active AP %s after changing encryption method" %
                    (self.passive_ad_ip_addr, self.ap_ip_addr)]

        return ["PASS", ""]

    def _defineTestParams(self, conf):

        self.active_ad_config = {}
        self.passive_ad_conf = {}
        self.active_ap = None
        self.remote_win_sta = None
        self.remote_linux_sta = None

        if conf.has_key('change_ssid'):
            self.change_ssid = conf['change_ssid']

        self.check_status_timeout = 90
        self.url = ""
        self.browser_type = "ie"
        self.home_protection = ""
        self.ap_channel = '6'
        self.wlan_if = 'wlan0'
        self.verify_status = conf['verify_status']

    def _get_ip_addrs(self, conf):

        self.ip_addr = conf['ip']
        self.ap_ip_addr = self.testbed.getAPIpAddrBySymName(conf['active_ap'])
        self.active_ad_ip_addr = self.testbed.getAdIpAddrBySymName(conf['active_ad'])
        self.passive_ad_ip_addr = self.testbed.getAdIpAddrBySymName(conf['passive_ad'])

        # Find ip address of interface that connected to the adapter on the remote linux station
        self.linux_sta_ip_addr = getLinuxIpAddr(self.remote_linux_sta, self.testbed.sta_wifi_subnet)
        if not self.linux_sta_ip_addr:
            raise Exception("IP address of interface that connecting to the adapter is not correct")

        # Find ip address of interface that connected to the adapter on the remote windows station
        self.win_sta_ip_addr = getWinsIpAddr(self.remote_win_sta, self.testbed.sta_wifi_subnet)
        if not self.win_sta_ip_addr:
            raise Exception("IP address of interface that connecting to the adapter is not correct")

        # Get ip address of video interface
        self.video_ip_addr = ""
        self.profile = self.active_ap.get_profile()
        if self.profile.lower() == "ruckus05":
            ip_tmp = self.active_ap.get_bridge_if_cfg()
            for key, value in ip_tmp.iteritems():
                if key == "br2":
                    self.video_ip_addr = value['ip_addr']
                    break
        else:
            self.video_ip_addr = self.ap_ip_addr

    def _getStations(self, conf):
        # Find exactly stations
        station_list = self.testbed.components['Station']
        self.remote_win_sta = getStation(conf['remote_win_sta'], station_list)
        self.remote_linux_sta = getStation(conf['remote_linux_sta'], station_list)

    def _getADConfig(self, conf):
        # Get adapter configuration information
        self.active_ad_config = getADConfig(self.testbed, conf['active_ad'], self.testbed.ad_list)
        self.passive_ad_conf = getADConfig(self.testbed, conf['passive_ad'], self.testbed.ad_list, "Passive AD")

        # Get mac address of the active adapter
        self.ad_model = self.remote_linux_sta.get_ad_device_type(self.active_ad_config)
        self.active_ad_mac = self.remote_linux_sta.get_ad_wireless_mac(self.active_ad_config)
