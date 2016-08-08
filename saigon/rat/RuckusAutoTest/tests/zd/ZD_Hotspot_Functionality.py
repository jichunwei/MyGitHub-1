"""
Description: ZD_Hotspot_Functionality test class tests the ability of the ZD to
             deploy a Hotspot WLAN with different configuration

Prerequisite (Assumptions about the state of the testbed/DUT):
1. Build under test is loaded on the AP and Zone Director

Required components: 'Station', 'RuckusAP', 'ZoneDirector'
Test parameters:
    target_ip:
        IP address of a available destination which is used to verify the
        connectivity of the wireless station
    active_ap:
        Symbolic name of the active AP - optional
    target_station:
        IP address of target wireless station
    hotspot_cfg:
        Configuration of a Hotspot profile given as a dictionary, refer to the
        module hotspot_services_zd to find the configuration keys of a Hotspot profile
        
        The script verifies only keys that are specified in this dictionary structure
    wlan_cfg:
        Association parameters, given as a dictionary - optional
    auth_info:
        Information about the authentication method, given as a dictionary
        Refer to module aaa_servers_zd to find the keys to define a specific
        authentication server
        In case of RADIUS server, if the user account has Session-Timeout/
        Idle-Timeout attribute set, they are also defined in this structure
        so that the script can verify them
    acct_info:
        Information about the accounting server, given as a dictionary - optional
    vlan_id:
        Enable VLAN tagging on the WLAN with given VLAN ID
    do_tunnel:
        Enable tunnelling on the WLAN
    number_of_profile:
        State the number of the Hotspot profiles will be created, optional
    acl_integration:
        True/False to enable integration test with L2 ACL, optional

   Result type: PASS/FAIL
   Results:
       PASS: target station can associate to the WLAN, ping to a destination
             successfully and information is shown correctly in ZD
        FAIL: if one of the above criteria is not satisfied

   Messages: If FAIL the test script returns a message related to the criterion
             that is not satisfied

   Test procedure:
   1. Config:
       - Remove all WLAN configuration on the target station
       - Remove all configuration about WLANs, users, authentication servers,
         and active clients on the ZD
   2. Test:
       - Create the authentication server/accounting server/local user account on the ZD
       - Create the Hotspot profile with given configuration
       - Create a Hotspot WLAN using the profile created above
       - Verify the status of the WLAN on the active AP and turn off the
         WLAN on other APs
       - If the restricted subnets/walled garden entries are defined in the
         Hotspot profile access to the Linux shell of the ZD/AP, read the proc
         file at /proc/afmod/policy and verify the entries
       - Configure the wireless station to associate to the Hotspot WLAN
       - Get the IP address of the wireless adapter on the wireless station
       - Verify the connectivity from the wireless station before it is authenticated
       - Verify the status of the station on the ZD before it is authenticated
       - Perform Hotspot authentication on the wireless station
       - Verify the connectivity from the wireless station after it is authenticated
       - Verify the status of the station on the ZD after it is authenticated
       - If accounting server is specified, start the sniffer on the Radius server,
         wait for a few update intervals, read the capture and verify the update
         interval and the attributes in the packets
       - If Session-Timeout is defined on the server or in the Hotspot profile,
         wait for a period that is longer than the configured value, verify the
         connectivity of the station, and verify the status of the station shown
         on the ZD
       - If Idle-Timeout is defined on the server or in the Hotspot profile
         and the test is to validate before the timer expired, disconnect the
         station from the WLAN, wait for a period that is about a half of the
         configured value, re-associate the station to the WLAN, verify its
         connectivity and status shown on the ZD. If the test is to validate
         after the timer expired, wait for a period that is about one and
         a half of the configured value, then repeat the same verification.
       - If the logout URL is specified in the hotspot profile, access to the
         URL on the station, then verify its connectivity and status shown on the ZD.
   3. Cleanup:
       - Remove all configuration created on the ZD
       - Remove wireless profile on wireless station
"""

import logging
import re
import time
import copy

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components import ZoneDirectorCLI
from RuckusAutoTest.common import Ratutils as utils

class ZD_Hotspot_Functionality(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
        'target_ip':
            'IP address to test connectivity',
        'active_ap':
            'Symbolic name of the active AP - optional',
        'target_station':
            'IP address of target station',
        'hotspot_cfg':
            'Configuration of a Hotspot profile given as a dictionary',
        'wlan_cfg':
            'Association parameters, given as a dictionary, optional',
        'auth_info':
            'Information about the authentication method, given as a dictionary',
        'acct_info':
            'Information about the accounting server, given as a dictionary, optional',
        'vlan_id':
            'Enable VLAN tagging on the WLAN with given VLAN ID',
        'do_tunnel':
            'Enable tunnelling on the WLAN',
        'number_of_profile':
            'State the number of the Hotspot profiles will be created, optional',
        'acl_integration':
            'True/False to enable integration test with L2 ACL, optional'
    }

    def config(self, conf):
        self._cfgInitTestParams(conf)
        self._cfgRemoveAllConfigOnZD()
        self._cfgGetTargetStation()
        self._cfgGetActiveAP()
        self._cfgCreateZDCLI()

    def test(self):
#Chico@2014-06-24, add timeout looping to tolerance some instability ZF-8847
        CR_timeout = 45
        t0 = time.time()
        while True:
            if (time.time() - t0) < CR_timeout:
                try:
                    self._cfgDefineAuthSourceOnZD()
                    logging.info("Auth server created successfully this time")
                    break
                except Exception, e:
                    logging.error("Retry after 5 seconds because of received exception %s" % e.message)
                    self.zd.refresh()
                    time.sleep(5)
            else:
                raise Exception("%sseconds timeout and hotspot auth still failed" % CR_timeout)
 #Chico@2014-06-24, add timeout looping to tolerance some instability ZF-8847
        

        self._testCreateHotspotProfileOnZD()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._cfgCreateWlanOnZD()

        self._testVerifyWlanOnAPs()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._testACLOnZDLinuxShell()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._testACLOnAPLinuxShell()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._testAssociateStationToWlan()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._cfgGetStaWifiIpAddress()

        self._testVerifyStationInfoOnZDBeforeHotspotAuth()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._testStationConnectivityBeforeHotspotAuth()
        if self.errmsg: return ("FAIL", self.errmsg)

 #Chico@2014-06-24, add timeout looping to tolerance some instability ZF-8847
        HS_timeout = 120
        t0 = time.time()
        while True:
            if (time.time() - t0) < HS_timeout:
                try:
                    self._cfgPerformHotspotAuthOnStation()
                    logging.info("Auth by hotspot succeed this time")
                    break
                except:
                    logging.info("Failed to auth by hotspot this time and try again 5 seconds later")
                    time.sleep(5)
            else:
                raise Exception("%sseconds timeout and hotspot auth still failed" % HS_timeout)
 #Chico@2014-06-24, add timeout looping to tolerance some instability ZF-8847


        self._testVerifyStationInfoOnZDAfterHotspotAuth()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._testStationConnectivityAfterHotspotAuth()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._testRadiusAccouting()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._testSessionTimeout()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._testIdleTimeout()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._testUAMRedirectedURL()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._testIntegration()
        if self.errmsg: return ("FAIL", self.errmsg)

        return ("PASS", self.msg.strip())

    def cleanup(self):
        self._cfgRemoveAllConfigOnZDAtCleanup()
        self._cfgRemoveWlanFromStation()
        self._cfgStopSnifferOnLinuxPC()

#
# Config()
#
    def _cfgInitTestParams(self, conf):
        self.conf = dict(ping_timeout_ms = 10000,
                         check_status_timeout = 90,
                         check_wlan_timeout = 45)
        self.conf.update(conf)

        self.target_station = None
        self.zd = self.testbed.components['ZoneDirector']
        self.sniffer = self.testbed.components['LinuxServer']

        if not self.conf.has_key('wlan_cfg'):
            # Obtain the default open system configuration
            self.conf['wlan_cfg'] = tmethod8.get_default_wlan_cfg()

        self.conf['wlan_cfg']['ssid'] = tmethod.touch_ssid("WISPr-WLAN-UNDER-TEST")
        self.conf['wlan_cfg']['type'] = "hotspot"

        # Enable tunnel if requested
        if self.conf.has_key('do_tunnel'):
            self.conf['wlan_cfg']['do_tunnel'] = self.conf['do_tunnel']

        # Enable VLAN tagging if requested:
        if self.conf.has_key('vlan_id'):
            self.conf['wlan_cfg']['vlan_id'] = self.conf['vlan_id']

        # Define the L2 ACL if required
        if self.conf.has_key('acl_integration') and self.conf['acl_integration']:
            self.conf['acl_cfg'] = {'acl_name': 'The wireless client ACL'}
            self.conf['wlan_cfg']['acl_name'] = self.conf['acl_cfg']['acl_name']

        else:
            self.conf['acl_cfg'] = None

        # Parse the subnet/mask
        if self.conf.has_key('expected_subnet'):
            l = self.conf['expected_subnet'].split("/")
            self.conf['expected_subnet'] = l[0]
            if len(l) == 2:
                self.conf['expected_mask'] = l[1]
            else:
                self.conf['expected_mask'] = ""
        else:
            self.conf['expected_subnet'] = ""
            self.conf['expected_mask'] = ""

        # Hotspot configuration must be provided
        if not self.conf.has_key('hotspot_cfg'):
            raise Exception('Hotspot configuration was not given')

        # Give it a name if not given
        if not self.conf['hotspot_cfg'].has_key('name'):
            self.conf['hotspot_cfg']['name'] = "WISPr Profile Under Test"

        # Assign the profile to the WLAN
        self.conf['wlan_cfg']['hotspot_profile'] = self.conf['hotspot_cfg']['name']

        # Auth information must be provided
        if not self.conf.has_key('auth_info'):
            raise Exception('Authentication configuration was not given')

        # Give the auth server a name, and assign it to the hotspot profile
        if self.conf['auth_info']['type'] != "local":
            self.conf['auth_info']['svr_name'] = "Authentication Server"
            self.conf['hotspot_cfg']['auth_svr'] = self.conf['auth_info']['svr_name']

        else:
            # If there is not any auth server, the local database is used
            self.conf['hotspot_cfg']['auth_svr'] = "Local Database"

        # Give the accounting server a name, and assign it to the hotspot profile
        if self.conf.has_key('acct_info'):
            self.conf['acct_info']['svr_name'] = "Accounting Server"
            self.conf['hotspot_cfg']['acct_svr'] = self.conf['acct_info']['svr_name']

        # In case the Location ID or the Location Name is defined but the update
        # frequency is not specified
        # Set it to 2 minutes to shorten the testing time
        if self.conf['hotspot_cfg'].has_key('radius_location_id') or \
           self.conf['hotspot_cfg'].has_key('radius_location_name'):
            if not self.conf['hotspot_cfg'].has_key('interim_update_interval'):
                self.conf['hotspot_cfg']['interim_update_interval'] = "2"

        # Obtain the domain name server of the test bed
        # It is used to resolve names in the walled garden related tests
        if self.conf['hotspot_cfg'].has_key('walled_garden_list'):
            logging.info("Get the DNS server address configured on the ZD")
            zd_ip_cfg = self.zd.get_ip_cfg()
            if not zd_ip_cfg['pri_dns']:
                msg = "The ZD does not have information of the DNS server. "\
                      "It cannot resolve names in walled garden entries."
                raise Exception(msg)
            self.dns_server_addr = zd_ip_cfg['pri_dns']

        if self.conf['hotspot_cfg'].has_key('idle_timeout'):
            if not self.conf.has_key('relogin_before_timer_expired'):
                raise Exception("Key 'relogin_before_timer_expired' not found")

        # Clone to many profiles if required
        if self.conf.has_key('number_of_profile'):
            self.conf['hotspot_cfg_list'] = [self.conf['hotspot_cfg']]
            for i in range(int(self.conf['number_of_profile']) - 1):
                new_cfg = copy.deepcopy(self.conf['hotspot_cfg'])
                new_cfg['name'] = "%s-%s" % (new_cfg['name'], i + 2)
                self.conf['hotspot_cfg_list'].append(new_cfg)

        self.errmsg = ""
        self.msg = ""
        self.wlan_id = None
        self.sta_wifi_if = None

    def _cfgRemoveAllConfigOnZD(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        #lib.zd.wispr.remove_all_profiles(self.zd)
        #lib.zd.ac.delete_all_l2_acl_policies(self.zd)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)

    def _cfgGetTargetStation(self):
        logging.info("Find the target station on the test bed")
        self.target_station = tconfig.get_target_station(
                                  self.conf['target_station'],
                                  self.testbed.components['Station'],
                                  check_status_timeout = self.conf['check_status_timeout'],
                                  remove_all_wlan = True)

        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

        if self.conf['acl_cfg']:
            ip, mac = self.target_station.get_wifi_addresses()
            if not mac:
                raise Exception("Unable to get the MAC address of the wireless"
                                " adapter of the wireless station")

            self.sta_wifi_if = {'mac':mac}

    def _cfgGetActiveAP(self):
        if self.conf.has_key('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed,
                                                           self.conf['active_ap'])
            if not self.active_ap:
                raise Exception("Active AP [%s] not found in the test bed" %
                                self.conf['active_ap'])

    def _cfgCreateZDCLI(self):
        if self.conf['hotspot_cfg'].has_key('restricted_subnet_list') or \
        self.conf['hotspot_cfg'].has_key('walled_garden_list'):
            #zd_cli_cfg = {'ip_addr':self.zd.ip_addr,
            #              'username':self.zd.username,
            #              'password':self.zd.password}
            #self.zd_cli = ZoneDirectorCLI.ZoneDirectorCLI(zd_cli_cfg)
            #Updated by cwang@2012/8/21
            self.zd_cli = self.testbed.components['ZoneDirectorCLI']
#
# test()
#
    def _cfgDefineAuthSourceOnZD(self):
        if self.conf['auth_info']['type'] == 'local':
            logging.info("Create a user account on the ZoneDirector")
            self.zd.create_user(self.conf['auth_info']['username'],
                                self.conf['auth_info']['password'])

        else:
            logging.info("Create an authentication server on the ZoneDirector")
            server_info = {'server_addr': self.conf['auth_info']['svr_addr'],
                           'server_port': self.conf['auth_info']['svr_port'],
                           'server_name': self.conf['auth_info']['svr_name']}

            if self.conf['auth_info']['type'] == 'ad':
                server_info['win_domain_name'] = self.conf['auth_info']['svr_info']

            elif self.conf['auth_info']['type'] == 'ldap':
                server_info['ldap_search_base'] = self.conf['auth_info']['svr_info']

            elif self.conf['auth_info']['type'] == 'radius':
                server_info['radius_auth_secret'] = self.conf['auth_info']['svr_info']

            lib.zd.aaa.create_server(self.zd, **server_info)

        # Create radius accouting server if required
        if self.conf.has_key('acct_info'):
            logging.info("Create an accounting server on the ZoneDirector")
            server_info = {'server_addr': self.conf['acct_info']['svr_addr'],
                           'server_port': self.conf['acct_info']['svr_port'],
                           'server_name': self.conf['acct_info']['svr_name'],
                           'radius_acct_secret': self.conf['acct_info']['svr_info']}

            lib.zd.aaa.create_server(self.zd, **server_info)


    def _testCreateHotspotProfileOnZD(self):
        if self.conf.has_key('hotspot_cfg_list'):
            try:
                logging.info("Try to create %s Hotspot profiles" %
                             self.conf['number_of_profile'])

                for cfg in self.conf['hotspot_cfg_list']:
                    logging.info("Create a Hotspot profile [%s] on the "
                                 "ZoneDirector" % cfg['name'])
                    lib.zd.wispr.create_profile(self.zd, **cfg)
                    time.sleep(2)

                self.msg += "%s Hotspot profiles have been created successfully. " \
                            % self.conf['number_of_profile']

            except:
                self.errmsg = "Unable to create %s Hotspot profiles" \
                              % self.conf['number_of_profile']

                return

            try:
                logging.info("Try to create one more Hotspot profile")
                cfg = copy.deepcopy(self.conf['hotspot_cfg'])
                cfg['name'] = "%s-extra" % cfg['name']
                lib.zd.wispr.create_profile(self.zd, **cfg)
                self.errmsg = "The ZD did allow creating more than " \
                              "%s Hotspot profiles" % self.conf['number_of_profile']

            except:
                self.msg += "The ZD didn't allow creating more than "\
                            "%s Hotspot profiles. " % self.conf['number_of_profile']

        else:
            logging.info("Create a Hotspot profile [%s] on the ZoneDirector" %
                         self.conf['hotspot_cfg']['name'])

            lib.zd.wispr.create_profile(self.zd, **self.conf['hotspot_cfg'])


    def _cfgCreateWlanOnZD(self):
        if self.conf['acl_cfg']:
            logging.info("Create an L2 ACL [%s] on the ZD" %
                         self.conf['acl_cfg']['acl_name'])
            lib.zd.ac.create_l2_acl_policy(self.zd, self.conf['acl_cfg'])

        logging.info("Create WLAN [%s] as a Hotspot WLAN on the Zone Director" %
                     self.conf['wlan_cfg']['ssid'])

        if self.conf['wlan_cfg'].has_key('vlan_id') \
        and self.conf['wlan_cfg']['vlan_id']:
            logging.info("The WLAN has VLAN tagging enabled with VLANID %s" %
                         self.conf['wlan_cfg']['vlan_id'])

        if self.conf['wlan_cfg'].has_key('do_tunnel'):
            logging.info("The WLAN has tunnel %s" %
                         {True:'enabled', False:'disabled'}
                         [self.conf['wlan_cfg']['do_tunnel']])

        if self.conf['wlan_cfg'].has_key('acl_name'):
            logging.info("The WLAN set L2 ACL [%s]" %
                         self.conf['wlan_cfg']['acl_name'])

        lib.zd.wlan.create_wlan(self.zd, self.conf['wlan_cfg'])
        tmethod8.pause_test_for(3, "Wait for the ZD to push new configuration to the APs")


    def _testVerifyWlanOnAPs(self):
        if self.conf.has_key('active_ap'):
            self.errmsg = tmethod.verify_wlan_on_aps(self.active_ap,
                                                     self.conf['wlan_cfg']['ssid'],
                                                     self.testbed.components['AP'])
            if not self.errmsg:
                self.msg += "The WLAN has been deployed on the AP [%s] successfully. " \
                % self.active_ap.base_mac_addr

    def _parseWalledGardenEntry(self, subnet, resolve_name = True):
        entry_re = re.compile("^([\w\-\.]+):?([\d]*)/?([\d]*)$")
        ip_re = re.compile("^[\d\.]+$")
        m = entry_re.match(subnet)
        if m:
            ip = m.group(1)
            port = m.group(2)
            mask = m.group(3)

        else:
            raise Exception("Invalid walled garden entry [%s]" % subnet)

        if not ip_re.match(ip) and resolve_name:
            ip = utils.lookup_domain_name(ip, self.dns_server_addr)

        if not mask:
            mask = "32"

        return (ip, port, mask)

    def _testACLOnZDLinuxShell(self):
        # Verify if the ACL has been applied in the ZD's Linux shell
        # This test is performed when the restricted subnets or walled garden
        # targets are configured

        if self.conf['hotspot_cfg'].has_key('restricted_subnet_list'):
            logging.info("Verify the Access Policy stored in the ZD's Linux shell "
                         "in /proc/afmod/policy")

            self.wlan_id = self.zd_cli.get_wlan_id(self.conf['wlan_cfg']['ssid'])

            acl_list = self.zd_cli.get_hotspot_policy(self.wlan_id,
                                                      access_policy = True)

            matched = False
            for subnet in self.conf['hotspot_cfg']['restricted_subnet_list']:
                logging.info("Verify entry [%s]" % subnet)

                if type(subnet) is dict:
                    descmp = []
                    if subnet['protocol'] == 'Any':
                        descmp.append('255')
                    else:
                        descmp.append(subnet['protocol'])

                    descmp.append(subnet['destination_addr'])

                    if subnet['destination_port'] == 'Any':
                        descmp.append('0')
                    else:
                        descmp.append(subnet['destination_port'])

                    if subnet['action'] == 'Deny':
                        descmp.append('Block')
                    elif subnet['action'] == 'Allow':
                        descmp.append('Pass')

                else:
                    descmp = subnet

                for acl in acl_list:
                    if type(subnet) is dict:
                        srccmp = [acl['proto'], acl['dst-addr'],
                                  acl['dport'], acl['action']]
                    else:
                        srccmp = acl['dst-addr']

                    if srccmp == descmp:
                        matched = True
                        break

                if not matched:
                    self.errmsg = "Not found in the ZD's Linux shell an ACL entry " \
                                  "matched with the restricted subnet [%s]" % subnet
                    return


            self.msg += "All the restricted subnet entries have been applied on "\
                        "the ZD successfully. "


        if self.conf['hotspot_cfg'].has_key('walled_garden_list'):
            logging.info("Verify the Redirect Policy stored in the ZD's Linux shell "
                         "in /proc/afmod/policy")
            time.sleep(20)
            if not self.wlan_id:
                self.wlan_id = self.zd_cli.get_wlan_id(self.conf['wlan_cfg']['ssid'])

            acl_list = self.zd_cli.get_hotspot_policy(self.wlan_id, redir_policy = True)

            for entry in self.conf['hotspot_cfg']['walled_garden_list']:
                logging.info("Verify entry [%s]" % entry)
                ip, port, mask = self._parseWalledGardenEntry(entry, resolve_name = False)
                logging.info("IP:[%s] - port[%s] - mask[%s]" % (ip, port, mask))
                dst_addr = "%s/%s" % (ip, mask)
                t1 = time.time()
                duration = 0
                while True:
                    timedout = duration > self.conf['check_wlan_timeout']
                    match = [acl for acl in acl_list if acl['dst-addr'] == dst_addr]
                    if not match and not timedout:
                        time.sleep(5)
                        acl_list = self.zd_cli.get_hotspot_policy(self.wlan_id,
                                                                  redir_policy = True)

                    else:
                        break

                    duration = time.time() - t1

                logging.info("It took %s seconds for the ZD to apply "
                             "the entry [%s]" % (duration, entry))
                if not match:
                    self.errmsg = "Not found in the ZD's Linux shell an "\
                                  "ACL entry for the walled garden entry [%s]" % entry
                    return

                if match[0]['action'] != "Pass":
                    self.errmsg = "The ACL entry [%s] has the action [%s] " \
                                  "instead of [Pass]" % (entry, match[0]['action'])
                    return

                if port and match[0]['dport'] != port:
                    self.errmsg = "The ACL entry [%s] has the port [%s] " \
                                  "instead of [%s]" % (entry, match[0]['dport'], port)
                    return

    #JLIN@20100611 modified for comparing restricted_subnet logical error
    def _testACLOnAPLinuxShell(self):
        # Verify if the ACL has been applied in the AP's Linux shell
        # This test is performed when the restricted subnets or walled garden
        # targets are configured
        if self.conf['hotspot_cfg'].has_key('restricted_subnet_list'):
            # If an active AP is not specified, verify the ACL in all AP
            if self.conf.has_key('active_ap'):
                ap_list = [self.active_ap]

            else:
                ap_list = self.testbed.components['AP']

            for ap in ap_list:
                logging.info("Verify the ACL list stored in the AP[%s]'s "\
                             "Linux shell in /proc/afmod/policy" \
                             % ap.base_mac_addr)

                acl_list = ap.get_hotspot_policy(self.wlan_id,
                                                 access_policy = True)

                matched = False
                for subnet in self.conf['hotspot_cfg']['restricted_subnet_list']:
                    logging.info("Verify entry [%s]" % subnet)

                    if type(subnet) is dict:
                        descmp = []
                        if subnet['protocol'] == 'Any':
                            descmp.append('255')
                        else:
                            descmp.append(subnet['protocol'])

                        descmp.append(subnet['destination_addr'])

                        if subnet['destination_port'] == 'Any':
                            descmp.append('0')
                        else:
                            descmp.append(subnet['destination_port'])

                        if subnet['action'] == 'Deny':
                            descmp.append('Block')
                        elif subnet['action'] == 'Allow':
                            descmp.append('Pass')
                    else:
                        descmp = subnet

                    for acl in acl_list:
                        if type(subnet) is dict:
                            srccmp = [acl['proto'], acl['dst-addr'],
                                      acl['dport'], acl['action']]
                        else:
                            srccmp = acl['dst-addr']
                        if srccmp == descmp:
                            matched = True
                            logging.debug("found subnet[%s] was shown on AP[%s] shell" % (subnet, self.active_ap.get_base_mac()))
                            break

                    if not matched:
                        self.errmsg = "Not found in the AP's Linux shell an "\
                                      "ACL entry matched with the restricted "\
                                      "subnet [%s]" % subnet
                        return


            self.msg += "All the restricted subnet entries have been applied "\
                        "on the AP successfully. "


        if self.conf['hotspot_cfg'].has_key('walled_garden_list'):
            # If an active AP is not specified, verify the ACL in all AP
            if self.conf.has_key('active_ap'):
                ap_list = [self.active_ap]

            else:
                ap_list = self.testbed.components['AP']

            for ap in ap_list:
                logging.info("Verify the Redirect Policy list stored in "\
                             "the AP[%s]'s Linux shell in /proc/afmod/policy" % \
                             ap.base_mac_addr)

                acl_list = ap.get_hotspot_policy(self.wlan_id,
                                                 redir_policy = True)

                for entry in self.conf['hotspot_cfg']['walled_garden_list']:
                    logging.info("Verify entry [%s]" % entry)
                    #Updated by Jacky Luh @since: 2013-12-05
                    #9.8 build enhance the walled garden policy file to surpport the domain name
                    ip, port, mask = self._parseWalledGardenEntry(entry, resolve_name = False)
                    logging.info("IP:[%s] port[%s] - mask[%s]" % (ip, port, mask))
                    dst_addr = "%s/%s" % (ip, mask)
                    match = [acl for acl in acl_list if acl['dst-addr'] == dst_addr]
                    if not match:
                        self.errmsg = "Not found in the AP's Linux shell "\
                                      "an ACL entry for the walled garden entry [%s]" % entry
                        return

                    if match[0]['action'] != "Pass":
                        self.errmsg = "The ACL entry [%s] has the action [%s] "\
                                      "instead of [Pass]" % (entry, match[0]['action'])
                        return

                    if port and match[0]['dport'] != port:
                        self.errmsg = "The ACL entry [%s] has the port [%s] "\
                                      "instead of [%s]" % (entry, match[0]['dport'], port)
                        return

            self.msg += "All the walled garden entries have been applied on the AP successfully. "


    def _testAssociateStationToWlan(self):
        if self.conf['acl_cfg']:
            logging.info("Modify the L2 ACL [%s] to deny the wireless station" % self.conf['acl_cfg']['acl_name'])
            self.conf['acl_cfg'].update({'allowed_access':False, 'mac_list':[self.sta_wifi_if['mac']]})
            lib.zd.ac.edit_l2_acl_policy(self.zd, self.conf['acl_cfg']['acl_name'], self.conf['acl_cfg'])

            logging.info("Try to associate the station to the WLAN")
            res = tmethod.assoc_station_with_ssid(self.target_station, self.conf['wlan_cfg'], 10)
            if res:
                msg = "The station failed to associate to the WLAN: CORRECT BEHAVIOR. "
                logging.info(msg)
                self.msg += msg
            else:
                self.errmsg = "The station could associate to the WLAN while it had been denied by the ACL"
                return

            logging.info("Modify the L2 ACL [%s] to allow the wireless station" % self.conf['acl_cfg']['acl_name'])
            self.conf['acl_cfg'].update({'allowed_access':True, 'mac_list':[]})
            lib.zd.ac.edit_l2_acl_policy(self.zd, self.conf['acl_cfg']['acl_name'], self.conf['acl_cfg'])

            logging.info("Try to re-associate the station to the WLAN")
            res = tmethod.assoc_station_with_ssid(self.target_station, self.conf['wlan_cfg'], self.conf['check_status_timeout'])
            if res:
                self.errmsg = "The station could not associate to the WLAN after it had been allowed by the ACL"
                return
            else:
                msg = "The station succeeded in associating to the WLAN: CORRECT BEHAVIOR. "
                logging.info(msg)
                self.msg += msg
        else:
            self.errmsg = tmethod.assoc_station_with_ssid(self.target_station, self.conf['wlan_cfg'], self.conf['check_status_timeout'])

    def _cfgGetStaWifiIpAddress(self):
        res, ip, mac = tmethod.renew_wifi_ip_address(self.target_station, self.conf['check_status_timeout'])
        if not res:
            raise Exception(mac)
        self.sta_wifi_if = {'ip': ip, 'mac': mac.lower()}

    def _testStationConnectivityBeforeHotspotAuth(self):
        logging.info("Verify the connectivity from the station before Hotspot authentication is performed")
        self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.conf['target_ip'],
                                                           ping_timeout_ms = self.conf['ping_timeout_ms'])
        if self.errmsg: return
        self.msg += "The station could not transmit traffic before being authenticated. "

        # It is expected that there should be some host entries in the walled garden list (entries without port/subnet)
        # Those are used to verify connectivity from the wireless station. They are should be pingable.
        # It is suggested that the IP interfaces of the Netgear switch, or the names that can be resolved by the DNS server
        if self.conf['hotspot_cfg'].has_key('walled_garden_list'):
            for entry in self.conf['hotspot_cfg']['walled_garden_list']:
                #Updated by Jacky Luh @since: 2013-12-05
                #9.8 build enhance the walled garden policy file to surpport the domain name
                ip, port, mask = self._parseWalledGardenEntry(entry, resolve_name = False)
                if mask == "32":
                    logging.info("The walled garden destination: %s" % ip)
                    self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, ip,
                                                                      ping_timeout_ms = self.conf['ping_timeout_ms'])
                    if self.errmsg: return
            self.msg += "The station could transmit traffic to destinations in the walled garden list. "

    def _testVerifyStationInfoOnZDBeforeHotspotAuth(self):
        logging.info("Verify information of the target station shown on the Zone Director before performing Hotspot authentication")
        exp_client_info = {"ip": self.sta_wifi_if['ip'], "status": "Unauthorized", "wlan": self.conf['wlan_cfg']['ssid']}

        self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd, self.sta_wifi_if['mac'],
                                                                           exp_client_info, self.conf['check_status_timeout'])
        if not self.errmsg:
            self.msg += "The status of the station was 'Unauthorized' before being authenticated. "

    def _cfgPerformHotspotAuthOnStation(self):
        logging.info("Perform Hotspot authentication on the station")
        if self.conf['hotspot_cfg'].has_key('start_page'):
            redirect_url = self.conf['hotspot_cfg']['start_page']

        else:
            redirect_url = ''

        start_t = time.time()
        arg = tconfig.get_hotspot_auth_params(
            self.zd, self.conf['auth_info']['username'],
            self.conf['auth_info']['password'],
            redirect_url = redirect_url
        )
        self.target_station.perform_hotspot_auth(arg)

        self.auth_time = time.time() - start_t
        logging.debug('Time needed for perform_hotspot_auth: %s' % self.auth_time)
        self.msg += "Hotspot authentication was done on the station successfully. "
        if self.conf['hotspot_cfg'].has_key('start_page'):
            self.msg += "The station's Web session was redirected successfully to %s. " % self.conf['hotspot_cfg']['start_page']

        # Record the time when the station starts being authenticated by the ZD
        # This value is used to verify the Session Timeout behaviour
        self.t0 = time.time()


    def _testStationConnectivityAfterHotspotAuth(self):
        logging.info("Verify the connectivity from the station after Hotspot authentication is performed")
        logging.info("The not restricted destination: %s" % self.conf['target_ip'])
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.conf['target_ip'],
                                                          ping_timeout_ms = self.conf['ping_timeout_ms'])
        if self.errmsg: return
        self.msg += "The station could transmit traffic after being authenticated. "

        # It is expected that the restricted subnet list contains some host entries (subnets with mask of 32 bits)
        # These host entries should be the IP addresses of the interfaces configured on the Linux server/Netgear switch
        if self.conf['hotspot_cfg'].has_key('restricted_subnet_list'):
            for subnet in self.conf['hotspot_cfg']['restricted_subnet_list']:
                ip, mask = subnet.split("/")
                if mask == "32":
                    logging.info("The restricted destination: %s" % ip)
                    self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, ip,
                                                                       ping_timeout_ms = self.conf['ping_timeout_ms'])
                    if self.errmsg: return
            self.msg += "The station could not transmit traffic to destinations in restricted subnet list. "


    def _testVerifyStationInfoOnZDAfterHotspotAuth(self):
        logging.info("Verify information of the target station shown on the Zone Director after performing Hotspot authentication")
        exp_client_info = {"ip": self.conf['auth_info']['username'], "status": "Authorized", "wlan": self.conf['wlan_cfg']['ssid']}
        self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd, self.sta_wifi_if['mac'],
                                                                           exp_client_info, self.conf['check_status_timeout'])
        if not self.errmsg:
            self.msg += "The status of the station was 'Authorized' after being authenticated. "

    def _testRadiusAccouting(self):
        if not self.conf['hotspot_cfg'].has_key('acct_svr'): return
        if not self.conf['hotspot_cfg'].has_key('interim_update_interval'): return
        
        self._cfgStartSnifferOnLinuxPC()

        re_list = []
        if self.conf['hotspot_cfg'].has_key('radius_location_id') or self.conf['hotspot_cfg'].has_key('radius_location_name'):
            logging.info("Verify Radius accouting extra attributes")
            if self.conf['hotspot_cfg'].has_key('radius_location_id'):
                value_pattern = re.escape(self.conf['hotspot_cfg']['radius_location_id'])
                pattern = "Vendor Specific Attribute \(26\), length: [\d]+, Value: Vendor: Wi-Fi Alliance \(14122\)"
                pattern += "[\s]+Vendor Attribute: 1, Length: [\d]+, Value: %s" % value_pattern
                reg = re.compile(pattern)
                re_list.append([reg, self.conf['hotspot_cfg']['radius_location_id']])
            if self.conf['hotspot_cfg'].has_key('radius_location_name'):
                value_pattern = re.escape(self.conf['hotspot_cfg']['radius_location_name'])
                pattern = "Vendor Specific Attribute \(26\), length: [\d]+, Value: Vendor: Wi-Fi Alliance \(14122\)"
                pattern += "[\s]+Vendor Attribute: 2, Length: [\d]+, Value: %s" % value_pattern
                reg = re.compile(pattern)
                re_list.append([reg, self.conf['hotspot_cfg']['radius_location_name']])
        else:
            logging.info("Verify Radius accouting update frequency")

        svr_addr_pattern = re.escape(self.conf['acct_info']['svr_addr'])
        svr_port_pattern = self.conf['acct_info']['svr_port']
              
        number_of_update = 5
        wait_t = int(self.conf['hotspot_cfg']['interim_update_interval']) * 60 * number_of_update + 15
        logging.info("Wait in %d seconds ..." % wait_t)
        time.sleep(wait_t)
        
        logging.info("Read the RADIUS ACCOUNTING packets captured on the server")
        res = self.sniffer.read_sniffer(return_as_list = False)
        
        lines = res.split("\r\n")[2:]
        packets = []
        tmp = ""
        for line in lines:
            packet_entry = False if line.startswith('\t') else True
            if packet_entry:
                if tmp:
                    packets.append(tmp) 
                    
                tmp = line
            
            else:
                tmp += line
                   
        request_pattern = "%s\.%s: RADIUS, length: [\d]+[\s]+Accounting Request" % (svr_addr_pattern, svr_port_pattern)
        request_re = re.compile(request_pattern)
        request_packets = [p for p in packets if request_re.search(p)]
        
        if not request_packets:
            self.errmsg = "Not found any radius accounting request packet"
            return
        
        if re_list:
            for reg, value in re_list:
                for p in request_packets:
                    if not reg.search(p):
                        self.errmsg = "Not found attribute value [%s] in the radius accounting request packet" % value
                        return
                    
            self.msg += "The extra attribute values were transmitted in the accounting packets. "

        else:
            update_pattern = "Accounting Status Attribute \(40\), length: [\d]+, Value: Interim-Update"
            update_re = re.compile(update_pattern)
            update_packets = [p for p in request_packets if update_re.search(p)]
            
            ts_pattern = "([\d\-]{10} [\d:]{8})(\.[\d]+)"
            ts_re = re.compile(ts_pattern)
            sid_pattern = "Accounting Session ID Attribute \(44\), length: [\d]+, Value: ([\w\-]+)"
            sid_re = re.compile(sid_pattern)
            
            time_stamp_dict = {}
            for p in update_packets:
                tsr = ts_re.search(p)
                sidr = sid_re.search(p)
                if tsr and sidr:
                    t = time.mktime(time.strptime(tsr.group(1), "%Y-%m-%d %H:%M:%S")) + float(tsr.group(2))
                    # Convert to minutes
                    t = int(round(t / 60))
                    sid = sidr.group(1)
                    if sid in time_stamp_dict:
                        time_stamp_dict[sid].append(t)
                    
                    else:
                        time_stamp_dict[sid] = [t]
            
            count = 0
            for sid in time_stamp_dict:
                if len(time_stamp_dict[sid]) > count:
                    count = len(time_stamp_dict[sid])
            
            if count < 2:
                self.errmsg = "Found maximum %d accounting interim-update packets in a session: %s" % (count, time_stamp_dict)
                return

            # Verify the interval between the accounting Interim-Update packets
            interval = int(self.conf['hotspot_cfg']['interim_update_interval'])
            for sid in time_stamp_dict:
                if len(time_stamp_dict[sid]) > 1:
                    for i in range(len(time_stamp_dict[sid]) - 1):
                        if time_stamp_dict[sid][i + 1] - time_stamp_dict[sid][i] != interval:
                            self.errmsg = "The interval between the accounting interim-update packets was %s minutes instead of %s minutes" % \
                                          (time_stamp_dict[sid][i + 1] - time_stamp_dict[sid][i], interval)
                            return
            
            self.msg += "The interval between the accounting interim-update packets was %d minutes. " % interval 

    def _cfgStartSnifferOnLinuxPC(self):
        logging.info("Start the sniffer on the Linux PC to capture RADIUS ACCOUNTING packets")
        sniffing_if = self.sniffer.get_interface_name_by_ip(self.sniffer.ip_addr)
        sniffing_param = "-i %s udp port %s" % (sniffing_if, self.conf['acct_info']['svr_port'])
        self.sniffer.start_sniffer(sniffing_param)

    def _testSessionTimeout(self):
        zd_t = self.conf['hotspot_cfg']['session_timeout'] if self.conf['hotspot_cfg'].has_key('session_timeout') else 0
        svr_t = self.conf['auth_info']['session_timeout'] if self.conf['auth_info'].has_key('session_timeout') else 0
        zd_t = int(zd_t) * 60
        svr_t = int(svr_t) * 60
        # Quit if none of the timers are specified
        if not zd_t and not svr_t: return

        logging.info("Verify Session Timeout behaviour")
        if svr_t:
            logging.info("The Session Timeout attribute is configured on the Radius server. It overrides the Hotspot configuration.")
            t = svr_t
        else:
            logging.info("The Session Timeout value configured in the Hotspot profile takes effect.")
            t = zd_t
        wait_t = t - (time.time() - self.t0) + 5

        logging.info("Remove all log entries on the ZD")
        self.zd.clear_all_events()

        logging.info("Wait in %d seconds ..." % wait_t)
        time.sleep(wait_t)

        self._testSessionTimeoutStationStatusOnZD()
        if self.errmsg: return
        self._testSessionTimeoutStationConnectivity()
        if self.errmsg: return
        self._testSessionTimeoutEventLog()
        if self.errmsg: return

    def _testSessionTimeoutStationConnectivity(self):
        logging.info("Verify the connectivity from the station after its session is terminated")
        self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.conf['target_ip'],
                                                           ping_timeout_ms = self.conf['ping_timeout_ms'])
        if self.errmsg: return
        self.msg += "The station could not transmit traffic after its session was terminated. "

    def _testSessionTimeoutStationStatusOnZD(self):
        logging.info("Verify information of the target station shown on the Zone Director after its session is terminated")
        exp_client_info = {"ip": self.sta_wifi_if['ip'], "status": "Unauthorized", "wlan": self.conf['wlan_cfg']['ssid']}

        self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd, self.sta_wifi_if['mac'],
                                                                           exp_client_info, self.conf['check_status_timeout'])
        if not self.errmsg:
            self.msg += "The status of the station was 'Unauthorized' after its session was terminated. "

    def _testSessionTimeoutEventLog(self):
        logging.info("Verify the Event Logs")

        #MSG_client_session_expired={user} session time limit exceeded; session terminated
        event = self.zd.messages['MSG_client_session_expired']
        event = event.replace('{user}', '')

        all_logs = self.zd.get_events()
        match = [l for l in all_logs \
                 if event in l[3] and l[2] == self.conf['auth_info']['username']]
        if not match:
            self.errmsg = "There was no log entry to record the event that the station has terminated due to timed out session"
        else:
            self.msg += "Found a log entry indicates that the station has been terminated due to session timed out. "

    def _testIdleTimeout(self):
        zd_t = self.conf['hotspot_cfg']['idle_timeout'] if self.conf['hotspot_cfg'].has_key('idle_timeout') else 0
        svr_t = self.conf['auth_info']['idle_timeout'] if self.conf['auth_info'].has_key('idle_timeout') else 0
        zd_t = int(zd_t) * 60
        svr_t = int(svr_t) * 60
        # Quit if none of the timers are specified
        if not zd_t and not svr_t: return

        msg = "Verify Idle Timeout behaviour: Station reassociates %s the timer gets expired" % \
              ("BEFORE" if self.conf['relogin_before_timer_expired'] else "AFTER")
        logging.info(msg)
        if svr_t:
            logging.info("The Idle Timeout attribute is configured on the Radius server. It overrides the Hotspot configuration.")
            t = svr_t
        else:
            logging.info("The Idle Timeout value configured in the Hotspot profile takes effect.")
            t = zd_t

        self._cfgDisconnectStationFromWLAN()

        logging.info("Remove all log entries on the ZD")
        self.zd.clear_all_events()

        #wait_t = (t - (time.time() - self.t0)) / 4 if self.conf['relogin_before_timer_expired'] else t * 2 - (time.time() - self.t0)
        #wait_t = (t - self.auth_time - (time.time() - self.t0)) / 4 if self.conf['relogin_before_timer_expired'] else t + t * 1/3
        #JLIN@20100624 since zd check hotspot client if expired every 10 minutes, wait more 10 minutes to make sure client expired.
        #wait_t = 0 if self.conf['relogin_before_timer_expired'] else t + t * 1 / 3
        wait_t = 0 if self.conf['relogin_before_timer_expired'] else t + 600
        logging.info("Wait in %d seconds ..." % wait_t)
        time.sleep(wait_t)
        self._cfgConnectStationToWLAN()
        self._testIdleTimeoutStationStatusOnZD(timer_expired = not self.conf['relogin_before_timer_expired'])
        if self.errmsg: return
        self._testIdleTimeoutStationConnectivity(timer_expired = not self.conf['relogin_before_timer_expired'])
        if self.errmsg: return
        self._testIdleTimeoutEventLog(timer_expired = not self.conf['relogin_before_timer_expired'])
        if self.errmsg: return

    def _cfgDisconnectStationFromWLAN(self):
        logging.info("Disconnect the station from the currently associated WLAN")
        self.target_station.disconnect_from_wlan()
        # Record the time when the station starts disassociating from the WLAN
        # This value is used to verify the Idle Timeout behaviour
        self.t0 = time.time()

    def _cfgConnectStationToWLAN(self):
        logging.info("Connect the station back to the configured WLAN [%s]" % self.conf['wlan_cfg']['ssid'])
        self.target_station.connect_to_wlan(ssid = self.conf['wlan_cfg']['ssid'])

    def _testIdleTimeoutStationConnectivity(self, timer_expired):
        logging.info("Verify the connectivity from the station after it reassociates back to the WLAN")
        if timer_expired:
            self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.conf['target_ip'],
                                                               ping_timeout_ms = self.conf['ping_timeout_ms'])
            if self.errmsg: return
            self.msg += "The station could not transmit traffic after it reassociates back to the WLAN. "
        else:
            self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.conf['target_ip'],
                                                              ping_timeout_ms = self.conf['ping_timeout_ms'])
            if self.errmsg: return
            self.msg += "The station could transmit traffic after it reassociates back to the WLAN. "

    def _testIdleTimeoutStationStatusOnZD(self, timer_expired):
        logging.info("Verify information of the target station shown on the Zone Director after it reassocicates back to the WLAN")
        if timer_expired:
            exp_client_info = {"ip": self.sta_wifi_if['ip'], "status": "Unauthorized", "wlan": self.conf['wlan_cfg']['ssid']}

            self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd, self.sta_wifi_if['mac'],
                                                                               exp_client_info, self.conf['check_status_timeout'])
            if not self.errmsg:
                self.msg += "The status of the station was 'Unauthorized' after it reassociates back to the WLAN. "
        else:
            exp_client_info = {"ip": self.conf['auth_info']['username'], "status": "Authorized", "wlan": self.conf['wlan_cfg']['ssid']}

            self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd, self.sta_wifi_if['mac'],
                                                                               exp_client_info, self.conf['check_status_timeout'])
            if not self.errmsg:
                self.msg += "The status of the station was 'Authorized' after it reassociates back to the WLAN. "

    def _testIdleTimeoutEventLog(self, timer_expired):
        logging.info("Verify the Event Logs")
        all_logs = self.zd.get_events()

        #MSG_client_reconnect_within_grace_period=
        # {user} reconnects to {ap} within grace period.  \
        # No additional authentication is required.

        msg = self.zd.messages['MSG_client_reconnect_within_grace_period']
        msg = msg.replace('  ', ' ')
        msg_with_mac = msg
        msg = msg.replace('{user}', 'User\[%s\]' % self.conf['auth_info']['username'])

        if self.conf.has_key('active_ap'):
            msg = msg.replace('{ap}', 'AP\[%s\]' % self.active_ap.base_mac_addr)
        else:
            msg = msg.replace('{ap}', 'AP\[%s\]' % '.*')


        msg_with_mac = msg_with_mac.replace('{user}', 'User\[%s@%s\]' %
                                            (self.conf['auth_info']['username'],
                                             self.sta_wifi_if['mac']))

        if self.conf.has_key('active_ap'):
            msg_with_mac = msg_with_mac.replace('{ap}', 'AP\[%s\]' %
                                                self.active_ap.base_mac_addr)
        else:
            msg_with_mac = msg_with_mac.replace('{ap}', 'AP\[%s\]' % '.*')

        match = [l for l in all_logs \
                 if re.search(msg, l[3]) and l[2] == self.conf['auth_info']['username']]

        # backward compability
        if not match:
            match = [l for l in all_logs \
                 if re.search(msg_with_mac, l[3])
                 and l[2] == self.conf['auth_info']['username']]

        if match:
            if timer_expired:
                self.errmsg = "There was a log entry to record the event that "\
                              "the station reconnects within grace period. "
            else:
                self.msg += "Found a log entry indicates that the station "\
                            "reconnects within grace period. "

        else:
            if timer_expired:
                self.msg += "Not found any log entries indicate that "\
                            "the station reconnects within grace period. "
            else:
                self.errmsg = "There was no log entry to record the event that "\
                              "the station reconnects within grace period. "


    def _testUAMRedirectedURL(self):
        if self.conf['hotspot_cfg'].has_key('logout_page'):
            logging.info("Verify the UAM Redirected URL [%s]" %
                         self.conf['hotspot_cfg']['logout_page'])

            self._cfgPerformHotspotDeAuthOnStation()
            self._testHotspotDeAuthConnectivity()
            if self.errmsg:
                return

            self._testHotspotDeAuthStationStatusOnZD()
            if self.errmsg:
                return

    def _cfgPerformHotspotDeAuthOnStation(self):
        logging.info("Log out the Hotspot WLAN on the wireless station")
        params = {'logout_url':self.conf['hotspot_cfg']['logout_page']}
        self.target_station.perform_hotspot_deauth(**params)
        self.msg += "Logging out the Hotspot was done on the station successfully. "

    def _testHotspotDeAuthConnectivity(self):
        logging.info("Verify the connectivity from the station after logging out the Hotspot WLAN")
        self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.conf['target_ip'],
                                                           ping_timeout_ms = self.conf['ping_timeout_ms'])
        if self.errmsg: return
        self.msg += "The station could not transmit traffic after logging out the Hotspot WLAN. "

    def _testHotspotDeAuthStationStatusOnZD(self):
        logging.info("Verify information of the target station shown on the Zone Director after logging out the Hotspot WLAN")
        exp_client_info = {"ip": self.sta_wifi_if['ip'], "status": "Unauthorized", "wlan": self.conf['wlan_cfg']['ssid']}

        self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd, self.sta_wifi_if['mac'],
                                                                           exp_client_info, self.conf['check_status_timeout'])
        if not self.errmsg:
            self.msg += "The status of the station was 'Unauthorized' after logging out the Hotspot WLAN. "

    def _testIntegration(self):
        if self.conf['expected_subnet']:
            logging.info("Verify the subnet address of the wireless station")
            net_addr = utils.get_network_address(self.sta_wifi_if['ip'], self.conf['expected_mask'])
            if self.conf['expected_subnet'] != net_addr:
                self.errmsg = "The leased IP address was [%s], which is not in the expected subnet [%s]" % \
                              (self.sta_wifi_if['ip'], self.conf['expected_subnet'])

#
# cleanup()
#
    def _cfgRemoveAllConfigOnZDAtCleanup(self):
        logging.info("Remove all WLANs configured on the ZD")
        lib.zd.wlan.delete_all_wlans(self.zd)
        logging.info("Remove all HOTSPOT profiles configured on the ZD")
        lib.zd.wispr.remove_all_profiles(self.zd)
        logging.info("Remove all AAA servers configured on the ZD")
        lib.zd.aaa.remove_all_servers(self.zd)
        if self.conf['acl_cfg']:
            logging.info("Remove all L2 ACL rules configured on the ZD")
            lib.zd.ac.delete_all_l2_acl_policies(self.zd)

    def _cfgRemoveWlanFromStation(self):
        if self.target_station:
            logging.info("Remove all WLANs from the station")
            tconfig.remove_all_wlan_from_station(self.target_station, check_status_timeout = self.conf['check_status_timeout'])

    def _cfgStopSnifferOnLinuxPC(self):
        if self.conf.has_key('acct_info'):
            logging.info("Stop the sniffer on the Linux PC")
            self.sniffer.stop_sniffer()

