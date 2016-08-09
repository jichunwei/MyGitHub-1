"""
Description: ZD_GuestAccess_RestrictedSubnet_Enhancement test class verifies the ZD's ability to
             create/modify guest ACL entries and deploy them on the APs

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters:

   Result type: PASS/FAIL
   Results: PASS: if the ACLs can be created/modified/cloned
            FAIL: if any of the steps fails

   Test procedure:
   1. Config:
       - Create a source ACL if the test is about editing/cloning an ACL
   2. Test:
       - Try to create/clone/modify an ACL with given information
   3. Cleanup:
       - Remove all ACL created during the test
"""

import logging
import time
import re

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class ZD_GuestAccess_RestrictedSubnet_Enhancement(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {}


    def config(self, conf):
        self._cfgInitTestParams(conf)
        self._cfgInitTargetStation()
        self._cfgInitZoneDirector()
        self._cfgSetupZoneDirector()
        self._cfgActiveAP()
        self._cfgAssociateStationToWlan()
        self._cfgGetStaWifiIpAddress()
        self._cfgPerformGuestAuth()


    def test(self):
        if self.conf['test_case'] == 'create-acl':
            self._testCreateACLRule()
            if self.errmsg: return("FAIL", self.errmsg)

        if self.conf['test_case'] == 'edit-acl':
            self._testEditACLRule()
            if self.errmsg: return("FAIL", self.errmsg)

        if self.conf['test_case'] == 'clone-acl':
            self._testCloneACLRule()
            if self.errmsg: return("FAIL", self.errmsg)

        if self.conf['test_case'] == 'remove-acl':
            self._testRemoveACLRule()
            if self.errmsg: return("FAIL", self.errmsg)

        if self.conf['test_case'] == 'maximum-acl':
            self._testMaxiumumACLRules()
            if self.errmsg: return("FAIL", self.errmsg)

        if self.conf['test_case'] == 'all-acl':
            self._testAllACLCombinations()
            if self.errmsg: return("FAIL", self.errmsg)

        if self.conf['test_case'] == 'integration':
            self._testIntegration()
            if self.errmsg: return("FAIL", self.errmsg)

        return ("PASS", self.passmsg.strip())


    def cleanup(self):
        self._cfgRemoveAllConfigOnZDAtCleanup()
        self._cfgRestoreToDefaultConfigOnZD()

#
# Config()
#
    def _cfgInitTestParams(self, conf):
        self.conf = dict(ping_timeout_ms = 10000,
                         check_status_timeout = 90,
                         check_wlan_timeout = 45)
        self.conf.update(conf)

        self.current_guest_access_policy = None
        self.current_acl_rules = None

        self.zd = self.testbed.components['ZoneDirector']
        self.sniffer = self.testbed.components['LinuxServer']
        self.sniffing_if = self.sniffer.get_interface_name_by_ip(self.sniffer.ip_addr)

        self.errmsg = ''
        self.passmsg = ''

        self.def_port = '33333'

        # Define guest access policy
        self.guest_access_policy = \
            {'use_guestpass_auth': True,
             'use_tou': True,
             'redirect_url': 'http://www.ruckuswireless.com',
             }

        self.auth_info = \
            {'username': 'local.username',
             'password': 'local.password',
             }

        self.gp_info = \
            {
             'guest_pass': '',
             'use_tou': self.guest_access_policy['use_tou'],
             'redirect_url': self.guest_access_policy['redirect_url'],
             }

        self.dlg_cfg = self._getDefaultDlgConfig()

        # Define the WLAN configuration
        if not self.conf.has_key('wlan_cfg'):
            # Obtain the default open system configuration
            self.conf['wlan_cfg'] = tmethod8.get_default_wlan_cfg()
        self.conf['wlan_cfg']['ssid'] = tmethod.touch_ssid("GUEST-ACL")
        # Make sure it is a Guest WLAN
        self.conf['wlan_cfg']['type'] = "guest"

        self.gp_cfg = \
            {'username': self.auth_info['username'],
             'password': self.auth_info['password'],
             'wlan': self.conf['wlan_cfg']['ssid'],
             'guest_fullname': 'Guest Pass',
             'duration': '5',
             'duration_unit': 'Days',
             'remarks': 'Guest Pass Under Test',
             }

        # Enable tunnel if requested
        if self.conf.has_key('do_tunnel'):
            self.conf['wlan_cfg']['do_tunnel'] = self.conf['do_tunnel']
        # Enable VLAN tagging if requested:
        if self.conf.has_key('vlan_id'):
            self.conf['wlan_cfg']['vlan_id'] = self.conf['vlan_id']

        # Parse the subnet/mask
        if self.conf.has_key('expected_subnet'):
            l = self.conf['expected_subnet'].split("/")
            self.conf['expected_subnet'] = l[0]
            if len(l) == 2:
                self.conf['expected_mask'] = l[1]
            else:
                self.conf['expected_mask'] = ""
        else:
            self.conf['expected_mask'] = ""

        # Define the protocol and port number for the predefined applications in the L3/L4 ACLs
        self.app_2_proto_port = {'HTTP'  : ('6', '80'),
                                 'HTTPS' : ('6', '443'),
                                 'FTP'   : ('6', '21'),
                                 'SSH'   : ('6', '22'),
                                 'TELNET': ('6', '23'),
                                 'SMTP'  : ('6', '25'),
                                 'DNS'   : ('Any', '53'),
                                 'DHCP'  : ('Any', '67'),
                                 'SNMP'  : ('Any', '161')}

        if self.conf['test_case'] == 'maximum-acl':
            if not self.conf.has_key('number_of_acl'):
                raise Exception("Key 'number_of_acl' is not given")

        zd_subnet, zd_mask = utils.get_network_address(self.zd.ip_addr), utils.get_subnet_mask(self.zd.ip_addr)
        self.zdacl = {'order': '1', 'dst_addr': '%s/%s' % (zd_subnet, zd_mask), 'action': 'Deny'}


    def _cfgInitTargetStation(self):
        # Find the target station object and remove all Wlan profiles on it
        self.target_station = tconfig.get_target_station(self.conf['target_station'],
                                                       self.testbed.components['Station'],
                                                       check_status_timeout = self.conf['check_status_timeout'],
                                                       remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])


    def _cfgInitZoneDirector(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        #logging.info("Remove all Guest Passes created on the Zone Director")
        #self.zd.remove_all_guestpasses()

        logging.info("Record current Guest Access Policy on the ZD")
        self.current_guest_access_policy = self.zd.get_guestaccess_policy()

        logging.info("Record current Restricted Subnet entries on the ZD")
        self.current_acl_rules = lib.zd.ga.get_all_restricted_subnet_entries(self.zd)

        logging.info("Remove all Restricted Subnet entries on the ZD")
        lib.zd.ga.remove_all_restricted_subnet_entries(self.zd)


    def _cfgSetupZoneDirector(self):
        logging.info("Configure Guest Access policy on the ZD")
        self.zd.set_guestaccess_policy(**self.guest_access_policy)

        if self.conf['test_case'] != "maximum-acl":
            # This ACL is added just in case the test cases are executed on an L3 test bed.
            # The default ACLs don't deny traffic to the ZD's subnet so the ACL is added
            # to make sure that traffic is denied to ZD's subnet in order to apply the test logic
            # Note that: the test case "maximum-acl" must not be executed on L3 test beds.
            logging.info("Set up the ACL to deny access to the ZD's subnet")
            lib.zd.ga.create_restricted_subnet_entries(self.zd, self.zdacl)

        logging.info("Create a user account used for generating Guest Pass on the ZD")
        self.zd.create_user(self.auth_info['username'], self.auth_info['password'])

        logging.info("Create WLAN [%s] as a Guest WLAN on the ZD" % self.conf['wlan_cfg']['ssid'])
        if self.conf.has_key('vlan_id') and self.conf['vlan_id']:
            logging.info("The WLAN has VLAN tagging enabled with VLANID %s" % self.conf['vlan_id'])
        if self.conf.has_key('do_tunnel'):
            logging.info("The WLAN has tunnel %s" % {True:'enabled', False:'disabled'}[self.conf['do_tunnel']])
        lib.zd.wlan.create_wlan(self.zd, self.conf['wlan_cfg'])
        tmethod8.pause_test_for(3, "Wait for the ZD to push new configuration to the APs")

        self._generate_single_guestpass()


    def _cfgActiveAP(self):
        # Get the Active AP and disable all WLAN interface (non mesh interface) in non active APs
        if self.conf.has_key('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if self.active_ap:
                tmethod.verify_wlan_on_aps(self.active_ap, self.conf['wlan_cfg']['ssid'], self.testbed.components['AP'])
            else:
                raise Exception("Active AP [%s] not found in the test bed" % self.conf['active_ap'])


    def _cfgAssociateStationToWlan(self):
        tmethod.assoc_station_with_ssid(self.target_station, self.conf['wlan_cfg'], self.conf['check_status_timeout'])


    def _cfgGetStaWifiIpAddress(self):
        res, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.conf['check_status_timeout'])
        if not res:
            raise Exception(val2)
        self.sta_wifi_if = {'ip': val1, 'mac': val2.lower()}


    def _cfgPerformGuestAuth(self):
        logging.info("Perform Guest authentication on the target station %s" % self.target_station.get_ip_addr())

        arg = tconfig.get_guest_auth_params(self.zd, self.gp_info['guest_pass'],
                                            self.gp_info['use_tou'], self.gp_info['redirect_url'])
        self.target_station.perform_guest_auth(arg)


    def _generate_single_guestpass(self, guestpass_key = None):
        logging.info("Try to generate a single Guest Pass")
        self.gp_cfg.update({'key': guestpass_key,
                            'dlg_title': self.dlg_cfg['dlg_title'],
                            'dlg_text': self.dlg_cfg['dlg_text_dupgp'] % guestpass_key,
                            'validate_gprints': False,
                       })

        lib.zd.ga._perform_auth_to_generate_guestpass(self.zd, self.gp_cfg['username'], self.gp_cfg['password'])
        lib.zd.ga._generate_single_guestpass(self.zd, **self.gp_cfg)

        logging.debug("Guest pass was generated successfully, %s" % lib.zd.ga.guestpass_info['single_gp'])
        self.gp_info['guest_pass'] = lib.zd.ga.guestpass_info['single_gp']['guest_pass']


    def _getDefaultDlgConfig(self):
        zd_url = self.zd.selenium_mgr.to_url(self.zd.ip_addr, self.zd.https)
        dlg_cfg = {'dlg_title': "The page at %s says:" % zd_url,
                   #'dlg_text_maxgp': "The total number of guest and user accounts reaches maximum allowable size %d" % (self.conf['max_gp_allowable']),
                   'dlg_text_dupgp': 'The key %s already exists. Please enter a different key.',
                   }
        return dlg_cfg

#
# test()
#
    def _testTransmitTraffic(self, acl_rule):
        """
        A helper function used to verify the traffic transmission before and after an ACL is configured
        """
        logging.info("Traffic should be %s" % ("allowed" if acl_rule['action'].lower() == 'allow' else "denied"))
        logging.info("- Start sniffing packets on the Linux PC")
        sniffing_arg_str = tconfig.make_tcp_dump_arg_from_acl(acl_rule)
        if sniffing_arg_str:
            # In case the ACL deals with any kinds of traffic, TCP/UDP port 33333 is used to verify the filter
            if "dst port" not in sniffing_arg_str and "ip proto 1" not in sniffing_arg_str:
                sniffing_arg_str = "%s and dst port %s" % (sniffing_arg_str, self.def_port)
            sniffing_arg_str = "-i %s %s and src host %s" % \
                               (self.sniffing_if, sniffing_arg_str, self.sta_wifi_if['ip'])
        else:
            sniffing_arg_str = "-i %s src host %s and dst port %s" % \
                               (self.sniffing_if, self.sta_wifi_if['ip'], self.def_port)
        logging.debug("Sniffing argument string: %s" % sniffing_arg_str)
        self.sniffer.start_sniffer(sniffing_arg_str)

        logging.info("- Try to transmit traffic from the wireless station")
        addr, app, proto, port = acl_rule['dst_addr'], \
                                 acl_rule['application'], \
                                 acl_rule['protocol'], \
                                 acl_rule['dst_port']
        if addr == 'Any': addr = self.sniffer.ip_addr
        if app not in ['Any', '']: proto, port = self.app_2_proto_port[app]
        if port == 'Any': port = self.def_port
        self.target_station.transmit_traffic(addr, proto, port)

        logging.info("- Verify the sniffer")
        time.sleep(5)
        self.sniffer.stop_sniffer()
        sniff_txt = self.sniffer.read_sniffer(return_as_list = False)
        tcp_pattern = "[\d\-]{10} [\d:]{8}\.[\d]+ IP.*proto TCP \(6\)"
        udp_pattern = "[\d\-]{10} [\d:]{8}\.[\d]+ IP.*proto UDP \(17\)"
        icmp_pattern = "[\d\-]{10} [\d:]{8}\.[\d]+ IP.*proto ICMP \(1\)"

        tcp = re.search(tcp_pattern, sniff_txt, re.M)
        udp = re.search(udp_pattern, sniff_txt, re.M)
        icmp = re.search(icmp_pattern, sniff_txt, re.M)

        if acl_rule['action'].lower() == 'allow':
            if proto == '1' and not icmp:
                self.errmsg = "ICMP traffic was not forwarded to the Linux PC while it was allowed"
                return
            if proto == '6' and not tcp:
                self.errmsg = "TCP traffic was not forwarded to the Linux PC while it was allowed"
                return
            if proto == '17' and not udp:
                self.errmsg = "UDP traffic was not forwarded to the Linux PC while it was allowed"
                return
            if proto == 'Any' and (not tcp or not udp):
                self.errmsg = "TCP/UDP traffic were not forwarded to the Linux PC while they were allowed"
                return
        else:
            if proto == '1' and icmp:
                self.errmsg = "ICMP traffic was forwarded to the Linux PC while it was not allowed"
                return
            if proto == '6' and tcp:
                self.errmsg = "TCP traffic was forwarded to the Linux PC while it was not allowed"
                return
            if proto == '17' and udp:
                self.errmsg = "UDP traffic was forwarded to the Linux PC while it was not allowed"
                return
            if proto == 'Any' and (tcp or udp):
                self.errmsg = "TCP/UDP traffic were forwarded to the Linux PC while they were not allowed"
                return
        logging.info("- Finish sniffing packets")


    def _testCreateACLRule(self):
        # Define the ACL to deal with TCP traffic to port 33333 on the Linux PC
        acl = {'order': '1', 'dst_addr': '%s/32' % self.sniffer.ip_addr,
               'application': 'Any', 'protocol': '6', 'dst_port': self.def_port}

        logging.info("Verify the traffic transmission before creating the ACL")
        acl['action'] = 'Deny'
        self._testTransmitTraffic(acl)
        if self.errmsg: return
        self.passmsg += "TCP traffic to port %s was filtered. " % acl['dst_port']

        # Set up the ACL
        try:
            logging.info("Create the Guest ACL to allow TCP traffic to port %s on the Linux PC" % acl['dst_port'])
            acl['action'] = 'Allow'
            lib.zd.ga.create_restricted_subnet_entries(self.zd, acl)
            tmethod8.pause_test_for(5, "Wait for the ZD to apply the Guest ACL to the APs")
        except Exception, e:
            self.errmsg = "Unable to create the Guest ACL: %s" % e.message
            return
        self.passmsg += "The allow ACL was created successfully. "

        logging.info("Verify the traffic transmission after creating the Guest ACL")
        self._testTransmitTraffic(acl)
        if self.errmsg: return
        self.passmsg += "TCP traffic to port %s was allowed. " % acl['dst_port']


    def _testEditACLRule(self):
        # Define the ACL to deal with TCP/UDP traffic to port 33333 on the Linux PC
        acl_1 = {'order': '1', 'dst_addr': '%s/32' % self.sniffer.ip_addr, 'action': 'Deny',
                 'application': 'Any', 'protocol': 'Any', 'dst_port': self.def_port}
        # Define the ACL to deal with TCP traffic only
        acl_2 = acl_1.copy()
        acl_2['protocol'] = '6'
        # Define the ACL to deal with UDP traffic only
        acl_3 = acl_1.copy()
        acl_3['protocol'] = '17'

        logging.info("Verify the traffic transmission before creating the ACL")
        # This should deny both TCP/UDP
        self._testTransmitTraffic(acl_1)
        if self.errmsg: return
        self.passmsg += "Traffic to port %s was filtered. " % acl_1['dst_port']

        # Set up the ACL to allow TCP traffic to port 33333 on the Linux PC
        logging.info("Create a Guest ACL to allow TCP traffic to port %s on the Linux PC" % acl_2['dst_port'])
        acl_2['action'] = 'Allow'
        lib.zd.ga.create_restricted_subnet_entries(self.zd, acl_2)
        tmethod8.pause_test_for(5, "Wait for the ZD to apply the Guest ACL to the APs")
        self.passmsg += "The ACL to allow TCP/%s traffic was created. " % acl_2['dst_port']

        logging.info("Verify the traffic transmission after creating the ACL")
        # This should allow TCP traffic
        self._testTransmitTraffic(acl_2)
        if self.errmsg: return
        self.passmsg += "TCP traffic to port %s was allowed. " % acl_2['dst_port']
        # This should deny UDP traffic
        self._testTransmitTraffic(acl_3)
        self.passmsg += "UDP traffic to port %s was still filtered. " % acl_3['dst_port']
        if self.errmsg: return

        # Edit the ACL to allow only UDP traffic
        logging.info("Edit the ACL [%s] to allow only UDP traffic" % acl_2['order'])
        edited_info = {'protocol': '17'}
        lib.zd.ga.edit_restricted_subnet_entry(self.zd, edited_info, order = acl_2['order'])
        tmethod8.pause_test_for(5, "Wait for the ZD to apply the modified Guest ACL to the APs")
        self.passmsg += "The ACL was updated to allow only UDP/%s traffic. " % acl_3['dst_port']

        logging.info("Verify the traffic transmission after creating the ACL")
        # This should deny TCP traffic
        acl_2['action'] = 'Deny'
        self._testTransmitTraffic(acl_2)
        if self.errmsg: return
        self.passmsg += "TCP traffic to port %s was denied. " % acl_2['dst_port']
        # This should allow UDP traffic
        acl_3['action'] = 'Allow'
        self._testTransmitTraffic(acl_3)
        if self.errmsg: return
        self.passmsg += "UDP traffic to port %s was allowed. " % acl_3['dst_port']


    def _testCloneACLRule(self):
        # Define the ACL to deal with TCP/UDP traffic to port 33333 on the Linux PC
        acl_1 = {'order': '1', 'dst_addr': '%s/32' % self.sniffer.ip_addr, 'action': 'Deny',
                 'application': 'Any', 'protocol': 'Any', 'dst_port': self.def_port}
        # Define the ACL to deal with TCP traffic only
        acl_2 = acl_1.copy()
        acl_2['protocol'] = '6'
        # Define the ACL to deal with UDP traffic only
        acl_3 = acl_1.copy()
        acl_3['protocol'] = '17'

        logging.info("Verify the traffic transmission before creating the ACL")
        # This should deny both TCP/UDP
        self._testTransmitTraffic(acl_1)
        if self.errmsg: return
        self.passmsg += "Traffic to port %s was filtered. " % acl_1['dst_port']

        # Set up the ACL to allow TCP traffic to port 33333 on the Linux PC
        logging.info("Create a Guest ACL to allow TCP traffic to port %s on the Linux PC" % acl_2['dst_port'])
        acl_2['action'] = 'Allow'
        lib.zd.ga.create_restricted_subnet_entries(self.zd, acl_2)
        tmethod8.pause_test_for(5, "Wait for the ZD to apply the Guest ACL to the APs")
        self.passmsg += "The ACL to allow TCP/%s traffic was created. " % acl_2['dst_port']

        logging.info("Verify the traffic transmission after creating the ACL")
        # This should allow TCP traffic
        self._testTransmitTraffic(acl_2)
        if self.errmsg: return
        self.passmsg += "TCP traffic to port %s was allowed. " % acl_2['dst_port']
        # This should deny UDP traffic
        self._testTransmitTraffic(acl_3)
        self.passmsg += "UDP traffic to port %s was still filtered. " % acl_3['dst_port']
        if self.errmsg: return

        # Clone to make a new allow ACL
        logging.info("Clone the ACL [%s] to make a new ACL that allows UDP traffic" % acl_2['order'])
        cloned_info = {'protocol': '17', 'order': '1'}
        lib.zd.ga.clone_restricted_subnet_entry(self.zd, cloned_info, order = acl_2['order'])
        tmethod8.pause_test_for(5, "Wait for the ZD to apply the newly cloned Guest ACL to the APs")
        self.passmsg += "The ACL to allow UDP/%s traffic was created. " % acl_3['dst_port']

        logging.info("Verify the traffic transmission after creating the ACL")
        # This should allow both TCP and UDP traffic
        acl_1['action'] = 'Allow'
        self._testTransmitTraffic(acl_1)
        if self.errmsg: return
        self.passmsg += "TCP/UDP traffic to port %s was allowed. " % acl_1['dst_port']


    def _testRemoveACLRule(self):
        # Define the ACL to deal with TCP traffic to port 33333 on the Linux PC
        acl = {'order': '1', 'dst_addr': '%s/32' % self.sniffer.ip_addr, 'action': 'Deny',
               'application': 'Any', 'protocol': '6', 'dst_port': self.def_port}

        logging.info("Verify the traffic transmission before creating the ACL")
        # This should deny TCP
        self._testTransmitTraffic(acl)
        if self.errmsg: return
        self.passmsg += "Traffic to port %s was filtered. " % acl['dst_port']

        # Set up the ACL to allow TCP traffic to port 33333 on the Linux PC
        logging.info("Create a Guest ACL to allow TCP traffic to port %s on the Linux PC" % acl['dst_port'])
        acl['action'] = 'Allow'
        lib.zd.ga.create_restricted_subnet_entries(self.zd, acl)
        tmethod8.pause_test_for(5, "Wait for the ZD to apply the Guest ACL to the APs")
        self.passmsg += "The ACL to allow TCP/%s traffic was created. " % acl['dst_port']

        logging.info("Verify the traffic transmission after creating the ACL")
        # This should allow TCP traffic
        self._testTransmitTraffic(acl)
        if self.errmsg: return
        self.passmsg += "TCP traffic to port %s was allowed. " % acl['dst_port']

        # Remove the ACL
        logging.info("Remove the ACL [%s]" % acl['order'])
        lib.zd.ga.remove_restricted_subnet_entry(self.zd, order = acl['order'])
        tmethod8.pause_test_for(5, "Wait for the ZD to apply the newly cloned Guest ACL to the APs")
        self.passmsg += "The ACL was removed successfully. "

        logging.info("Verify the traffic transmission after creating the ACL")
        # This should deny TCP traffic
        acl['action'] = 'Deny'
        self._testTransmitTraffic(acl)
        if self.errmsg: return
        self.passmsg += "TCP traffic to port %s was denied again. " % acl['dst_port']


    def _testMaxiumumACLRules(self):
        # Define the ACL to deal with UDP traffic to the Linux PC
        sample_acl = {'order': '1', 'dst_addr': '%s/32' % self.sniffer.ip_addr, 'action': 'Deny',
                      'application': 'Any', 'protocol': '17'}

        # Define the ACL set
        acl_list = []
        for i in range(self.conf['number_of_acl']):
            x = sample_acl.copy()
            x['dst_port'] = str(int(self.def_port) + i)
            acl_list.append(x)

        logging.info("Verify the traffic transmission before creating the ACLs")
        for acl in acl_list:
            # This should deny the traffic
            self._testTransmitTraffic(acl)
            if self.errmsg: return
        self.passmsg += "UDP traffic was initially filtered. "

        # Create the ACLs
        try:
            logging.info("Create %s Guest ACL entries to allow UDP traffic to the Linux PC" % self.conf['number_of_acl'])
            for acl in acl_list:
                acl['action'] = 'Allow'
            lib.zd.ga.create_restricted_subnet_entries(self.zd, acl_list)
        except Exception, e:
            self.errmsg = "Unable to create %s Guest ACL rules: %s" % (self.conf['number_of_acl'], e.message)
            return
        self.passmsg += "%s Guest ACL entries were created successfully. " % self.conf['number_of_acl']

        # Try creating one more ACL
        try:
            logging.info("Try creating one more Guest ACL entry")
            lib.zd.ga.create_restricted_subnet_entries(self.zd, acl_list[0])
            self.errmsg = "The ZD did allow creating more than %s Guest ACL entries" % self.conf['number_of_acl']
            return
        except Exception, e:
            logging.info("Catch the exception [%s] when trying creating one more ACL" % e.message)
            self.passmsg += "The ZD didn't allow creating more than %s Guest ACL entries. " % self.conf['number_of_acl']

        tmethod8.pause_test_for(5, "Wait for the ZD to apply the Guest ACL to the APs")

        logging.info("Verify the traffic transmission after creating the ACL")
        for acl in acl_list:
            # This should allow UDP traffic
            self._testTransmitTraffic(acl)
            if self.errmsg: return
        self.passmsg += "UDP traffic was allowed after all. "


    def _testAllACLCombinations(self):
        if self.conf['test_case'] != 'all-acl': return

        # Get the acl combination definitions
        dst_ip_mask = '%s/32' % self.sniffer.ip_addr
        acl_list = tconfig.generate_l3_l4_rule_set(dst_ip_mask, self.def_port)

        for acl in acl_list:
            logging.info("Verify the ACL <<< %s >>>" % acl)

            if acl['application'] in ['DNS', 'DHCP'] or acl['dst_port'] in ['53', '67']:
                logging.info("The ACL is not verified because this type of traffic is always allowed by the ZD")
                continue

            logging.info("Verify the traffic transmission before creating the ACL")
            acl['action'] = 'Deny'
            self._testTransmitTraffic(acl)
            if self.errmsg: return

            # Set up the ACL
            try:
                logging.info("Create the Guest ACL")
                acl['order'] = '1'
                acl['action'] = 'Allow'
                lib.zd.ga.create_restricted_subnet_entries(self.zd, acl)
                tmethod8.pause_test_for(5, "Wait for the ZD to apply the Guest ACL to the APs")
            except Exception, e:
                self.errmsg = "Unable to create the Guest ACL: %s" % e.message
                return

            logging.info("Verify the traffic transmission after creating the Guest ACL")
            self._testTransmitTraffic(acl)
            if self.errmsg: return

            logging.info("Remove the ACL")
            lib.zd.ga.remove_restricted_subnet_entry(self.zd, order = acl['order'])

        self.passmsg += "All the Guest ACL combinations have been verified successfully. "


    def _testIntegration(self):
        if self.conf['expected_subnet']:
            logging.info("Verify the subnet address of the wireless station")
            net_addr = utils.get_network_address(self.sta_wifi_if['ip'], self.conf['expected_mask'])
            if self.conf['expected_subnet'] != net_addr:
                self.errmsg = "The leased IP address was [%s], which is not in the expected subnet [%s]" % \
                              (self.sta_wifi_if['ip'], self.conf['expected_subnet'])
                return

        self._testEditACLRule()

#
# cleanup()
#
    def _cfgRemoveAllConfigOnZDAtCleanup(self):
        logging.info("Remove all the WLANs on the Zone Director")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)

        logging.info("Remove all Guest Passes created on the Zone Director")
        self.zd.remove_all_guestpasses()

        logging.info("Try to remove all the created Guest ACLs")
        lib.zd.ga.remove_all_restricted_subnet_entries(self.zd)


    def _cfgRestoreToDefaultConfigOnZD(self):
        if self.current_guest_access_policy:
            logging.info("Restore Guest Access Policy to original configuration on the ZD")
            self.zd.set_guestaccess_policy(**self.current_guest_access_policy)

        if self.current_acl_rules:
            logging.info("Restore Guest Access restricted subnet entries on the ZD")
            lib.zd.ga.create_restricted_subnet_entries(self.zd, self.current_acl_rules)

