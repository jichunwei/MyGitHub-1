# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: Firmware_Upgrade class tests ability of Upgrade/Downgrade function in the AP containing the manual and auto update.
    Author: Tam Nguyen
    Prerequisite (Assumptions about the state of the testbed/DeviceUnderTest):
    1. Build under test is loaded on the AP

    Required components: RuckusAP, StationLinuxPC
    Test parameters:        {'active_ap':'ip address of the tested AP',
                             'local_station':'ip address of local station',
                             'remote_station':'ip address of remote station',
                             'latest_build':'name of current build',
                             'up_from_build':'name of the build the AP will upgrade from',
                             'cli_command':'Bool value. Decide if testing cli upgrade command',
                             'up_cli':'Bool value. Decide if testing upgrade using cli command',
                             'up_webui':'Bool value. Decide if testing upgrade from webui',
                             'manual':'Bool value. Decide if testing upgrade from another stream using cli',
                             'auto_up':'Bool value. Decide if testing auto upgrade',
                             'auto_up_traffic':'Bool value. Decide if testing auto upgrade with traffic',
                             'corrupted_img':'Bool value. Decide if testing the ap with corrupted image',
                             'auto':'Bool value. Decide if testing auto upgrade from another stream'}

    Result type: PASS/FAIL/N/A

    Results: PASS: if all the above criteria are satisfied.
             FAIL: If one of the above criteria is not satisfied.

    Messages: If FAIL the test script returns a message related to the criterion that is not satisfied.

    Test procedure:
    1. Config:
        - Look for the active AP, active adapter and local station and remote station in the testbed.
        - Save the current Encryption information on the active AP
    2. Test:
        - Upgrade the AP to the build want to test.
        - Use manual or auto upgrade to test the upgrade function of the AP.
        - Verify by get image running.

    3. Cleanup:
        - Return the previous fw setting.
"""

import time
import logging
import tempfile
import os
import pdb

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.Ratutils import *
import libIPTV_TestConfig as tconfig
import libIPTV_TestMethods as tmethod

class Firmware_Upgrade(Test):
    required_components = ['RuckusAPSerial', 'StationLinuxPC']
    parameter_description = {'active_ap':'ip address of the tested AP',
                             'local_station':'ip address of local station',
                             'remote_station':'ip address of remote station',
                             'latest_build':'name of current build',
                             'up_from_build':'name of the build the AP will upgrade from',
                             'cli_command':'Bool value. Decide if testing cli upgrade command',
                             'up_cli':'Bool value. Decide if testing upgrade using cli command',
                             'up_webui':'Bool value. Decide if testing upgrade from webui',
                             'manual':'Bool value. Decide if testing upgrade from another stream using cli',
                             'auto_up':'Bool value. Decide if testing auto upgrade',
                             'auto_up_traffic':'Bool value. Decide if testing auto upgrade with traffic',
                             'corrupted_img':'Bool value. Decide if testing the ap with corrupted image',
                             'auto':'Bool value. Decide if testing auto upgrade from another stream'
    }

    def config(self, conf):
        self._defineTestParams(conf)
        self._getStations(conf)
        self.upgraded_build = self.local_station.create_copy_image(self.latest_build,name="fw%s" % int(time.time()))
        self._getActiveAP(conf)
        self._saveConfig()

        logging.info ("Disable auto upgrade in the AP")
        self.active_ap.change_fw_setting({'auto' : False})

    def test(self):
        # Verify upgrade command
        if self.cli_command: return self._cliCommand()

        # Upgrade through cli.
        if self.up_cli: return self._upCli()

        # Upgrade through WebUI.
        if self.up_webui: return self._upWebui()

        # Upgrade From older build
        if self.manual: return self._upManual()

        # Auto upgrade.
        if self.auto_up: return self._autoUp()

        # Auto upgrade with traffic.
        if self.auto_up_traffic: return self._autoUpTraffic()

        # Upgrade with corrupted image
        if self.corrupted_img: return self._corruptedImg()

        # Auto upgrade from older build.
        if self.auto: return self._upAuto()

    def cleanup(self):
        logging.info("Return the previous fw setting for AP")
        self.active_ap.change_fw_setting(self.old_fw_info)
        os.remove("%s/%s" % (self.ftpserv['rootpath'],self.upgraded_build))

        if self.auto_up_traffic:
            logging.info("Return the previous encryption for AP")
            self.active_ap.cfg_wlan(self.current_ap_encryption)

            logging.info("Down %s interface on the active AP" % self.wlan_if)
            self.active_ap.set_state(self.wlan_if, 'down')
            time.sleep(2)

            logging.info("Down svcp interface on the active Adapter")
            self.remote_station.set_ruckus_ad_state(self.active_ad_config, 'down', 'wlan0')
            logging.info("Kill iperf server process on the station ")
            self.remote_station.stop_iperf()
            self.local_station.stop_iperf()
        logging.info("------------ FINISH ---------------\n")

    def _cliCommand(self):

        msg = "[FW CLI Command]"

        ctrl_file = "fw"
        logging.info("%s: Configure control file" % msg)
        self.active_ap.change_fw_setting({'control' : ctrl_file})
        info = self.active_ap.get_fw_upgrade_setting()
        if info['control'] != ctrl_file:
            return ["FAIL", "%s: Could not configure control file option" % msg]
        logging.info("%s: Configure firmware control file for the AP successfully" % msg)

        logging.info("%s: Configure host information for the AP" % msg)
        self.active_ap.change_fw_setting({'host' : self.ftpserv['ip_addr']})
        info = self.active_ap.get_fw_upgrade_setting()
        if info['host'] != self.ftpserv['ip_addr']:
            return ["FAIL", "%s: Could not configure host for AP" % msg]
        logging.info("%s: Configure host for the AP to upgrade successfully" % msg)

        logging.info("%s: Configure protocol tftp for firmware settings" % msg)
        self.active_ap.change_fw_setting({'proto' : "tftp"})
        info = self.active_ap.get_fw_upgrade_setting()
        if info['proto'].lower() != 'tftp':
            return ["FAIL", "%s: Could not set protocol tftp for firmware upgrade" % msg]

        logging.info("%s: Set protocol ftp for firmware settings" % msg)
        self.active_ap.change_fw_setting({'proto' : "ftp", 'user':'abc', 'password':'abc'})
        info = self.active_ap.get_fw_upgrade_setting()
        if info['proto'].lower() != 'ftp':
            return ["FAIL", "%s: Could not set protocol ftp for firmware upgrade" % msg]
        logging.info("%s: Set protocol to download for the upgrade successfully" % msg)

        logging.info("%s: Enable auto upgrade" % msg)
        self.active_ap.change_fw_setting({'auto' : True})
        info = self.active_ap.get_fw_upgrade_setting()
        if info['auto_upgrade'] != "enabled":
            return ["FAIL", "%s: Could not enable the auto upgrade" % msg]
        logging.info("%s: Enable auto upgrade successfully" % msg)

        logging.info("%s: Configure firstcheck time after reboot" % msg)
        self.active_ap.change_fw_setting({'firstcheck' : "10"})
        info = self.active_ap.get_fw_upgrade_setting()
        if info['firstcheck'] != '10':
            return ["FAIL", "%s: Could not configure firstcheck for firmware upgrade" % msg]
        logging.info("%s: Configure firstcheck parameter for fw setting successfully" % msg)

        logging.info("%s: Configure interval time check for ap" % msg)
        self.active_ap.change_fw_setting({'interval' : "20"})
        info = self.active_ap.get_fw_upgrade_setting()
        if info['interval'] != '20':
            return ["FAIL", "%s: Could not set interval time for Upgrade" % msg]
        logging.info("%s: Set interval time for the upgrade successfully" % msg)

        logging.info("%s: Disable auto upgrade" % msg)
        self.active_ap.change_fw_setting({'auto' : False})
        info = self.active_ap.get_fw_upgrade_setting()
        if info['auto_upgrade'] != "disabled":
            return ["FAIL", "%s: Could not Disable the auto upgrade" % msg]
        logging.info("%s: Disable auto upgrade successfully" % msg)

        logging.info("Verify Upgrade command in CLI done.")
        return ["PASS", ""]

    def _upCli(self, same = False):

        msg = "[Manual Upgrade"
        if self.ap_model: msg = "%s - %s]" % (msg, self.ap_model)
        else: msg = "%s]" % msg

        logging.info("%s: Upgrade AP to the latest release [%s]" % (msg, self.latest_build))
        self._upgrade(self.latest_build)
        boarddata1 = self._getBoarddata()
        image1 = self.active_ap.get_fw_upgrade_setting()['running_image']
        logging.info(
            "%s: Upgrade AP from build [%s] to build [%s]" %
            (msg, self.latest_build, self.upgraded_build)
        )
        self._upgrade(self.upgraded_build)
        image2 = self.active_ap.get_fw_upgrade_setting()['running_image']
        boarddata2 = self._getBoarddata()
        logging.info("%s: Checking boarddata after upgrade" % msg)
        if boarddata1 != boarddata2:
            return ["FAIL", "%s: Boarddata change after upgrade" % msg]

        return self._checkRunningImage(image1, image2, same)

    def _upWebui(self):
        return ["N/A", "Temporary skip this test case"]

    def _upManual(self):

        if self.active_ap.get_model().lower() != self.ap_model.lower():
            return ["N/A","The AP model is not correct. Skip this test cases"]

        else:
            self.latest_build = self.up_from
            return self._upCli(same = False)

    def _autoUp(self):

        logging.info("Upgrade AP to the latest release [%s]" % self.latest_build)
        self._upgrade(self.latest_build)
        image1 = self.active_ap.get_fw_upgrade_setting()['running_image']

        logging.info("Enable auto upgrade in the AP, the AP will upgrade the new build")
        self.cntrl_file = self.active_ap.create_ctrl_file(self.ftpserv['rootpath'], self.upgraded_build)
        self.active_ap.change_fw_setting(self.fw_conf)
        self.active_ap.check_log_auto_up()
        image2 = self.active_ap.get_fw_upgrade_setting()['running_image']
        self._checkRunningImage(image1, image2)
        logging.info("The AP is successfully upgraded")

        logging.info("Change the control file server for ap to upgrade after first check")
        self.active_ap.change_fw_setting({'interval':self.interval, 'firstcheck':self.firstcheck})
        os.remove(self.cntrl_file)
        self.cntrl_file = self.active_ap.create_ctrl_file(self.ftpserv['rootpath'], self.latest_build)
        time.sleep(5)
        self.active_ap.check_log_auto_up()
        tmethod.verifyStaConnection(self.local_station, self.ftpserv['ip_addr'], self.active_ap.ip_addr)
        image3 = self.active_ap.get_fw_upgrade_setting()['running_image']
        self._checkRunningImage(image2, image3)
        logging.info("The AP is successfully upgraded after Firstcheck.")

        logging.info("Waiting for %s minutes for the ap to upgrade after interval time" % self.interval)
        time.sleep(int(self.interval)*60 -10)
        logging.info("Change the control file server for ap to upgrade after interval check")
        os.remove(self.cntrl_file)
        self.cntrl_file = self.active_ap.create_ctrl_file(self.ftpserv['rootpath'], self.upgraded_build)
        self.active_ap.check_log_auto_up()
        logging.info("The AP upgraded successfully after Interval check.")
        image4 = self.active_ap.get_fw_upgrade_setting()['running_image']
        self._checkRunningImage(image3, image4)
        os.remove(self.cntrl_file)
        return ["PASS", ""]

    def _autoUpTraffic(self):

        logging.info("Upgrade AP to the latest release [%s]" % self.latest_build)
        self._upgrade(self.latest_build)
        image1 = self.active_ap.get_fw_upgrade_setting()['running_image']

        wlan_cfg = dict(auth="open",
                        encryption="none",
                        ssid='IPTV',
                        wlan_if='%s' % self.wlan_if)
        logging.info("Configure a WLAN with SSID %s on the active AP" % wlan_cfg['ssid'])
        self.active_ap.cfg_wlan(wlan_cfg)
        self.active_ap.set_state(self.wlan_if, 'up')

        ad_wlan_cfg = wlan_cfg.copy()
        ad_wlan_cfg['wlan_if'] = 'wlan0'
        logging.info("Configure a WLAN with SSID %s  on the active adapter" % wlan_cfg['ssid'])
        self.remote_station.cfg_wlan(self.active_ad_config, ad_wlan_cfg)
        logging.info("Turn on svcp interface on this adapter")
        self.remote_station.set_ruckus_ad_state(self.active_ad_config, 'up', 'wlan0')

        tmethod.verifyStaConnection(self.local_station, self.local_sta_ip_addr, self.remote_sta_ip_addr)

        logging.info("Start iperf server on the station %s" % self.remote_sta_ip_addr)
        self.remote_station.start_iperf(test_udp = True)
        logging.info("Send traffic with bandwith 0.3m")
        self.local_station.start_iperf(serv_addr = self.remote_sta_ip_addr,
                                      test_udp = True,
                                      packet_len = '800',
                                      timeout = '1200',
                                      bw = '0.3m', tos = "")

        logging.info("Enable auto upgrade in the ap")
        self.cntrl_file = self.active_ap.create_ctrl_file(self.ftpserv['rootpath'], self.upgraded_build)
        self.active_ap.change_fw_setting(self.fw_conf)
        self.active_ap.check_log_auto_up()
        time.sleep(10)
        tmethod.verifyStaConnection(self.local_station, self.local_sta_ip_addr, self.remote_sta_ip_addr)
        image2 = self.active_ap.get_fw_upgrade_setting()['running_image']
        self._checkRunningImage(image1, image2)
        self.local_station.stop_iperf()

        self.local_station.start_iperf(serv_addr = self.remote_sta_ip_addr,
                                      test_udp = True,
                                      packet_len = '800',
                                      timeout = '1200',
                                      bw = '2m', tos = "")
        os.remove(self.cntrl_file)
        logging.info("Disable auto upgrade, change the control file")
        self.active_ap.change_fw_setting({'auto' : False})
        self.cntrl_file = self.active_ap.create_ctrl_file(self.ftpserv['rootpath'], self.latest_build)
        self.active_ap.change_fw_setting(self.fw_conf)
        logging.info("Enable auto upgrade, the Ap will download the new image immediately")
        self._checkLogTraffic()

        logging.info("Check if the AP reboot while have traffic online over 1M")
        self._checkReboot(False)
        image3 = self.active_ap.get_fw_upgrade_setting()['running_image']
        self._checkRunningImage(image2, image3, same = True)
        logging.info("The AP did not reboot to upgrade when the traffic is over 1M")

        logging.info("Stop Iperf, The AP will reboot and upgrade...")
        self.local_station.stop_iperf()
        self._checkReboot(True)
        tmethod.verifyStaConnection(self.local_station, self.ftpserv['ip_addr'], self.active_ap.ip_addr)
        image4 = self.active_ap.get_fw_upgrade_setting()['running_image']
        self._checkRunningImage(image3, image4)
        os.remove(self.cntrl_file)
        return ["PASS", ""]

    def _corruptedImg(self):

        logging.info("Upgrade AP to the latest release [%s]" % self.latest_build)
        self._upgrade(self.latest_build)
        image1 = self.active_ap.get_fw_upgrade_setting()['running_image']
        self.cntrl_file = self.active_ap.create_ctrl_file(self.ftpserv['rootpath'], self.upgraded_build)
        self.active_ap.change_fw_setting(self.fw_conf)

        self.active_ap.corrupt_image()
        logging.info("Force the ap to load the corrupted image")
        self.active_ap.tty.write("reboot now \n")

        self.active_ap.goto_red_boot()
        bootid = 1
        current_bootid = self.active_ap.get_main_image_id()
        if current_bootid == 1:
            bootid = 2
        self.active_ap.set_main_image_id(bootid)
        logging.info("Count the number of retries to load the corrupted image")
        count = self.active_ap.check_reboot_times()

        logging.info("The AP try %s times to recover the image" % count)
        MAX_RETRIES = 5
        if count < MAX_RETRIES:
            return ["FAIL", "The ap try to recover %s times, not %s times" % (count, MAX_RETRIES)]
        logging.info("Waiting for the AP to come up...")
        tmethod.verifyStaConnection(self.local_station, self.ftpserv['ip_addr'], self.active_ap.ip_addr)
        image2 = self.active_ap.get_fw_upgrade_setting()['running_image']
        self._checkRunningImage(image1, image2, same = True)

        logging.info("The AP is trying to recover the corrupted Image...")
        self.active_ap.check_log_auto_up()
        time.sleep(10)
        tmethod.verifyStaConnection(self.local_station, self.ftpserv['ip_addr'], self.active_ap.ip_addr)
        image3 = self.active_ap.get_fw_upgrade_setting()['running_image']
        self._checkRunningImage(image2, image3)

        return ["PASS", ""]

    def _upAuto(self):

        msg = "Auto Upgrade - %s]" % self.ap_model
        if self.active_ap.get_model().lower() != self.ap_model.lower():
            return ["N/A","The AP model is not correct. Skip this test cases"]

        self.latest_build = self.up_from
        logging.info("%s: Disable auto upgrade in the AP" % msg)
        self.active_ap.change_fw_setting({'auto' : False})
        logging.info("%s: Upgrade AP to the latest release [%s]" % (msg, self.latest_build))
        self._upgrade(self.latest_build)
        image1 = self.active_ap.get_fw_upgrade_setting()['running_image']

        logging.info("%s: Enable auto upgrade in the AP, the AP will upgrade the new build" % msg)
        self.cntrl_file = self.active_ap.create_ctrl_file(self.ftpserv['rootpath'], self.upgraded_build)
        self.active_ap.change_fw_setting(self.fw_conf)
        self.active_ap.check_log_auto_up()
        image2 = self.active_ap.get_fw_upgrade_setting()['running_image']
        self._checkRunningImage(image1, image2)
        os.remove(self.cntrl_file)
        return ["PASS", ""]

    def _upgrade(self, build):
        # Create control file
        cntrl_file = self.active_ap.create_ctrl_file(self.ftpserv['rootpath'], build)

        # Config fw setting for AP and upgrade
        self.fw_conf['control'] = cntrl_file
        self.fw_conf['auto']=False
        self.active_ap.change_fw_setting(self.fw_conf)
        self.active_ap.upgrade_sw()
        time.sleep(3)

        # Remove control file
        os.remove(cntrl_file)
        self.fw_conf['auto'] = True

    def _getActiveAP(self, conf):
        logging.info("Find the active AP object")

        self.active_ap = tconfig.getTestbedActiveAP(self.testbed, conf['active_ap'],
                                                    self.testbed.components['AP'], "", "")

    def _getBoarddata(self):
        data = {}
        data['Model'] = self.active_ap.get_model()
        data['Mac'] = self.active_ap.get_base_mac()
        data['profile'] = self.active_ap.get_profile()
        data['FixedCountryCode'] = self.active_ap.get_fixed_country_code()
        return data

    def _saveConfig(self):
        logging.info("Save AP firmware setting")
        self.old_fw_info = self.active_ap.get_fw_upgrade_setting()
        if self.auto_up_traffic:
            logging.info("Save encryption information")
            self.current_ap_encryption = self.active_ap.get_encryption(self.wlan_if)
            self.current_ap_encryption['wlan_if'] = self.wlan_if
            self.current_active_ad_encryption = self.remote_station.get_ad_encryption(self.active_ad_config, 'wlan0')
            self.current_active_ad_encryption['wlan_if'] = 'wlan0'

    def _getStations(self, conf):
        # Find exactly stations
        station_list = self.testbed.components['Station']
        self.local_station = tconfig.getStation(conf['local_station'], station_list)
        if self.auto_up_traffic:
            self.active_ad_config = tconfig.getADConfig(self.testbed,
                                                        conf['active_ad'],
                                                        self.testbed.ad_list)
            self.remote_station = tconfig.getStation(conf['remote_station'], station_list)
            self.remote_sta_ip_addr = tconfig.getLinuxIpAddr(self.remote_station, self.testbed.sta_wifi_subnet)
            self.local_sta_ip_addr = tconfig.getLinuxIpAddr(self.local_station, self.testbed.sta_wifi_subnet)

    def _checkRunningImage (self, image1, image2, same = False):
        if not same:
            if image1 == image2:
                return ["FAIL", "The AP could not perform the upgrade"]
        else:
            if image1 != image2:
                return ["FAIL", "The AP performs the upgrade while it should not"]

        return ['PASS', '']

    def _checkLogTraffic(self, timeout = 300):
        logging.info("Check if AP will automatically download the images")

        # loop until AP write firmware success or timeout
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise Exception("Upgrade failed after %s seconds" % timeout)
            ix, rx = self.active_ap.expect(['\*\*\*(.*)\*\*\*'], 10)
            if ix != -1:
                break
            time.sleep(1)

        rl = rx.split('\n')
        rl = [x.rstrip('\r') for x in rl]

        fw_txt = ''
        for res in rl:
            if res.lower().find("reboot") != -1:
                fw_txt = res
                break
        logging.info("The AP successfully download the image")

    def _checkReboot(self, expect_reboot=False):
        start_time = time.time()
        while time.time() - start_time < 90:
            ix, rx = self.active_ap.expect(['System Shutdown'], 5)
            if ix != -1:
                if expect_reboot:
                    return ['FAIL', "The AP did not reboot after the upgrade while traffic is under 1m"]
            else:
                if not expect_reboot:
                    return ['FAIL', "The AP reboot while the traffic is over 1m"]

    def _defineTestParams(self, conf):

        if conf.has_key('ap_model'): self.ap_model = conf['ap_model']
        else: self.ap_model = ""

        self.latest_build = conf['latest_build']
        self.ftpserv = self.testbed.ftpserv

        self.firstcheck = '1'
        self.interval = '2'
        self.cntrl_file = ""
        self.fw_conf = {'host':self.ftpserv['ip_addr'],
                        'control':self.cntrl_file,
                        'proto':"ftp",
                        'user':self.ftpserv['username'],
                        'password':self.ftpserv['password'],
                        'auto':True}

        if conf.has_key('cli_command'):
            self.cli_command = conf['cli_command']
        else: self.cli_command= False

        if conf.has_key('up_cli'):
            self.up_cli = conf['up_cli']
        else: self.up_cli = False

        if conf.has_key('up_webui'):
            self.up_webui = conf['up_webui']
        else: self.up_webui = False

        if conf.has_key('manual'):
            self.manual = conf['manual']
            self.up_from = conf['up_from_build']
        else: self.manual = False

        if conf.has_key('auto_up'):
            self.auto_up = conf['auto_up']
        else: self.auto_up = False

        if conf.has_key('auto_up_traffic'):
            self.auto_up_traffic = conf['auto_up_traffic']
            self.wlan_if = 'wlan8'
        else: self.auto_up_traffic = False

        if conf.has_key('corrupted_img'):
            self.corrupted_img = conf['corrupted_img']
        else: self.corrupted_img = False

        if conf.has_key('auto'):
            self.auto = conf['auto']
            self.up_from = conf['up_from_build']
        else: self.auto = False
