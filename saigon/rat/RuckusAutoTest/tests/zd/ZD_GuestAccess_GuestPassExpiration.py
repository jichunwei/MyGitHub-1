# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: ZD_GuestPass Expiration Test class tests the usage of guest pass when it's expired.
The guest pass will expire in amount of specified time after it's first used or after it's issued

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and ZD

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: 'target_station_ip': 'ip address of target station',
                    'is_pass_expired_after_used': 'This is the bool value used to decide guest pass will be expired
                                                   even if it is first use or not. If it is False, the guest pass will
                                                   be expired even if it's not used. Otherwise, the guest pass will be
                                                   expired after it's first used'

   Result type: PASS/FAIL/ERROR
   Results: PASS: If 'is_pass_expired_after_used' is True, the guest pass must be used to authenticate client successfully
                   first. The client is in the 'Authorized' status. After the valid time of this guest pass is over, the client still
                   associates to the wlan, but its status now is "Unauthorized"
                   If 'is_pass_expired_after_used' is False, the client using the expired guest pass to authenticate can associate to the
                   wireless network, but its status is always "Unauthorized".
            FAIL: if one of the above criteria is not satisfied
            ERROR: if some unexpected events happen

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Remove all WLAN configuration on the target station
       - Remove all configurations about WLANs, users, authentication servers, and active clients on the ZD
       - Remove all guest passes if existed
   2. Test:
       - Configure a WLAN on the ZD with open security setting
       - Configure Guest Access policy and configure a user which will be used to generate guest pass
       - Open another browser, browse to the Guest Pass Generation page and generate a guest pass
       - If 'is_pass_expired_after_used' is True:
           + Configure the target station with given security setting
           + Wait until it gets associated and get IP and MAC addresses of the wireless adapter
           + Do Guest authentication from the station
           + Verify if the ZD shows correct information about the connected station, and the station's status now is
           "Authorized"
       - Increase PC time so that it is later than the valid time of guest pass. Perform synchronizing between ZD
        system time and PC time. The guest pass is expired now.
       - If 'is_pass_expired_after_used' is True, verify that the station still asscociates to the wireless network,
       but its status now is "Unauthorized"
       - If 'is_pass_expired_after_used' is False:
           + Configure the target station with given security setting
           + Wait until it gets associated and get IP and MAC addresses of the wireless adapter
           + Do Guest authentication from the station
           + Verify the station's status now is "Unauthorized"
   3. Cleanup:
       - Remove all wlan configuration and generated guest passes on ZD
       - Remove wireless profile on remote wireless STA
       - Verify if wireless station is completely disconnected after removing the wireless profile

   How it is tested?
       - While the test is running, right after the guest pass is generated, change PC time so that it's sooner than
       the valid time of guest pass. Synchronize it with ZD system time. The test script should report FAIL because
       the guest pass is not expired and station's status shown on the ZD is "Authorized"
"""

import os
import logging
import time
import datetime

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd.ZD_GuestAccess_Common import ZD_GuestAccess_Common


class ZD_GuestAccess_GuestPassExpiration(ZD_GuestAccess_Common):
    required_components = ['Station', 'ZoneDirector']
    parameter_description = {'is_pass_expired_after_used': 'This is the bool value used to decide guest pass will be expired \
                                                            even if it is used or not',
                             'target_station_ip': 'ip address of target station'}

    def config(self, conf):
        # the super method should be called first
        ZD_GuestAccess_Common.config(self, conf)

        self.tc2f = {
            'guestpass-expiration': self._testGuestPassExpiration, # TCs 3.1.16, 17
        }

        self._cfgBackupConfigOnZD()

        self._cfgRemoveAllWlanProfilesOnStation()


    def test(self):
        return ZD_GuestAccess_Common.test(self)


    def cleanup(self):
        # removes all config on the ZD.
        # refers to the docstring in config() for detail.
        ZD_GuestAccess_Common.cleanup(self)

        self._cfgRestoreSavedConfig()

    def _cfgInitTestParams(self, conf = None):
        # the super method should be called first to initialize common variables
        ZD_GuestAccess_Common._cfgInitTestParams(self, conf)

        # additional params should be put below
        if conf is None:
            conf = self._getDefaultConfig()
            self.conf = conf
        else:
            self.conf.update(conf)

        self.wlan_cfg = self._getDefaultWlanConfig()
        self.wlan_cfg.update(conf['wlan_cfg'])

        self.sta_wifi_mac_addr = None
        self.sta_wifi_ip_addr = None


    def _getDefaultConfig(self):
        conf = {'testcase': '',
                'use_tou': False,
                'wlan_cfg': {},
                'username': 'guesttest',
                'password': 'guesttest',
                'valid_time': 5,
                'expired_duration': 2,
                'redirect_url': '',
                'is_pass_expired_after_used': True,
                'check_status_timeout': 150,
                'target_station_ip': '192.168.1.11',
                }
        return conf


    def _getDefaultWlanConfig(self):
        # Modified by Serena Tan. 2010.11.22
        # To fix bug 16514.
        ssid = "wlan-guestpass-%s" % time.strftime("%H%M%S")
        wlan_cfg = {
#                    'ssid': 'wlan-guestpass',
                    'ssid': ssid,
                    'type': 'guest',
                    'username': '',
                    'sta_auth': 'open',
                    'ras_port': '',
                    'key_index': '',
                    'auth': 'open',
                    'sta_encryption': 'none',
                    'ras_addr': '',
                    'password': '',
                    'use_guest_access': True,
                    'ad_domain': '',
                    'ad_port': '',
                    'key_string': '',
                    'sta_wpa_ver': '',
                    'encryption': 'none',
                    'ad_addr': '',
                    'wpa_ver': '',
                    'ras_secret': ''
                    }
        return wlan_cfg


    # overriding method. should not invoke the super method.
    def _cfgRemoveAllConfigOnZD(self):
        #logging.info("Remove all Guest Passes on the ZD")
        #lib.zd.ga.delete_all_guestpass(self.zd)

        #logging.info("Remove all configurations on the ZD")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)


    def _cfgCreateWlanOnZD(self):
        logging.info("Create WLAN [%s] as a Guest Access WLAN on the ZD" % self.wlan_cfg['ssid'])
        lib.zd.wlan.create_wlan(self.zd, self.wlan_cfg)
        tmethod8.pause_test_for(3, "Wait for the ZD to push new configuration to the APs")


    def _cfgAuthServerOnZD(self):
        self._cfgCreateUser()


    def _cfgBackupConfigOnZD(self):
        logging.info("Save the current configurations of guest access and guest pass")
        self.old_guestaccess_policy = self.zd.get_guestaccess_policy()
        self.old_guestpass_policy = self.zd.get_guestpass_policy()


    def _cfgRestoreSavedConfig(self):
        logging.info("Return the old policies about guest access and guest pass for the ZD")
        self.zd.set_guestaccess_policy(**self.old_guestaccess_policy)
        self.zd.set_guestpass_policy(**self.old_guestpass_policy)


    def _cfgConfigPolicy(self):
        logging.info("Configure Guest Access policy on the ZD")
        self.zd.set_guestaccess_policy()
        self.zd.set_guestpass_policy("Local Database", self.conf['is_pass_expired_after_used'], self.conf['valid_time'])


    def _generateASingleGuestPass(self):
        gp_cfg = {'username': self.conf['username'],
                  'password': self.conf['password'],
                  'wlan': self.wlan_cfg['ssid'],
                  'duration': self.conf['expired_duration'],
                  'duration_unit': 'Days',
                  'type': 'single',
                  'guest_fullname': 'Guest Reading',
                  'remarks': '',
                  'key': '',
                  }

        logging.info("Generate a Guest Pass on the ZD")
        lib.zd.ga.generate_guestpass(self.zd, **gp_cfg)
        self.guest_pass = lib.zd.ga.guestpass_info['single_gp']['guest_pass']
        self.guest_name = lib.zd.ga.guestpass_info['single_gp']['guest_name']


    def _cfgCreateUser(self):
        logging.info("Create a User on the ZD")
        self.zd.create_user(self.conf['username'], self.conf['password'])


    def _cfgRemoveAllWlanProfilesOnStation(self):
        for station in self.station:
            if station.get_ip_addr() == self.conf['target_station_ip']:
                # Found the target station
                self.target_station = station
                self._cfgRemoveStationWlanProfiles()
                break

        if not self.target_station:
            errmsg = "Target station % s not found. " % self.conf['target_station']
            self.errmsg = self.errmsg + errmsg
            logging.info(errmsg)
            raise Exception(errmsg)


    def _cfgRemoveStationWlanProfiles(self):
        logging.info("Remove all WLAN profiles on the remote station")
        self.target_station.remove_all_wlan()

        logging.info("Make sure the target station %s disconnects from wireless network" %
                     self.target_station.get_ip_addr())

        errorMsg = "The station did not disconnect from wireless network within %d seconds"

        return self._checkConnectionStatus("disconnected", self.conf['check_status_timeout'], errorMsg)


    def _checkConnectionStatus(self, status, timeout, errorMsg):
        start_time = time.time()
        while True:
            if self.target_station.get_current_status() == status:
                return True

            time.sleep(1)
            if time.time() - start_time > timeout:
                errmsg = errorMsg % timeout
                self.errmsg = self.errmsg + errmsg
                raise Exception(errmsg)
                return False


    def _checkValidGuestPassExpiration(self, guestpass_info):
        # If GuestPass is expired in the amount of time after it's first used,
        # the maximum valid time of this GuestPass is the current time on ZD plus the valid days
        # which configured in the GuestPass expiration policy
        max_expired_time = self.zd.get_current_time()
        max_expired_time = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(max_expired_time, "%A, %B %d, %Y %H:%M:%S %p")) # %p
        max_expired_time = time.mktime(time.strptime(max_expired_time.split()[0], "%Y/%m/%d")) + self.conf['expired_duration'] * 24 * 3600
        guestpass_time = guestpass_info['expire_time']
        guestpass_time = time.mktime(time.strptime(guestpass_time.split()[0], "%Y/%m/%d"))

        if guestpass_time != max_expired_time:
            logging.info("The configured expired time for Guest Pass is: %s" % guestpass_time)
            logging.info("The right expired time for Guest Pass is: %s" % max_expired_time)
            errmsg = "The expired time for the Guest Pass %s is not right. " % self.guest_pass
            self.errmsg = self.errmsg + errmsg
            logging.debug(errmsg)


    def _checkExpirityStatus(self):
        # Make sure that target station is in the "Unauthorized" status after doing guest auth with expired guest pass
        time.sleep(2)
        logging.info("Verify information of the target station shown on the ZD")
        client_info_on_zd = None
        start_time = time.time()

        contd = True
        while contd:
            active_client_list = self.zd.get_active_client_list()
            for client in active_client_list:
                if client['mac'].upper() == self.sta_wifi_mac_addr.upper():
                    if client['status'] == 'Authorized':
                        logging.debug("Active Client: %s" % str(client))
                        errmsg = "The status of station is %s instead of 'Unauthorized'"
                        errmsg += "after doing Guest authentication with expired Guest Pass. " % client['status']
                        self.errmsg = self.errmsg + errmsg
                        logging.debug(errmsg)
                        return

                    client_info_on_zd = client
                    contd = False

                    break #the for loop

            if not contd or time.time() - start_time > self.conf['check_status_timeout']:
                logging.debug("Active Client: %s" % str(client_info_on_zd))
                logging.info("The status of station is %s now" % client_info_on_zd['status'])

                break #the while loop

        if not client_info_on_zd:
            logging.debug("Active Client List: %s" % str(active_client_list))
            errmsg = "ZD didn't show any info about the target station (with MAC %s). " % self.sta_wifi_mac_addr
            self.errmsg = self.errmsg + errmsg
            logging.debug(errmsg)


    def _associateClient(self):
        logging.info("Configure a WLAN with SSID %s on the target station %s" %
                        (self.wlan_cfg['ssid'], self.target_station.get_ip_addr()))
        self.target_station.cfg_wlan(self.wlan_cfg)

        logging.info("Make sure the station associates to the WLAN")

        errorMsg = "The station didn't associate to the wireless network after %d seconds"

        self._checkConnectionStatus("connected", self.conf['check_status_timeout'], errorMsg)

        logging.info("Renew IP address of the wireless adapter on the target station")
        self.target_station.renew_wifi_ip_address()

        logging.info("Get IP and MAC addresses of the wireless adapter on the target station %s" % \
                     self.target_station.get_ip_addr())

        start_time = time.time()

        while time.time() - start_time < self.conf['check_status_timeout']:
            self.sta_wifi_ip_addr, self.sta_wifi_mac_addr = self.target_station.get_wifi_addresses()
            if self.sta_wifi_mac_addr and self.sta_wifi_ip_addr and self.sta_wifi_ip_addr != "0.0.0.0" and \
               not self.sta_wifi_ip_addr.startswith("169.254"):
                break

            time.sleep(1)


    def _performClientAuthentication(self):
        time.sleep(5)
        logging.info("Perform Guest Pass authentication on the target station %s" % self.target_station.get_ip_addr())

        try:
            auth_failed = False
            arg = tconfig.get_guest_auth_params(self.zd, self.guest_pass, self.conf['use_tou'], self.conf['redirect_url'])
            self.target_station.perform_guest_auth(arg)

        except Exception, e:
            auth_failed = True
            errmsg = "Provided Guest Pass is invalid".strip()
            if not errmsg in e.message:
                self.errmsg = self.errmsg + e.message
                logging.debug(errmsg + " " + e.message)
                return

        if not auth_failed:
            errmsg = "Guest authentication could not be done while the Guest Pass had expired. "
            self.errmsg = self.errmsg + errmsg
            logging.debug(errmsg)


    def _performGuestPassAuthentication(self):
        logging.info("Perform Guest Pass authentication on the target station %s" % self.target_station.get_ip_addr())
        time.sleep(5)

        arg = tconfig.get_guest_auth_params(self.zd, self.guest_pass, self.conf['use_tou'], self.conf['redirect_url'])
        self.target_station.perform_guest_auth(arg)

        logging.info("Verify information of the target station shown on the ZD")
        client_info_on_zd = None
        start_time = time.time()
        found = False

        while True:
            active_client_list = self.zd.get_active_client_list()
            for client in active_client_list:
                if client['mac'].upper() == self.sta_wifi_mac_addr.upper():
                    client_info_on_zd = client
                    if client['status'] == 'Authorized':
                        found = True
                        break

            if found:
                logging.debug("Active Client: %s" % str(client_info_on_zd))
                logging.info("The status of station is %s now" % client_info_on_zd['status'])
                break

            if time.time() - start_time > self.conf['check_status_timeout']:
                if client_info_on_zd:
                    logging.debug("Active Client: %s" % str(client_info_on_zd))
                    errmsg = "The station status shown on ZD is %s instead of 'Authorized' after doing Guest authentication. " % client_info_on_zd['status']
                    self.errmsg = self.errmsg + errmsg
                    logging.debug(errmsg)
                    return

                if not client_info_on_zd:
                    logging.debug("Active Client list: %s" % str(active_client_list))
                    errmsg = "ZD didn't show any info about the target station (with MAC %s). " % self.sta_wifi_mac_addr
                    self.errmsg = self.errmsg + errmsg
                    logging.debug(errmsg)
                    return


    def _testGuestPassExpiration(self):

        self._cfgConfigPolicy()

        self._generateASingleGuestPass()

        if self.conf['is_pass_expired_after_used']:
            self._associateClient()

            self._performGuestPassAuthentication()

        # Get guest pass information in the Generated Guest Passes table
        guestpass_info = lib.zd.ga.get_guestpass_by_name(self.zd, self.guest_name)

        if self.conf['is_pass_expired_after_used']:
            self._checkValidGuestPassExpiration(guestpass_info)

        # Change ZD system time to make Guest Pass expired by changing the PC time and ZD is synced with this new PC time
        logging.info("The Guest Pass %s is valid until %s" %
                     (lib.zd.ga.guestpass_info['single_gp']['guest_pass'], guestpass_info['expire_time']))
        logging.info("Change ZD time so that all the generated guest passes are expired")

        tmptime = datetime.datetime.now() + datetime.timedelta(days = 365)
        os.system("date %s" % str(tmptime.month) + "-" + str(tmptime.day) + "-" + str(tmptime.year))
        time.sleep(5)
        self.zd.get_current_time(True)

        try:
            if self.conf['is_pass_expired_after_used']:
                self.zd.remove_all_active_clients()
            else:
                self._associateClient()

                self._performClientAuthentication()

            self._checkExpirityStatus()

        except:
            raise

        finally:
            logging.info("Return the previous system time for ZD")
            tmptime = datetime.datetime.now() + datetime.timedelta(days = -365)
            os.system("date %s" % str(tmptime.month) + "-" + str(tmptime.day) + "-" + str(tmptime.year))
            time.sleep(5)
            self.zd.get_current_time(True)

        if self.conf.has_key('is_pass_expired_after_used') and self.conf['is_pass_expired_after_used']:
            msg = 'Effective from first use'
        else:
            msg = 'Effective from the creation time'

        self.passmsg = "Guest pass is expired correctly when option %s is selected. " % msg


