# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: AD_MGMT_LoginWebUI class tests the login ability to adapter WebUI from the AP WebUI.
    Author: Tam Nguyen
    Prerequisite (Assumptions about the state of the testbed/DeviceUnderTest):

    1. Build under test is loaded on the AP
    Required components: RuckusAP, StationLinuxPC, StationWinPC
    Test parameters: {'active_ap': 'ip address of the tested AP',
                      'active_ad': 'ip address of the tested adapter',
                      'ip': 'ip address to ping. This is the ip address of station behind the AP',
                      'remote_win_sta': 'ip address of Windows PC',
                      'remote_linux_sta': 'ip address of remote station behind the active adapter',
                      'video_network': 'This is the bool value used to determine if remote_win_sta joins to
                                        video network or data network',
                       'super_user': 'This is the bool value used to determine if station login to AP WebUI by super user
                                     or home user',
                       'ad_sta_mgmt_enable': 'This is the bool value used to determine if STA-Management is enable on the
                                              adapter or not'}

    Result type: PASS/FAIL
    Results: PASS: Verify that station can only login to adapter WebUI from AP WebUI when it is in Video network and
                   using super user to login. Otherwise it can not.
             FAIL: If one of the above criteria is not safisfied.

    Messages: If FAIL the test script returns a message related to the criterion that is not satisfied.

    Test procedure:
    1. Config:
        - Look for the active AP, active adapter and target station and remote station in the testbed.
        - Save the current link-local management configuration on the active AP and active adapter
    2. Test:
        - Turn off all wlans on non-active APs
        - Enable link-local management on the active Ap and active adapter
        - If 'video_network' is True:
            + Turn on svcp interface on the active AP and the active adapter
            + Login to AP WebUI by super user. If 'ad_sta_mgmt_enable' is True, verify that from here station can
            login to adapter WebUI. Otherwise, it can not see any information about Sta-WebServer on the AP WebUI.
            So that it can not login to the adapter WebUI.
            + Login to AP WebUI by home user. Verify that from here station does not see any information related to
            Sta-Management. So that it can not login to the adapter WebUI
        - If 'video_network' is False:
            + Create a wlan for Data network with given parameters
            + Configure wlan profile on target station, so that it can associate to the Data network
            + Turn on home interface on the active AP, and svcp interface on the active adapter
            + Login to AP WebUI by super user. Verify that station can not login to the adapter WebUI from AP WebUI
            Although it can see the STA-WebServer link from here
            + Login to AP WebUI by home user. Verify that station can not see any information about Video network
            as well as any information about STA-WebServer on the AP WebUI.
    3. Cleanup:
        - Return the previous configuration of link-local management on the AP and AD
        - Down svcp interface on the active adapter
        - Down all wlan interfaces on the active AP
"""

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.Ratutils import *
from libIPTV_TestConfig import *
from libIPTV_TestMethods import *

class AD_MGMT_LoginWebUI(Test):
    required_components = ['RuckusAP', 'StationLinuxPC', 'StationWinPC']
    parameter_description = {'active_ap': 'ip address of the tested AP',
                             'active_ad': 'ip address of the tested adapter',
                             'passive_ad': 'ip address the adapter in front of Windows station',
                             'ip': 'ip address to ping. This is the ip address of station behind the AP',
                             'remote_win_sta': 'ip address of Windows PC',
                             'remote_linux_sta': 'ip address of remote station behind the active adapter',
                             'video_network': 'This is the bool value used to determine if remote_win_sta joins to \
                                              video network or data network',
                             'super_user': 'This is the bool value used to determine if station login to AP WebUI by \
                                            super user or home user',
                            'ad_sta_mgmt_enable': 'This is the bool value used to determine if STA-Management is \
                                                    enabled on the adapter or not'}

    def config(self, conf):
        self.active_ad_config = {}
        self.passive_ad_conf = {}
        self.active_ap = None
        self.remote_win_sta = None
        self.remote_linux_sta = None

        self.video_network = conf['video_network']
        self.super_user = conf['super_user']
        self.ap_ip_addr = self.testbed.getAPIpAddrBySymName(conf['active_ap'])
        self.active_ad_ip_addr = self.testbed.getAdIpAddrBySymName(conf['active_ad'])
        self.passive_ad_ip_addr = self.testbed.getAdIpAddrBySymName(conf['passive_ad'])
        self.ip_addr = conf['ip']
        self.ap_channel = '6'
        self.wlan_if = 'wlan0'

        if conf.has_key('ad_sta_mgmt_enable'):
            self.ad_sta_mgmt_enable = conf['ad_sta_mgmt_enable']
        else:
            self.ad_sta_mgmt_enable = True

        if conf.has_key('home_username'): self.home_username = conf['home_username']
        else: self.home_username = ""
        if conf.has_key('home_password'): self.home_password = conf['home_password']
        else: self.home_password = ""


        self.ping_timeout = 120
        self.check_status_timeout = 90

        logging.info("Find the active AP object")
        self.active_ap = getTestbedActiveAP(self.testbed, conf['active_ap'], self.testbed.components['AP'],
                                            self.ap_channel, 'wlan0')

        # Information to login
        self.super_username = self.active_ap.get_username()
        self.super_password = self.active_ap.get_password()

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

        # Find exactly stations
        station_list = self.testbed.components['Station']
        self.remote_win_sta = getStation(conf['remote_win_sta'], station_list)
        self.remote_linux_sta = getStation(conf['remote_linux_sta'], station_list)

        # Find ip address of interface that connected to the adapter on the remote linux station
        self.linux_sta_ip_addr = getLinuxIpAddr(self.remote_linux_sta, self.testbed.sta_wifi_subnet)
        if not self.linux_sta_ip_addr:
            raise Exception("IP address of interface that connecting to the adapter is not correct")

        # Find ip address of interface that connected to the adapter on the remote windows station
        self.win_sta_ip_addr = getWinsIpAddr(self.remote_win_sta, self.testbed.sta_wifi_subnet)
        if not self.win_sta_ip_addr:
            raise Exception("IP address of interface that connecting to the adapter is not correct")

        # Get adapter configuration information
        self.active_ad_config = getADConfig(self.testbed, conf['active_ad'], self.testbed.ad_list)
        self.passive_ad_conf = getADConfig(self.testbed, conf['passive_ad'], self.testbed.ad_list, "Passive AD")

        logging.info("Save the current link-local management configuration on the active AP and active AD")
        self.cur_ap_sta_mgmt = self.active_ap.get_sta_mgmt('wlan0')
        self.cur_ad_sta_mgmt = self.remote_linux_sta.get_ad_sta_mgmt(self.active_ad_config, 'wlan0')

        if not self.video_network:
            logging.info("Save wlan configuration on the adapter %s" % self.passive_ad_ip_addr)
            self.cur_ad_wlan_cfg = self.remote_win_sta.get_ad_encryption(self.passive_ad_conf, 'wlan0')

            self.new_wlan_cfg = {'ssid':'IPTV_DATA', 'auth':'PSK',
                                 'wpa_ver':'WPA', 'encryption':'TKIP', 'key_string':'1234567890'}

        # Get mac address of the active adapter
        self.active_ad_mac = self.remote_linux_sta.get_ad_wireless_mac(self.active_ad_config)

    def test(self):

        # Get customer profile on the active AP to verify that if it has Data network or not
        if not self.video_network:
            if self.profile.lower() == "ruckus":
                self.active_ap = None
                self.remote_linux_sta = None
                self.remote_win_sta = None
                self.active_ad_config = {}
                self.passive_ad_conf = {}
                return ["N/A", "AP %s does not have Data network because its profile is ruckus" % self.ap_ip_addr]

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

        logging.info("Turn on the svcp interface on the active adapter %s" % self.active_ad_ip_addr)
        self.remote_linux_sta.set_ruckus_ad_state(self.active_ad_config, 'up', 'wlan0')

        # Check connectivity
        verifyStaConnection(self.remote_linux_sta, self.linux_sta_ip_addr, self.ip_addr)

        # If Windows station associates to the Video network, add one IP address that has the same subnet as
        # AP Video network to this station
        if self.video_network:
            self.remote_win_sta.cfg_wlan(self.passive_ad_conf, ad_wlan_cfg)
            logging.info("Turn on svcp interface on the adapter %s" % self.passive_ad_ip_addr)
            self.remote_win_sta.set_ruckus_ad_state(self.passive_ad_conf, 'up', 'wlan0')
            self._addIp(self.video_ip_addr)

        # Otherwise, create a wlan for Data network on AP, and Windows station will associate to this wlan.
        # Then add one IP address that has the same subnet as AP Data network to this station
        else:
            logging.info("Configure a WLAN with SSID %s on the Data network of the active AP" %
                         self.new_wlan_cfg['ssid'])
            self.new_wlan_cfg['wlan_if'] = 'wlan1'
            self.active_ap.cfg_wlan(self.new_wlan_cfg)

            logging.info("Turn on home interface on the active AP")
            self.active_ap.set_state('wlan1', 'up')

            logging.info("Configure a WLAN with SSID %s on the adapter %s" %
                         (self.new_wlan_cfg['ssid'], self.passive_ad_ip_addr))
            self.new_wlan_cfg['wlan_if'] = 'wlan0'
            self.remote_win_sta.cfg_wlan(self.passive_ad_conf, self.new_wlan_cfg)

            logging.info("Turn on svcp interface on the adapter %s" % self.passive_ad_ip_addr)
            self.remote_win_sta.set_ruckus_ad_state(self.passive_ad_conf, 'up', 'wlan0')

            # Get information of interface configuration on the active AP
            ap_home_inf_ip_addr = ""
            res = self.active_ap.get_bridge_if_cfg()
            if self.profile != 'ruckus03':
                for key, value in res.iteritems():
                    if key == "br1":
                        ap_home_inf_ip_addr = value['ip_addr']
                        self._addIp(ap_home_inf_ip_addr)
                        break
            else:
                for key, value in res.iteritems():
                    if key == 'br0':
                        ap_home_inf_ip_addr = value['ip_addr']
                        self._addIp(ap_home_inf_ip_addr)
                        time.sleep(2)
                        # Check connectivity
                        verifyStaConnection(self.remote_win_sta, self.win_sta_ip_addr, ap_home_inf_ip_addr)
                        break
            if not ap_home_inf_ip_addr:
                logging.debug("Interface info on the active AP ---------------> %s" % res)
                raise Exception("Can not find IP address of Home interface on the active AP %s" % self.ap_ip_addr)

        logging.info("Enable link-local management on the active AP %s" % self.ap_ip_addr)
        self.active_ap.set_sta_mgmt('wlan0', True)

        # Enable sta-mgmt feature on the adapter
        if self.ad_sta_mgmt_enable:
            logging.info("Enable link-local management on the active adapter %s" % self.active_ad_ip_addr)
            self.remote_linux_sta.set_ad_sta_mgmt(self.active_ad_config, 'wlan0', True)
            time.sleep(2)

            logging.info("Verify that STA-Management on the AP and adapter is enabled and is in active state")
            res, msg = verifyStaMGMT(self.active_ap, None, self.check_status_timeout)
            if res == "FAIL":
                return [res, msg]

            res, msg = verifyStaMGMT(None, self.remote_linux_sta, self.check_status_timeout, self.active_ad_config)
            if res == "FAIL":
                return [res, msg]
            logging.info("STA-Management is enabled and in active state on the AP and adapter")

        # Disable sta-mgmt feature on adapter
        else:
            logging.info("Disable STA-Management on the active adapter %s" % self.active_ad_ip_addr)
            self.remote_linux_sta.set_ad_sta_mgmt(self.active_ad_config, 'wlan0', False)
            time.sleep(3)

            logging.info("Verify that STA-Management on the active adapter is disabled")
            ad_sta_mgmt = self.remote_linux_sta.get_ad_sta_mgmt(self.active_ad_config, 'wlan0')
            if ad_sta_mgmt['enable']:
                return ["FAIL", "The adapter STA-Management is still enabled while it is turned off"]
            logging.info("The sta-mgmt feature is disabled on the adapter")

        # Get information of the active adapter on the AP
        ad_aid = str(getAID(self.active_ap, self.active_ad_ip_addr, self.active_ad_mac, self.check_status_timeout))

        # Test Login to AP WebUI
        if self.video_network:
            if not self.super_user:
                res = self._loginWithHomeUser(self.video_ip_addr)
                if res[0] == "FAIL":
                    return res
            else:
                res = self._loginWithSuperUser(self.video_ip_addr, ad_aid)
                if res[0] == "FAIL":
                    self.remote_win_sta.logout_ap_web_ui(self.video_ip_addr)
                    return res
                self.remote_win_sta.logout_ap_web_ui(self.video_ip_addr)
        else:
            if not self.super_user:
                res = self._loginWithHomeUser(ap_home_inf_ip_addr)
                if res[0] == "FAIL":
                    return res
            else:
                res = self._loginWithSuperUser(ap_home_inf_ip_addr, ad_aid)
                if res[0] == "FAIL":
                    self.remote_win_sta.logout_ap_web_ui(ap_home_inf_ip_addr)
                    return res
                self.remote_win_sta.logout_ap_web_ui(ap_home_inf_ip_addr)

        # Login Adapter WebUI
        if self.super_user and self.ad_sta_mgmt_enable:
            logging.info("Try to login to adapter WebUI from AP WebUI")
            if self.video_network:
                try:
                    self.remote_win_sta.login_ad_web_ui(self.video_ip_addr, ad_aid)
                    logging.info("Login to adapter WebUI successfully")
                except Exception, e:
                    if "Connection refused" in str(e.message):
                        return ["FAIL", "Can not login to adapter WebUI from AP WebUI by Super user"]
                    else:
                        raise Exception(e.message)
            else:
                login_false = True
                try:
                    self.remote_win_sta.login_ad_web_ui(ap_home_inf_ip_addr, ad_aid)
                    login_false = False
                except Exception, e:
                    if "Connection refused" in str(e.message):
                        logging.info("Can not login to adapter WebUI from AP WebUI in Home network")
                    else:
                        raise Exception(e.message)
                if not login_false:
                    return ["FAIL", "Station can login to adapter WebUI while it is in Home network"]

        return ["PASS", ""]

    def cleanup(self):
        if self.remote_win_sta:
            logging.info("Remove  the added ip address out of the interface that connecting to adapter %s" %
                         self.passive_ad_ip_addr)
            self.remote_win_sta.verify_if(self.win_sta_ip_addr)

            if self.passive_ad_conf:
                if not self.video_network:
                    logging.info("Return the previous wlan configuration with SSID %s for adapter %s" %
                                 (self.cur_ad_wlan_cfg['ssid'], self.passive_ad_ip_addr))
                    self.cur_ad_wlan_cfg['wlan_if'] = 'wlan0'
                    self.remote_win_sta.cfg_wlan(self.passive_ad_conf, self.cur_ad_wlan_cfg)
                    time.sleep(3)

                    msg = "Verify that after returning the previous wlan configuration, "
                    msg += "station %s can connect to the AP" % self.win_sta_ip_addr
                    logging.info(msg)
                    verifyStaConnection(self.remote_win_sta, self.win_sta_ip_addr, self.ip_addr)

                logging.info("Turn off svcp interface on the adapter %s" % self.passive_ad_ip_addr)
                self.remote_win_sta.set_ruckus_ad_state(self.passive_ad_conf, 'down', 'wlan0')

        if self.active_ap:
            logging.info("Return the previous sta-mgmt status of AP %s" % self.ap_ip_addr)
            self.active_ap.set_sta_mgmt('wlan0', self.cur_ap_sta_mgmt['enable'])

            logging.info("Turn off svcp interface on the active AP %s" % self.ap_ip_addr)
            self.active_ap.set_state('wlan0', 'down')

            if not self.video_network:
                logging.info("Turn off home interface on the active AP %s" % self.ap_ip_addr)
                self.active_ap.set_state('wlan1', 'down')

        if self.active_ad_config:
            logging.info("Turn off the svcp interface on the active adapter %s" % self.active_ad_ip_addr)
            self.remote_linux_sta.set_ruckus_ad_state(self.active_ad_config, 'down', 'wlan0')

            logging.info("Return the previous sta-mgmt on the active adapter %s" % self.active_ad_ip_addr)
            self.remote_linux_sta.set_ad_sta_mgmt(self.active_ad_config, 'wlan0', self.cur_ad_sta_mgmt['enable'])

        logging.info("--------------- FINISH ---------------")

    def _addIp(self, ap_ip):
        """
        This function adds one more ip address to the specific interface on the windows station
        """
        subnet_tmp = get_network_address(ap_ip)
        win_ip_tmp = ".".join(subnet_tmp.split('.')[:-1]) + "." + self.win_sta_ip_addr.split('.')[-1]
        mask_tmp = get_subnet_mask(ap_ip, False)

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
        verifyStaConnection(self.remote_win_sta, self.win_sta_ip_addr, ap_ip)

    def _loginWithHomeUser(self, ap_ip_addr):
        """
        Perform login to adapter WebUI from AP WebUI by using Home user
        """
        logging.info("Login to WebUI of the active AP %s by Home user from station %s" %
                     (self.ap_ip_addr, self.win_sta_ip_addr))
        self.remote_win_sta.login_ap_web_ui(self.home_username, self.home_password, ap_ip_addr)
        time.sleep(3)

        logging.info("Get wireless status from the AP WebUI")
        res = self.remote_win_sta.get_ap_wireless_status(ap_ip_addr)
        time.sleep(3)
        if res['video_status']:
            self.remote_win_sta.logout_ap_web_ui(ap_ip_addr)
            return ["FAIL", "Video network appears on the AP WebUI while station %s login to it by Home user" %
                    self.win_sta_ip_addr]

        self.remote_win_sta.logout_ap_web_ui(ap_ip_addr)
        logging.info("Video network completely disappear from the AP WebUI when login to it by Home User")
        return ["PASS", ""]

    def _loginWithSuperUser(self, ap_ip_addr, ad_aid):
        """
        Perform login to adapter WebUI from the AP WebUI by using Super user
        """
        logging.info("Login to WebUI of the active AP %s by Super user from station %s" %
                     (self.ap_ip_addr, self.win_sta_ip_addr))
        self.remote_win_sta.login_ap_web_ui(self.super_username, self.super_password, ap_ip_addr)
        time.sleep(3)

        logging.info("Get wireless status from the AP WebUI")
        res = self.remote_win_sta.get_ap_wireless_status(ap_ip_addr)
        time.sleep(3)
        if not res['video_status']:
            return ["FAIL", "Can not find information of Video network on the AP WebUI while login to it by Super user"]
        if not res['data_status']:
            if self.profile != "ruckus":
                msg = "Can not find information of Data network on the AP WebUI "
                msg += "while login to it by Super user"
                return ["FAIL", msg]
        if self.profile == "ruckus":
            logging.info("Video network is shown on the AP WebUI")
        else:
            logging.info("Video and Data networks are shown on the AP WebUI")

        logging.info("Information of the active adapter shown on the AP: mac addr -----> %s, aid -----> %s" %
                     (self.active_ad_mac, ad_aid))
        logging.info("Verify information of STA-Management from WebUI of the active AP %s" % self.ap_ip_addr)
        res = self.remote_win_sta.verify_station_mgmt(ap_ip_addr, ad_aid, self.active_ad_mac)
        time.sleep(3)
        if not res['sta_existed']:
            return ["FAIL", "Can not find adapter's mac address from the AP WebUI"]
        if not res['sta_mgmt_enable']:
            # If adapter disables sta-mgmt feature
            if self.ad_sta_mgmt_enable:
                msg = "Can not find any information about STA-WebServer (Adapter Management) from the AP WebUI"
                msg += " while login to it by super user"
                return ["FAIL", msg]
            else:
                msg = "Information about STA-WebServer (Adapter Management) does not show on the AP WebUI"
                msg += " because of disabling this feature on the active adapter"
                logging.info(msg)

        return ["PASS", ""]

