# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_ACL_Capacity Test class tests the ability of the ZD to create maximum number of ACLs or create
maximum number of MAC within an ACL, and verify that the ACLs are still functional after adding maximum number.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: 'ip': 'IP address to ping',
                    'target_station': 'ip address of target station',
                    'verify_max_acls': 'This is the bool value. If it is True, the script verifies that after creating
                                        maximum number of ACLs, these ACLs are still functional.
                                        Otherwise, the script verifies the functionality of an ACL with maximum mac addresses'
                    'max_entries': 'This is the bool value determine creating maximum number of ACLs or
                                    maximum number of MAC within ACL'

   Result type: PASS/FAIL
   Results: PASS: ACLs are still functional after adding maximum number. If mac address of target station is in the allow ACL,
                  it has full access to the wlan. If its mac address is in the deny ACL, it can not associtate to that wlan.
            FAIL: if one of the above criteria is not satisfied

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Remove all configuration about WLANs, and active clients on the ZD
       - Remove all ACL rules on the ZD
       - Remove all WLAN configuration on the target station
   2. Test:
       - If 'verify_mac_acls' is True:
           + Create maximum number of ACLs. Each ACL has allow-all policy, and mac address of station's.
           + Verify that total of ACLs created on the ZD is correct (It equal 'max_entries')
           + Perform functional test on three ACLs (the first, the middle, and the last):
               - Configure a WLAN on the ZD with given security setting, apply ACL to this WLAN
               - Configure the target station with given security setting
               - The target station is in the allow list of ACL. Verify that it has full access to the wlan, and
               its information shown on the ZD correctly
               - Change policy of ACL to 'deny-all'. Verify that the target station can not associate to the wlan any more
       - If 'verify_mac_acls' is False:
            + Create an ACL with maximum mac addresses, and allow-all policy. The last MAC is the station's, .
            + Configure a WLAN on the ZD with given security setting, apply ACL to this WLAN
            + Configure the target station with given security setting
            + The target station is in the allow list of ACL. Verify that it has full access to the wlan, and
               its information shown on the ZD correctly
            + Change policy of ACL to 'deny-all'. Verify that the target station can not associate to the wlan any more
   3. Cleanup:
       - Remove all wlan configuration on ZD
       - Remove all ACL rules configured on the ZD
       - Remove wireless profile on remote wireless STA
       - Verify if wireless station is completed disconnect after remove wireless profile.

   How it is tested?
       - After the client has associated to the wlan successfully, go to the table Active Clients and delete the entry
       of target station. The script should report that the information of that station is now shown on the ZD
       - While the test is running, the ACL policy is allow-all, and target station is not restricted. After applying ACL
       to the wlan, login to the ZD's GUI, remove mac address of target station out of the ACL. The script should report
       that station could not associate to the wlan while it's not prevented by ACL
"""

import time
import logging

from RuckusAutoTest.models import Test


class ZD_ACL_Capacity(Test):
    required_components = ['ZoneDirector']
    parameter_description = {'verify_max_acls' :'This is the bool value. If it is True, the script verifies that \
                                                  after creating maximum number of ACLs, these ACLs are still functional. \
                                                  Otherwise, the script verifies the functionality of an ACL with maximum mac addresses',
                              'target_station'  :'ip address of target station',
                              'max_entries'     :'This is the bool value determine creating maximum number of ACLs or \
                                                  maximum number of MAC within ACL',
                               'ip'             :'ip address to ping'}

    def config(self, conf):
        self.ip_addr = conf['ip']
        self.verify_max_acls = conf['verify_max_acls']
        self.ping_timeout = 150
        self.check_status_timeout = 120

        if self.verify_max_acls:
            self.max_acl_entries = conf['max_entries']
        else:
            self.max_mac_entries = conf['max_entries']
        self.acl_name_list = []
        self.acl_mac_list = []
        self.target_station = None
        self.wlan_cfg = {'username': '', 'sta_auth': 'open', 'ras_port': '', 'key_index': '', 'auth': 'open',
                          'sta_encryption': 'none', 'ras_addr': '', 'password': '', 'use_guest_access': False,
                          'ad_domain': '', 'ad_port': '', 'ssid': 'wlan_access_control', 'key_string': '',
                          'sta_wpa_ver': '', 'encryption': 'none', 'ad_addr': '', 'wpa_ver': '', 'ras_secret': '',
                          'acl_name': ''}

        # Make sure APs in the testbed connecting to the ZD
        self.connected_aps_list = []
        aps_info = self.testbed.components['ZoneDirector'].get_all_ap_info()
        for ap in aps_info:
            if ap['status'].lower().startswith("connected"):
                self.connected_aps_list.append(ap)

        if not aps_info:
            raise Exception("No APs connected to the ZD")
        if len(self.connected_aps_list) != len(self.testbed.components['AP']):
            raise Exception("At least %d AP(s) in the testbed disconnected from the ZD" % 
                            (len(self.testbed.components['AP']) - len(self.connected_aps_list)))

        logging.info("Remove all wlans on the Zone Director")
        self.testbed.components['ZoneDirector'].remove_all_wlan()

        logging.info("Remove all active clients on the Zone Director")
        self.testbed.components['ZoneDirector'].remove_all_active_clients()

        logging.info("Remove all ACL rules on the Zone Director")
        self.testbed.components['ZoneDirector'].remove_all_acl_rules()

        for station in self.testbed.components['Station']:
            if station.get_ip_addr() == conf['target_station']:
                # Found the target station
                self.target_station = station
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
                logging.info("Renew IP address of the wireless adapter on the target station")
                self.target_station.renew_wifi_ip_address()
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

    def test(self):
        if self.verify_max_acls:
            # Create maximum names of ACL entries
            for i in range(self.max_acl_entries):
                acl_name = "Test_max_ACLs_%d" % i
                self.acl_name_list.append(acl_name)
            self.acl_mac_list.append(self.sta_wifi_mac_addr)

            logging.info("Create %d ACL rules on the Zone Director" % len(self.acl_name_list))
            msg = "Each ACL has name prefix ---- Test_max_ACLs; policy ----- \'allow-all\'; "
            msg += "restricted mac addr ----- %s" % self.acl_mac_list[0]
            logging.info(msg)
            self.testbed.components['ZoneDirector'].create_acl_rule(self.acl_name_list, self.acl_mac_list, True)

            # Verify that maximum number of ACLs are created on the ZD successfully
            created_acl_list = self.testbed.components['ZoneDirector'].get_all_acl_names()
            if len(created_acl_list) != len(self.acl_name_list):
                logging.debug("The maximum number of ACLs must be created: %d" % len(self.acl_name_list))
                logging.debug("The maximum number of ACLs shown on the ZD: %d" % len(created_acl_list))
                return ["FAIL", "The total of ACL rules  is not correct"]

            # Verify that name of each ACL created correctly
            for acl_name in self.acl_name_list:
                if not acl_name in created_acl_list:
                    return ["FAIL", "The ACL %s is not shown on the ZD" % acl_name]
            logging.info("Create %d ACLs on the ZD successfully" % len(self.acl_name_list))

            logging.info("Make sure that the created ACLs operate well by trying with the first ACL in the ACL table")
            msg = "The first ACL information: acl_name ----- %s; policy ----- \'allow-all\'; " % self.acl_name_list[0]
            msg += "mac address in ACL ----- %s" % self.sta_wifi_mac_addr
            logging.info(msg)
            result, msg = self._verifyACLFunctionality(self.acl_name_list[0])
            if result == "FAIL":
                return [result, msg]

            logging.info("Make sure that the created ACLs operate well by trying with the 500th ACL in the ACL table")
            msg = "The 500th ACL information: acl_name ----- %s; policy ----- \'allow-all\'; " % self.acl_name_list[499]
            msg += "mac address in ACL ----- %s" % self.sta_wifi_mac_addr
            logging.info(msg)
            self.testbed.components['ZoneDirector'].remove_all_wlan()
            self._remove_wlansOnStation()
            result, msg = self._verifyACLFunctionality(self.acl_name_list[499])
            if result == "FAIL":
                return [result, msg]

            logging.info("Make sure that the created ACLs operate well by trying with the last ACL in the ACL table")
            msg = "The last ACL information: acl_name ----- %s; policy ----- \'allow-all\'; " % self.acl_name_list[-1]
            msg += "mac address in ACL ----- %s" % self.sta_wifi_mac_addr
            logging.info(msg)
            self.testbed.components['ZoneDirector'].remove_all_wlan()
            self._remove_wlansOnStation()
            result, msg = self._verifyACLFunctionality(self.acl_name_list[-1])
            if result == "FAIL":
                return [result, msg]

        else:
            self.acl_name_list.append("Test_max_mac_addr")
            # Create randomly maximum mac addresses, but the last mac address is target station's
            mac_random = ''
            for i in range(self.max_mac_entries - 1):
                for j in range(6):
                    mac_random = mac_random + "%02x" % (i + j) + ":"
                self.acl_mac_list.append(mac_random.rstrip(':'))
                mac_random = ""
            self.acl_mac_list.append(self.sta_wifi_mac_addr)

            msg = "Create an ACL rule: acl name ---- %s; policy ----- \'allow-all\'; " % self.acl_name_list[0]
            msg += "maximum number of MAC ---- %d" % len(self.acl_mac_list)
            logging.info(msg)
            self.testbed.components['ZoneDirector'].create_acl_rule(self.acl_name_list, self.acl_mac_list, True)

            # Verify that maximum mac addresses are added to the ACL correctly
            added_mac_list = self.testbed.components['ZoneDirector'].get_acl_info(self.acl_name_list[0])
            if len(added_mac_list['mac_entries']) != len(self.acl_mac_list):
                logging.debug("The maximum mac addresses must be added ----- %d" % len(self.acl_mac_list))
                logging.debug("The maximum mac addresses shown on the ZD ----- %d" % len(added_mac_list['mac_entries']))
                return ["FAIL", "The total of restricted mac addresses is not correct"]
            # Verify that each mac address is added correctly
            for mac in self.acl_mac_list:
                if not mac in added_mac_list['mac_entries']:
                    return ["FAIL", "MAC address %s is not shown on the ZD" % mac]
            logging.info("ACL with %d mac addresses is created successfully" % len(self.acl_mac_list))

            logging.info("Make sure that the ACL operates well")
            self.wlan_cfg['acl_name'] = self.acl_name_list[0]
            
            #waiting the acl setting send to APs 
            logging.info("delay 5 sec, waiting the acl-allow send to APs")
            time.sleep(5)

            logging.info("Configure a WLAN-enabled ACL with SSID %s and ACL %s on the Zone Director" % 
                         (self.wlan_cfg['ssid'], self.acl_name_list[0]))
            self.testbed.components['ZoneDirector'].cfg_wlan(self.wlan_cfg)

            msg = "Verify that APs in the testbed still stabilize "
            msg += "after applying an ACL with maximum number of MACs to the wlan"
            logging.info(msg)
            time.sleep(100)

            # Try to get director-info on APs to verify that if they disconnect from ZD
            start_time = time.time()
            disconnected_timeout = 180
            while time.time() - start_time < disconnected_timeout:
                try:
                    for ap_comp in self.testbed.components['AP']:
                        ap_comp.verify_component()
                        ap_comp.get_director_info()
                except:
                    time.sleep(1)
                    msg = "APs disconnect from the ZD "
                    msg += "after applying an ACL with maximum number of MACs to the wlan"
                    return ["FAIL", msg]

            logging.info("Configure a WLAN with SSID %s on the target station %s" % 
                        (self.wlan_cfg['ssid'], self.target_station.get_ip_addr()))
            self.target_station.cfg_wlan(self.wlan_cfg)

            status, msg = self._verifyAssociatedClient()
            if status == "FAIL":
                return [status, msg]

            # Change policy of ACL to 'deny-all' and verify that the target station can not associate to the wlan
            logging.info("Change policy of the ACL to \'deny-all\'")
            self.testbed.components['ZoneDirector'].edit_acl_rule(old_acl_name = self.acl_name_list[0], is_modified_policy = True)
            self._remove_wlansOnStation()
            
            #waiting the acl setting send to APs
            logging.info("delay 5 sec, waiting the acl-deny setting send to APs")
            time.sleep(5)

            logging.info("Configure a WLAN with SSID %s on the target station %s one more time" % 
                        (self.wlan_cfg['ssid'], self.target_station.get_ip_addr()))
            self.target_station.cfg_wlan(self.wlan_cfg)
            status, msg = self._verifyDisassociatedClient()
            if status == "FAIL":
                return [status, msg]

        return ["PASS", ""]

    def cleanup(self):

        # Try to remove all wlans on ZD, if exception is raised, catch it and try to remove again
        # If timeout is expired and wlans can not be removed, raise exception
        start_time = time.time()
        timeout = 60
        while True:
            try:
                logging.info("Remove all wlans on the Zone Director")
                self.testbed.components['ZoneDirector'].remove_all_wlan()
                break
            except:
                if time.time() - start_time > timeout:
                    raise Exception("Can not remove all wlans on the ZD")
                time.sleep(1)
        time.sleep(2)

        # Make sure that APs still connect to the ZD
        start_time = time.time()
        timeout = 150
        while True:
            connected = 0
            aps_info = self.testbed.components['ZoneDirector'].get_all_ap_info()
            for ap in aps_info:
                if ap['status'].lower().startswith("connected"):
                    connected += 1
            if connected == len(self.connected_aps_list):
                break
            if time.time() - start_time > timeout:
                raise Exception("There are %d APs disconnecting from the ZD" % (len(self.connected_aps_list) - connected))
            time.sleep(1)

        # Try telnet to each AP if its telnet session was closed
        for ap_comp in self.testbed.components['AP']:
            ap_comp.login()

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

    def _verifyAssociatedClient(self):
        """
        Verify information of target station when it associate to the wlan successfully
        """
        logging.info("The station is in the allowed list of ACL, make sure it can associate to the WLAN")
        start_time = time.time()
        while True:
            if self.target_station.get_current_status() == "connected":
                logging.info("The target station is connected to the ZD now")
                break
            time.sleep(1)
            if time.time() - start_time > self.check_status_timeout:
                return ["FAIL", "The target station does not associate to the wireless network after %d seconds" % 
                        self.check_status_timeout]

        logging.info("Get IP and MAC addresses of the wireless adapter on the target station %s" % 
                     self.target_station.get_ip_addr())
        start_time = time.time()
        sta_wifi_ip_addr = None
        sta_wifi_mac_addr = None
        while time.time() - start_time < self.check_status_timeout:
            sta_wifi_ip_addr, sta_wifi_mac_addr = self.target_station.get_wifi_addresses()
            if sta_wifi_mac_addr and sta_wifi_ip_addr and sta_wifi_ip_addr != "0.0.0.0" and not sta_wifi_ip_addr.startswith("169"):
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

        logging.info("Verify information of the target station shown on the Zone Director")
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
            if client_info_on_zd:
                logging.info("The active client information: ip address ----- %s; status ----- %s" % 
                             (client_info_on_zd['ip'], client_info_on_zd['status']))
                break
            time.sleep(1)

        if not client_info_on_zd:
            logging.debug("Active Client List: %s" % str(active_client_list))
            return ("FAIL", "Zone Director didn't show any info about the target station (with MAC %s)" % sta_wifi_mac_addr)

        logging.info("Ping to %s from the target station (timeout: %s)" % (self.ip_addr, self.ping_timeout))
        ping_result = self.target_station.ping(self.ip_addr, self.ping_timeout * 1000)
        if ping_result.find("Timeout") != -1:
            logging.info("Ping FAILED")
            return ("FAIL", "The target station could not send traffic while it has full access to the wireless network")
        else:
            logging.info("Ping OK ~~ %s second(s)" % ping_result)

        return ["", ""]

    def _verifyDisassociatedClient(self):
        """
        Verify information of target station when it can not associate to the wlan
        """
        logging.info("The station is in the denied list of ACL, make sure the station can not associate to the WLAN")
        start_time = time.time()
        while time.time() - start_time <= self.check_status_timeout:
            if self.target_station.get_current_status() == "connected":
                msg = "The target station can associate to the wireless network "
                msg += "while it is in the denied list of ACL"
                return ["FAIL", msg]
            time.sleep(1)
        if time.time() - start_time > self.check_status_timeout:
            logging.info("The target station disconnects from the ZD now")

        logging.info("Verify information of the target station shown on the Zone Director")
        start_time = time.time()
        while time.time() - start_time < self.check_status_timeout:
            active_client_list = self.testbed.components['ZoneDirector'].get_active_client_list()
            for client in active_client_list:
                if client['mac'].upper() == self.sta_wifi_mac_addr.upper():
                    logging.debug("Client information: %s" % str(client))
                    msg = "The entry of target station appears in the Active Client table "
                    msg += "while it can not associate to the WLAN"
                    return ["FAIL", msg]
                time.sleep(1)
        logging.debug("Active client list: %s" % str(active_client_list))
        logging.info("There is no entry of the target station %s on the zoneDirector" % 
                     self.target_station.get_ip_addr())

        return ["", ""]

    def _verifyACLFunctionality(self, acl_name):
        """
        Verify funtionality of an ACL when it applied to the wlan. If the station matches with ACL,
        it can associate to the wlan successfully. If the station does not match with ACL, it can not associate
        to the wlan.
        Input:
        - acl_name: name of ACL
        """
        self.wlan_cfg['acl_name'] = acl_name
        logging.info("Configure a WLAN-enabled ACL with SSID %s and ACL %s on the Zone Director" % 
                     (self.wlan_cfg['ssid'], acl_name))
        self.testbed.components['ZoneDirector'].cfg_wlan(self.wlan_cfg)

        logging.info("Configure a WLAN with SSID %s on the target station %s" % 
                    (self.wlan_cfg['ssid'], self.target_station.get_ip_addr()))
        self.target_station.cfg_wlan(self.wlan_cfg)

        status, msg = self._verifyAssociatedClient()
        if status == "FAIL":
            return [status, msg]

        # Change policy of ACL to 'deny-all' and verify that the target station can not associate to the wlan
        logging.info("Change policy of the ACL to \'deny-all\'")
        self.testbed.components['ZoneDirector'].edit_acl_rule(old_acl_name = acl_name, is_modified_policy = True)
        self._remove_wlansOnStation()

        logging.info("Configure a WLAN with SSID %s on the target station %s one more time" % 
                    (self.wlan_cfg['ssid'], self.target_station.get_ip_addr()))
        self.target_station.cfg_wlan(self.wlan_cfg)
        status, msg = self._verifyDisassociatedClient()
        if status == "FAIL":
            return [status, msg]

        return ["", ""]

    def _remove_wlansOnStation(self):
        """
        Remove all wlan profiles on the remove station, and verify its status to make sure that it completely
        disconnects from the wireless networks
        """
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

