# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_ACL_Policy Test class tests the ability of a station to associate to the wlan-enabled ACL
with a given security configuration. The ability to associate is confirmed via a ping test.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: 'ip': 'IP address to ping',
                    'target_station': 'ip address of target station',
                    'use_allow_acl': 'This is the bool value determine that if creating an ACL with allow-all policy or not.
                                      If it is True, the created ACL has allow-all policy.
                                      Otherwise, that ACL has deny-all policy'
                    'allow_station': 'This is the bool value. If it is True, the client is allowed to associate to the WLAN.
                                     Otherwise, It can not associate to the WLAN'
                    'verify_acl': 'This is bool value determine that whether verify information of created ACL or not.
                                   If it is True, verify information of ACL only. If it is False, checking that ACL operates well'

   Result type: PASS/FAIL
   Results: PASS: If 'verify_acl' is True, verify information of ACL about policy and mac addresses within it.
                  If 'verify_acl' is False:
                      - If target station is allowed by ACL, it has full access to that wlan,
                        ping to a destination successfully, and information is shown correctly in ZD.
                      - If target stations is denied by ACL, it can not associate to the wlan, and its entry is not shown in ZD
            FAIL: if one of the above criteria is not satisfied

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Remove all configuration about WLANs, and active clients on the ZD
       - Remove all ACL rules on the ZD
       - Remove all WLAN configuration on the target station
   2. Test:
       - Create a ACL rule with given parameter
       - Configure a WLAN on the ZD with given security setting, apply ACL to this WLAN
       - If 'verify_acl' is True, verify information of the created ACL including policy, mac addresses
       - If 'verify_acl_is False, make sure that ACL operates well:
           + If target station is allowed to associate the wlan:
               - Configure the target station with given security setting
               - Wait until it gets associated and get IP and MAC addresses of the wireless adapter
               - Do a ping to make sure the AP forwards the traffic from the station
               - Verify if the ZD shows correct information about the connected station
           + If target station is denied by ACL:
               - Configure the target station with given security setting
               - Make sure that the target station can not connect to the wireless network by verifying that
               its status is always "disconnected".
               - Verify that there's no entry of target station shown on the ZD
   3. Cleanup:
       - Remove all wlan configuration on ZD
       - Remove all ACL rules configured on the ZD
       - Remove wireless profile on remote wireless STA
       - Verify if wireless station is completed disconnect after remove wireless profile.

   How it is tested?
       - While the test is running, remove mac address of target station within the ACL, the script should report FAIL
       - After the client has associated to the wlan successfully, go to the table Active Clients and delete the entry
       of target station. The script should report that the information of that station is now shown on the ZD
       - While the test is running, the ACL policy is deny-all, and target station is not restricted. After applying ACL
       to the wlan, login to the ZD's GUI, add mac address of target station to ACL. The script should report that station
       could not associate to the wlan while it's not prevented by ACL
"""

import time
import logging

from RuckusAutoTest.models import Test


class ZD_ACL_Policy(Test):
    required_components = ['ZoneDirector', 'Station', 'RuckusAP']
    parameter_description = {'use_allow_acl' :'This is the bool value. If it is True, the policy of created ACL rule is allow-all.\
                                                Otherwise, the policy of created ACL rule is deny-all.',
                              'target_station':'ip address of target station',
                              'allow_station' :'This is the bool value. If it is True, the client is allowed to associate to the wlan.\
                                                Otherwise, It can not associate to the wlan',
                              'ip'            :'ip address to ping',
                              'verify_acl'    :'This is bool value determine that whether verify information of created ACL or not. \
                                                If it is True, verify information of ACL only. If it is False, checking that ACL operates well'}

    def config(self, conf):

        self.ip_addr = conf['ip']
        self.verify_acl = conf['verify_acl']
        self.use_allow_acl = conf['use_allow_acl']
        self.allow_station = conf['allow_station']

        self.ping_timeout = 150
        self.check_status_timeout = 120
        self.acl_name = ["Netanya_ACL"]
        self.mac_addr_list = []
        self.target_station = None
        self.wlan_cfg = {'username': '', 'sta_auth': 'open', 'ras_port': '', 'key_index': '', 'auth': 'open',
                          'sta_encryption': 'none', 'ras_addr': '', 'password': '', 'use_guest_access': False,
                          'ad_domain': '', 'ad_port': '', 'ssid': 'wlan_access_control', 'key_string': '',
                          'sta_wpa_ver': '', 'encryption': 'none', 'ad_addr': '', 'wpa_ver': '', 'ras_secret': '',
                          'acl_name': self.acl_name[0]}

        logging.info("Remove all wlans on the Zone Director")
        self.testbed.components['ZoneDirector'].remove_all_wlan()

        logging.info("Remove all acl rules on the Zone Director")
        self.testbed.components['ZoneDirector'].remove_all_acl_rules()

        # Find target station
        for station in self.testbed.components['Station']:
            if station.get_ip_addr() == conf['target_station']:
                # Found the target station
                self.target_station = station
                break
        if not self.target_station:
            raise Exception("Target station %s not found" % conf['target_station'])

        # Get mac address of wireless adapter on the target station.
        # This address is used as the restricted mac address in an ACL rule
        sta_wifi_ip_addr = None
        self.sta_wifi_mac_addr = None
        try:
            sta_wifi_ip_addr, self.sta_wifi_mac_addr = self.target_station.get_wifi_addresses()
        except:
            raise Exception("Unable to get MAC address of the wireless adapter of the target station %s" % 
                            self.target_station.get_ip_addr())

        if not self.verify_acl:
            # If this ACL is applied to the wlan, remove all wlan profiles on the station
            logging.info("Remove all active clients on the Zone Director")
            self.testbed.components['ZoneDirector'].remove_all_active_clients()

            logging.info("Remove all WLAN profiles on the target station %s" % self.target_station.get_ip_addr())
            self.target_station.remove_all_wlan()

            logging.info("Make sure the target station %s disconnects from wireless network" % 
                         self.target_station.get_ip_addr())
            start_time = time.time()
            while True:
                if self.target_station.get_current_status() == "disconnected":
                    break
                time.sleep(1)
                if time.time() - start_time > self.check_status_timeout:
                    raise Exception("The station did not disconnect from wireless network within %d seconds" % 
                                    self.check_status_timeout)

    def test(self):

        # Create an allow ACL
        if self.use_allow_acl:
            policy = "allow-all"
            if self.allow_station:
                # If station is allowed to associate to the wlan, add mac address to ACL
                self.mac_addr_list.append(self.sta_wifi_mac_addr)
            else:
                # Otherwise, add the any mac address to ACL
                self.mac_addr_list.append("aa:bb:cc:dd:ee:ff")
        else:
            # Create an deny ACL
            policy = "deny-all"
            if not self.allow_station:
                # If station is denied to associate to the wlan, add its mac address to ACL
                self.mac_addr_list.append(self.sta_wifi_mac_addr)
            else:
                # Otherwise, add the any mac address to ACL
                self.mac_addr_list.append("aa:bb:cc:dd:ee:ff")

        msg = "Create an ACL rule with following information: acl name ----- %s; " % self.acl_name[0]
        msg += "policy ----- '%s'; mac address ----- %s" % (policy, self.mac_addr_list[0])
        logging.info(msg)
        
        if self.mac_addr_list:
            self.testbed.components['ZoneDirector'].create_acl_rule(self.acl_name, self.mac_addr_list,
                                                               self.use_allow_acl)

        # Verify information of the created ACL
        if self.verify_acl:
            acl_info = self.testbed.components['ZoneDirector'].get_acl_info(self.acl_name[0])
            if not acl_info:
                return ["FAIL", "ACL %s does not appear in the Access Controls table" % self.acl_name[0]]
            else:
                if acl_info['policy'] != policy:
                    return ["FAIL", "Policy of ACL shown on the ZD is '%s' while it is '%s'" % 
                            (acl_info['policy'], policy)]
                if acl_info['mac_entries'] != self.mac_addr_list:
                    logging.debug("MAC entries must be added to the ACL: %s" % str(self.mac_addr_list))
                    logging.debug("MAC entries shown on the ZD: %s" % str(acl_info['mac_entries']))
                    return ["FAIL", "Mac address entries shown on the ZD is not correct"]
            logging.info("The ACL %s is created correctly" % self.acl_name[0])

        else:
            # Otherwise, verify the functionality of the created ACL
            logging.info("Configure a WLAN with SSID %s on the Zone Director" % self.wlan_cfg['ssid'])
            self.testbed.components['ZoneDirector'].cfg_wlan(self.wlan_cfg)

            logging.info("Configure a WLAN with SSID %s on the target station %s" % 
                        (self.wlan_cfg['ssid'], self.target_station.get_ip_addr()))
            self.target_station.cfg_wlan(self.wlan_cfg)

            # With an allow ACL, make sure that the station matching with ACL has full access to the wlan
            # But the station not matching with ACL can not associate to the wlan
            if self.use_allow_acl:
                if self.allow_station:
                    # The station is in the allowed list of ACL, it has full access to the wlan
                    logging.info("The station is matched with allow ACL, make sure it can associate to the WLAN")
                    status, msg = self._verifyClientStatus(True, True)
                    if status == "FAIL":
                        return [status, msg]

                    logging.info("Renew IP address of the wireless adapter on the target station")
                    self.target_station.renew_wifi_ip_address()

                    logging.info("Get IP and MAC addresses of the wireless adapter on the target station %s" % 
                                 self.target_station.get_ip_addr())
                    sta_wifi_ip_addr, sta_wifi_mac_addr = self._getStaWifiAddrs()

                    logging.info("Verify information of the target station shown on the Zone Director")
                    status, msg = self._verifyClientInfoOnZD(True, sta_wifi_mac_addr, sta_wifi_ip_addr)
                    if status == "FAIL":
                        return [status, msg]

                    logging.info("Ping to %s from the target station (timeout: %s)" % (self.ip_addr, self.ping_timeout))
                    ping_result = self.target_station.ping(self.ip_addr, self.ping_timeout * 1000)
                    if ping_result.find("Timeout") != -1:
                        logging.info("Ping FAILED")
                        return ("FAIL", "The target station could not send traffic while it has full access to the wireless network")
                    else:
                        logging.info("Ping OK ~~ %s second(s)" % ping_result)

                else:
                    # Although the policy of ACL is 'allow-all', the target station can not associate to the wlan
                    # because it is not in the allowed list of ACL
                    logging.info("The station is not matched with allow ACL, make sure it can not associate to the WLAN")
                    status, msg = self._verifyClientStatus(True, False)
                    if status == "FAIL":
                        return [status, msg]

                    logging.info("Verify information of the target station shown on the Zone Director")
                    status, msg = self._verifyClientInfoOnZD(False, self.sta_wifi_mac_addr)
                    if status == "FAIL":
                        return [status, msg]
                    logging.info("There is no entry of the target station %s on the ZD" % self.target_station.get_ip_addr())

            # With a deny ACL, make sure that the station is matched with ACL can not associate to the wlan
            # But the station is not matched has full access to that wlan
            else:
                if self.allow_station:
                    # The target station is not in the denied list of ACL, it has full access to the wlan
                    logging.info("The stations is not matched with deny ACL, make sure that the station can associate to the WLAN")
                    status, msg = self._verifyClientStatus(False, True)
                    if status == "FAIL":
                        return [status, msg]

                    logging.info("Renew IP address of the wireless adapter on the target station")
                    self.target_station.renew_wifi_ip_address()

                    logging.info("Get IP and MAC addresses of the wireless adapter on the target station %s" % 
                                 self.target_station.get_ip_addr())
                    sta_wifi_ip_addr, sta_wifi_mac_addr = self._getStaWifiAddrs()

                    logging.info("Verify information of the target station shown on the Zone Director")
                    status, msg = self._verifyClientInfoOnZD(True, sta_wifi_mac_addr, sta_wifi_ip_addr)
                    if status == "FAIL":
                        return [status, msg]

                    logging.info("Ping to %s from the target station (timeout: %s)" % (self.ip_addr, self.ping_timeout))
                    ping_result = self.target_station.ping(self.ip_addr, self.ping_timeout * 1000)
                    if ping_result.find("Timeout") != -1:
                        logging.info("Ping FAILED")
                        return ("FAIL", "The target station could not send traffic while it has full access to the wlan")
                    else:
                        logging.info("Ping OK ~~ %s second(s)" % ping_result)

                else:
                    # Make sure that station can not associate to the wlan because it is denied by ACL.
                    logging.info("The stations is matched with deny ACL, make sure the station can not associate to the WLAN")
                    status, msg = self._verifyClientStatus(False, False)
                    if status == "FAIL":
                        return [status, msg]

                    logging.info("Verify information of the target station shown on the Zone Director")
                    status, msg = self._verifyClientInfoOnZD(False, self.sta_wifi_mac_addr)
                    logging.info("There is no entry of the target station %s on the zoneDirector" % 
                                 self.target_station.get_ip_addr())

        return ["PASS", ""]

    def cleanup(self):

        if self.verify_acl:
            logging.info("Remove all ACL rules on the Zone Director")
            self.testbed.components['ZoneDirector'].remove_all_acl_rules()

        else:
            # If ACL is applied to the wlan, remove all configurations related to ACL
            logging.info("Remove all wlans on the Zone Director")
            self.testbed.components['ZoneDirector'].remove_all_wlan()

            logging.info("Remove all ACL rules on the Zone Director")
            self.testbed.components['ZoneDirector'].remove_all_acl_rules()

            if self.target_station:
                logging.info("Remove all WLAN profiles on the remote station")
                self.target_station.remove_all_wlan()

                logging.info("Make sure the target station disconnects from the wireless networks")
                start_time = time.time()
                while True:
                    if self.target_station.get_current_status() == "disconnected":
                        break
                    time.sleep(1)
                    if time.time() - start_time > self.check_status_timeout:
                        raise Exception("The station did not disconnect from wireless network within %d seconds" % 
                                        self.check_status_timeout)
        logging.info("-------- FINISHED --------\n")

    def _verifyClientInfoOnZD(self, is_allow_associate, sta_wifi_mac_addr = "", sta_wifi_ip_addr = ""):
        """
        This function verify information of target station shown on the ZD.
        - is_allow_associate: This is the bool value. If it's True, the target station can associate to the wlan.
                              Otherwise, the target station can not
        - sta_wifi_ip_addr: ip address of target station
        - sta_wifi_mac_addr: mac address of target station
        """
        # Verify information of target station on the ZD when it has full access to the wireless network
        if is_allow_associate:
            client_info_on_zd = None
            status_verifying_count = 5
            start_time = time.time()
            while time.time() - start_time < self.check_status_timeout:
                active_client_list = self.testbed.components['ZoneDirector'].get_active_client_list()
                for client in active_client_list:
                    if client['mac'].upper() == sta_wifi_mac_addr.upper():
                        if client['status'] != 'Authorized':
                            # This loop gives the ZD time to update its knowledge of the clients
                            if status_verifying_count == 0:
                                return ("FAIL",
                                        "The station status shown on ZD is '%s' instead of 'Authorized'" % 
                                        client['status'])
                            status_verifying_count = status_verifying_count - 1
                            break
                        if client['ip'] != sta_wifi_ip_addr:
                            if status_verifying_count == 0:
                                return ("FAIL", "The station wifi IP address shown on ZD is %s instead of %s" % 
                                        (client['ip'], sta_wifi_ip_addr))
                            status_verifying_count = status_verifying_count - 1
                            break
                        client_info_on_zd = client
                        break
                if client_info_on_zd: break
                time.sleep(1)

            if not client_info_on_zd:
                logging.debug("Active Client List: %s" % str(active_client_list))
                return ("FAIL", "Zone Director didn't show any info about the target station (with MAC %s)" % sta_wifi_mac_addr)

        else:
            # The target station can not associate to the wlan, make sure that there's no entry about shown on the ZD
            start_time = time.time()
            while time.time() - start_time < self.check_status_timeout:
                active_client_list = self.testbed.components['ZoneDirector'].get_active_client_list()
                for client in active_client_list:
                    if client['mac'].upper() == sta_wifi_mac_addr.upper():
                        logging.debug("Client information: %s" % str(client))
                        msg = "The entry of target station appears in the Active Client table "
                        msg += "while it can not associate to the WLAN"
                        return ["FAIL", msg]
                    time.sleep(1)
            logging.debug("Active client list: %s" % str(active_client_list))

        return ["", ""]

    def _getStaWifiAddrs(self):
        """
        This function gets mac address and ip address of the target station after associating to the wlan
        Loop until can get both MAC address & IP on target station
        Raise exception if can get all both MAC & IP Address after check status self.check_status_timeout
        """
        start_time = time.time()
        sta_wifi_ip_addr = None
        sta_wifi_mac_addr = None
        while time.time() - start_time < self.check_status_timeout:
            sta_wifi_ip_addr, sta_wifi_mac_addr = self.target_station.get_wifi_addresses()
            if sta_wifi_mac_addr and sta_wifi_ip_addr and sta_wifi_ip_addr != "0.0.0.0" and \
               not sta_wifi_ip_addr.startswith("169.254"):
                break
            time.sleep(1)

        if not sta_wifi_mac_addr:
            raise Exception("Unable to get MAC address of the wireless adapter of the target station %s" % 
                            self.target_station.get_ip_addr())
        elif not sta_wifi_ip_addr:
            raise Exception("Unable to get IP address of the wireless adapter of the target station %s" % 
                            self.target_station.get_ip_addr())
        elif sta_wifi_ip_addr == "0.0.0.0" or sta_wifi_ip_addr.startswith("169"):
            raise Exception("The target station %s could not get IP address from DHCP server" % 
                            self.target_station.get_ip_addr())
        return sta_wifi_ip_addr, sta_wifi_mac_addr

    def _verifyClientStatus(self, use_allow_acl, allow_station):
        """
        This function verifies status of target station when it tries to associate to the WLAN.
        - use_allow_acl: This is the bool value. If it's True, the target station is restricted in the allow ACL.
                                  Otherwise, it's restricted in the deny ACL
        - allow_station: This is the bool value determining whether the target station can associate
                                      to the WLAN or not
        - self.check_status_timeout: the maximum time to get status of target station
        """
        # If ACL rule is allow-all, verify that if the target station is in the allowed list of ACL,
        # its status is "connected". Otherwise, its status is "disconnected"
        if use_allow_acl:
            start_time = time.time()
            while time.time() - start_time <= self.check_status_timeout:
                if allow_station:
                    if self.target_station.get_current_status() == "connected":
                        logging.info("The target station is connected to the ZD now")
                        return ["", ""]
                else:
                    if self.target_station.get_current_status() == "connected":
                        msg = "The target station can associate to the wireless network "
                        msg += "while it is not matched with allow ACL"
                        return ["FAIL", msg]
                time.sleep(1)

            if time.time() - start_time > self.check_status_timeout:
                if allow_station:
                    return ["FAIL", "The target station does not associate to the wireless network after %d seconds" % self.check_status_timeout]
                else:
                    logging.info("The target station disconnects from the ZD because it is not allowed by ACL")
                    return ["", ""]

        else:
            # If ACL rule is deny-all, verify that if the target station is not in the denied list of ACL,
            # its status is "connected". Otherwise, its status is "disconnected"
            start_time = time.time()
            while time.time() - start_time <= self.check_status_timeout:
                if not allow_station:
                    if self.target_station.get_current_status() == "connected":
                        msg = "The target station can associate to the wireless network "
                        msg += "while it is matched with deny ACL"
                        return ["FAIL", msg]
                else:
                    if self.target_station.get_current_status() == "connected":
                        logging.info("The target station associates to the WLAN successfully")
                        return ["", ""]
                time.sleep(1)

            if time.time() - start_time > self.check_status_timeout:
                if not allow_station:
                    logging.info("The target station disconnects from the ZD now")
                    return ["", ""]
                else:
                    msg = "The target station can not associate to the wireless network "
                    msg += "while it is not matched with deny ACL"
                    return ["FAIL", msg]

