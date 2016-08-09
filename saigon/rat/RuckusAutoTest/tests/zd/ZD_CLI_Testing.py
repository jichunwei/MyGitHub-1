# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: This script use to test for the ZD CLI commands
Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters: 'testcase': the short name of test case. Ex: 'force-mesh-mode-to-auto'
                    'target_station': the target station ethernet  IP address

   Result type: PASS/FAIL/ERROR
   Results:

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
        - Clean up all non default ZD and station setting
   2. Test:
        - Base on the test case:
           + Configure ZD on WEBUI
           + Verify the result on the CLI by using the testing command
   3. Cleanup:
        - Clean up the testing environment by remove all non default configuration on ZD,
        target station.
"""
import time
import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_CLI as tmdcli
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components import Helpers as lib


class ZD_CLI_Testing(Test):
    required_components = ['Zone Director']
    test_parameters = {'testcase': 'the short name of test case'}

    def config(self, conf):
        self._initTestParameters(conf)
        self._cfgTargetStation()

        self._defineTestFunctions()

        logging.info("Remove all configuration on the Zone Director")
        #lib.zd.wgs.remove_wlan_groups(self.zd)
        #self.zd.remove_all_cfg()
        #self.zd.remove_all_acl_rules()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

    def test(self):
        self.test_functions_for_testcase[self.conf['testcase']]()
        if self.errmsg:
            return ('FAIL', self.errmsg)

        logging.info(self.passmsg)
        return ('PASS', self.passmsg)

    def cleanup(self):
        logging.info("Remove all configuration on the Zone Director")
        #lib.zd.wgs.remove_wlan_groups(self.zd)
        #self.zd.remove_all_cfg()
        #self.zd.remove_all_acl_rules()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        if self.target_station:
            self.target_station.remove_all_wlan()

        self.zd_cli.re_initialize()

    # Configuration
    def _initTestParameters(self, conf):
        self.conf = {'testcase':'',
                     'target_station':'',
                     'check_status_timeout': 180,
                     'break_time': 2}
        self.conf.update(conf)
        self.target_station = None
        self.zd_cli = None
        self.zd = self.testbed.components['ZoneDirector']

        self.zd_cli = self.testbed.components['ZoneDirectorCLI']

        self.aps = self.testbed.components['AP']

        self.test_functions_for_testcase = {}
        self.auth_server = {'server_addr': '192.168.0.252',
                            'server_port': '1812',
                            'server_name': 'Authentication',
                            'radius_auth_secret': '1234567890'}
        self.acct_server = {'server_addr': '192.168.0.250',
                            'server_port': '1812',
                            'server_name': 'Accounting',
                            'radius_acct_secret': '1234567890'}
        self.wlan_cfg = {'ssid': 'ZD-CLI-Testing',
                         'auth': 'open',
                         'encryption': 'none'}
        self.user_cfg = {'username': 'CLI_User',
                         'password': '123456'}

        self.comparative_params = {'ssid':self.wlan_cfg['ssid'],
                                   'auth_server': self.auth_server['server_addr'],
                                   'acct_server': self.acct_server['server_addr']}


        self.sta_ip_addr = self.get_station_download_ip_addr()
        self.sta_net_mask = utils.get_subnet_mask(self.zd.ip_addr, False)
        self.activate_url = self.zd.get_zero_it_activate_url()

        self.l2_acl_cfg = {'acl_name': 'Test_L2_ACL'}
        self.role_cfg = {'rolename': 'Test_Role'}

        self.errmsg = ''
        self.passmsg = ''

    def _defineTestFunctions(self):
        test_funcs = {'wlaninfo_v': self._testCommandWLANINFO_V,
                      'wlaninfo_s': self._testCommandWLANINFO_S,
                      'wlaninfo_t': self._testCommandWLANINFO_T,
                      'wlaninfo_c': self._testCommandWLANINFO_C,
                      'wlaninfo_r': self._testCommandWLANINFO_R,
                      'wlaninfo_w': self._testCommandWLANINFO_W,
                      'wlaninfo_u': self._testCommandWLANINFO_U,
                      'wlaninfo_m': self._testCommandWLANINFO_M,
                      'wlaninfo_a': self._testCommandWLANINFO_A,
                      'wlaninfo_system':self._testCommandWLANINFO_System,
                      'wlaninfo_dos': self._testCommandWLANINFO_Dos,
                      'wlaninfo_web_auth': self._testCommandWLANINFO_Web_Auth,
                      'wlaninfo_dpsk': self._testCommandWLANINFO_DPSK,
                      'wlaninfo_dcert': self._testCommandWLANINFO_DCERT,
                      'wlaninfo_acl': self._testCommandWLANINFO_ACL,
                      'wlaninfo_role': self._testCommandWLANINFO_Role,
                      'wlaninfo_auth': self._testCommandWLANINFO_Auth,
                      'wlaninfo_pmk': self._testCommandWLANINFO_PMK,
                      'wlaninfo_mesh_ap': self._testCommandWLANINFO_Mesh_AP,
                      'wlaninfo_mesh_topology': self._testCommandWLANINFO_Mesh_Topology,
                      'wlaninfo_mesh_history': self._testCommandWLANINFO_Mesh_History,
                      'wlaninfo_wlangroup': self._testCommandWLANINFO_WLANGroup,
                      'wlaninfo_apgroup': self._testCommandWLANINFO_APGroup,
                      'wlaninfo_disc_ap': self._testCommandWLANINFO_DISC_AP,
                      'apmgrinfo_a': self._testCommandAPMGRINFO_A,
                      'apmgrinfo_p': self._testCommandAPMGRINFO_P,
                      'ping': self._testCommandPing,
                      'stp': self._testCommandSTP,
                      'upnp': self._testCommandUPNP,
                      'show_ap': self._test_command_show_ap,
                      'show_station': self._test_command_show_station}
        self.test_functions_for_testcase.update(test_funcs)

    def _testCommandWLANINFO_V(self):
        """
        """
        self._configAuthenServer()
        self._configAccountingServer()
        self.wlan_cfg.update({'do_webauth': True,
                              'auth_svr': self.auth_server['server_name'],
                              'acct_svr': self.acct_server['server_name']})
        self._configWLAN()
        time.sleep(5)

        expected_vap_info = self._collectExpectedInfoOnWebUI()
        self.passmsg, self.errmsg = tmdcli.test_show_all_vap(self.zd_cli, expected_vap_info)
        if self.errmsg:
            logging.info('[Error][wlaninfo -V]: %s' % self.errmsg)
            return

        self.passmsg, self.errmsg = tmdcli.test_show_a_vap(self.testbed.components['AP'], self.zd,
                                                           self.zd_cli, self.comparative_params)
        if self.errmsg:
            logging.info('[Error][wlaninfo -v vap_mac -l7]: %s' % self.errmsg)
            return

        self.passmsg, self.errmsg = tmdcli.test_delete_a_vap(self.testbed.components['AP'], self.zd, self.zd_cli)
        if self.errmsg:
            logging.info('[Error][wlaninfo -v vap_mac -D]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_S(self):
        """
        """
        self._configWLAN()
        self._verifyStationConnection()
        if self.errmsg:
            raise Exception(self.errmsg)

        sta_info = (self.sta_wifi_mac_addr.lower(), self.sta_wifi_ip_addr)
        self.passmsg, self.errmsg = tmdcli.test_show_all_station(self.zd_cli, [sta_info])
        if self.errmsg:
            logging.info('[Error][wlaninfo -S]: %s' % self.errmsg)
            return

        self.passmsg, self.errmsg = tmdcli.test_show_a_station(self.zd_cli, sta_info)
        if self.errmsg:
            logging.info('[Error][wlaninfo -s sta_mac -l7]: %s' % self.errmsg)
            return

        self.passmsg, self.errmsg = tmdcli.test_delete_a_station(self.zd_cli, sta_info)
        if self.errmsg:
            logging.info('[Error][wlaninfo -s sta_mac -D]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_T(self):
        self.passmsg, self.errmsg = tmdcli.test_show_timer(self.zd_cli)
        if self.errmsg:
            logging.info('[Error][wlaninfo -T]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_C(self):
        self.passmsg, self.errmsg = tmdcli.test_show_all_config_ap(self.zd, self.zd_cli)
        if self.errmsg:
            logging.info('[Error][wlaninfo -C]: %s' % self.errmsg)
            return

        self.passmsg, self.errmsg = tmdcli.test_show_a_config_ap(self.zd, self.zd_cli)
        if self.errmsg:
            logging.info('[Error][wlaninfo -c ap_mac -l7]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_R(self):
        self.passmsg, self.errmsg = tmdcli.test_show_rogue(self.zd_cli)
        if self.errmsg:
            logging.info('[Error][wlaninfo -R]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_W(self):
        self._configWLAN()
        expected_info = {'ssid': self.wlan_cfg['ssid']}

        self.passmsg, self.errmsg = tmdcli.test_show_wlan_info(self.zd_cli, expected_info)
        if self.errmsg:
            logging.info('[Error][wlaninfo -W]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_U(self):
        self._create_user()
        expected_info = self.user_cfg

        self.passmsg, self.errmsg = tmdcli.test_show_user_info(self.zd_cli, expected_info)
        if self.errmsg:
            logging.info('[Error][wlaninfo -U]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_M(self):
        self.passmsg, self.errmsg = tmdcli.test_show_mesh_info(self.zd, self.zd_cli)
        if self.errmsg:
            logging.info('[Error][wlaninfo -M]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_A(self):
        self.passmsg, self.errmsg = tmdcli.test_show_all_active_ap(self.zd, self.zd_cli)
        if self.errmsg:
            logging.info('[Error][wlaninfo -A]: %s' % self.errmsg)
            return

        self.passmsg, self.errmsg = tmdcli.test_show_an_active_ap(self.zd, self.zd_cli)
        if self.errmsg:
            logging.info('[Error][wlaninfo -a ap_mac]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_System(self):
        self.passmsg, self.errmsg = tmdcli.test_show_system_parameters(self.zd_cli)
        if self.errmsg:
            logging.info('[Error][wlaninfo --system]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_Dos(self):
        self.passmsg, self.errmsg = tmdcli.test_show_dos_info(self.zd_cli)
        if self.errmsg:
            logging.info('[Error][wlaninfo --dos]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_Web_Auth(self):
        self._create_user()
        self.wlan_cfg.update({'do_webauth': True})
        self._configWLAN()
        time.sleep(2)

        self._verifyStationConnection()
        if self.errmsg:
            raise Exception(self.errmsg)
        time.sleep(2)

        logging.info("Perform Web Authentication on the target station %s" % self.conf['target_station'])

        arg = tconfig.get_web_auth_params(self.zd, self.user_cfg['username'], self.user_cfg['password'])
        self.target_station.perform_web_auth(arg)

        errmsg, client_info = tmethod.verify_zd_client_is_authorized(
                                  self.zd, self.user_cfg['username'], self.sta_wifi_mac_addr,
                                  self.conf['check_status_timeout'])
        if errmsg:
            raise Exception(errmsg)

        self.passmsg, self.errmsg = tmdcli.test_show_authen_client(self.zd_cli, self.sta_wifi_mac_addr)
        if self.errmsg:
            logging.info('[Error][wlaninfo --web-auth]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_DPSK(self):
        self._create_user()
        self.wlan_cfg.update({'do_zero_it': True,
                              'do_dynamic_psk': True,
                              'wpa_ver': 'WPA',
                              'encryption': 'TKIP',
                              'key_string': '12345678'
                              })
        self._configWLAN()
        time.sleep(2)

        self.target_station.cfg_wlan_with_zero_it(self.target_station.get_ip_addr(), self.sta_ip_addr,
                                                  self.sta_net_mask, '', False,
                                                  self.activate_url, self.user_cfg['username'],
                                                  self.user_cfg['password'], '')
        time.sleep(2)
        self.target_station.connect_to_wlan(self.wlan_cfg['ssid'])
        errmsg = tmethod.check_station_is_connected_to_wlan(self.target_station,
                                                            self.conf['check_status_timeout'],
                                                            self.conf['break_time'])
        if errmsg:
            raise Exception(errmsg)

        self.passmsg, self.errmsg = tmdcli.test_show_dynamic_psk(self.zd_cli)
        if self.errmsg:
            logging.info('[Error][wlaninfo --all-dpsk]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_DCERT(self):
        self._create_user()
        self.wlan_cfg.update({'do_dynamic_psk': True,
                              'auth': 'EAP',
                              'wpa_ver': 'WPA'
                              })
        self._configWLAN()
        time.sleep(2)
        self.target_station.cfg_wlan_with_zero_it(self.target_station.get_ip_addr(), self.sta_ip_addr,
                                                  self.sta_net_mask, self.wlan_cfg['auth'], False,
                                                  self.activate_url, self.user_cfg['username'],
                                                  self.user_cfg['password'], self.wlan_cfg['ssid'])
        time.sleep(2)
        self.passmsg, self.errmsg = tmdcli.test_show_dynamic_cert(self.zd_cli)
        if self.errmsg:
            logging.info('[Error][wlaninfo --all-dpsk]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_ACL(self):
        lib.zd.ac.create_l2_acl_policy(self.zd, self.l2_acl_cfg)
        time.sleep(2)

        self.passmsg, self.errmsg = tmdcli.test_show_l2_acl(self.zd_cli, self.l2_acl_cfg['acl_name'])
        if self.errmsg:
            logging.info('[Error][wlaninfo --all-acl]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_Role(self):
        self.zd.create_role(**self.role_cfg)
        time.sleep(2)

        self.passmsg, self.errmsg = tmdcli.test_show_role(self.zd_cli, self.role_cfg['rolename'])
        if self.errmsg:
            logging.info('[Error][wlaninfo --all-role]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_Auth(self):
        self._configAuthenServer()
        time.sleep(2)

        self.passmsg, self.errmsg = tmdcli.test_show_auth_server(self.zd_cli, self.auth_server['server_name'])
        if self.errmsg:
            logging.info('[Error][wlaninfo --all-auth]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_PMK(self):
        self._configAuthenServer()
        self.wlan_cfg.update({'auth': 'EAP',
                              'wpa_ver': 'WPA2',
                              'encryption': 'TKIP',
                              'key_string' : '',
                              'auth_svr': self.auth_server['server_name'],
                              'username': 'ras.eap.user',
                              'password': 'ras.eap.user',
                              'use_radius':  True})

        self._configWLAN()
        time.sleep(2)
        self._verifyStationConnection()
        if self.errmsg:
            raise Exception(self.errmsg)

        self.passmsg, self.errmsg = tmdcli.test_show_pmk_info(self.zd_cli)
        if self.errmsg:
            logging.info('[Error][wlaninfo --pmk-cache]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_Mesh_AP(self):
        mesh_ap_list = self._collectMeshAP()

        self.passmsg, self.errmsg = tmdcli.test_show_mesh_ap(self.zd_cli, mesh_ap_list)
        if self.errmsg:
            logging.info('[Error][wlaninfo --mesh-ap]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_Mesh_Topology(self):
        mesh_ap_list = self._collectMeshAP()

        self.passmsg, self.errmsg = tmdcli.test_mesh_topology(self.zd_cli, mesh_ap_list)
        if self.errmsg:
            logging.info('[Error][wlaninfo --mesh-topology]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_Mesh_History(self):
        mesh_ap_list = self._collectMeshAP()

        self.passmsg, self.errmsg = tmdcli.test_mesh_history(self.zd_cli, mesh_ap_list)
        if self.errmsg:
            logging.info('[Error][wlaninfo --mesh-history]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_WLANGroup(self):
        self.passmsg, self.errmsg = tmdcli.test_show_wlan_group(self.zd_cli, 'Default')
        if self.errmsg:
            logging.info('[Error][wlaninfo --all-wlangroup: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_APGroup(self):
        self.passmsg, self.errmsg = tmdcli.test_show_ap_group(self.zd_cli)
        if self.errmsg:
            logging.info('[Error][wlaninfo --all-apgroup]: %s' % self.errmsg)
            return

    def _testCommandWLANINFO_DISC_AP(self):
        all_disc_ap = self._collectAPByStatus('Disconnected')
        if all_disc_ap:
            expected_ap = all_disc_ap[0]
        else:
            expected_ap = ''

        self.passmsg, self.errmsg = tmdcli.test_show_disc_ap(self.zd_cli, expected_ap)
        if self.errmsg:
            logging.info('[Error][wlaninfo --mesh-history]: %s' % self.errmsg)
            return

    def _testCommandAPMGRINFO_A(self):
        self.passmsg, self.errmsg = tmdcli.test_display_ap_info(self.zd, self.zd_cli)
        if self.errmsg:
            logging.info('[Error][apmgrinfo -a]: %s' % self.errmsg)
            return

    def _testCommandAPMGRINFO_P(self):
        self.passmsg, self.errmsg = tmdcli.test_ping_ap_mgr(self.zd_cli)
        if self.errmsg:
            logging.info('[Error][apmgrinfo -p]: %s' % self.errmsg)
            return

    def _testCommandSTP(self):
        self.passmsg, self.errmsg = tmdcli.test_setting_stp(self.zd_cli)
        if self.errmsg:
            logging.info('[Error][stp]: %s' % self.errmsg)
            return

    def _testCommandUPNP(self):
        self.passmsg, self.errmsg = tmdcli.test_setting_upnp(self.zd_cli)
        if self.errmsg:
            logging.info('[Error][stp]: %s' % self.errmsg)
            return

    def _testCommandPing(self):
        self.passmsg, self.errmsg = tmdcli.test_ping_command(self.zd_cli, self.zd.ip_addr)
        if self.errmsg:
            logging.info('[Error][ping]: %s' % self.errmsg)
            return

    def _test_command_show_ap(self):
        self.passmsg, self.errmsg = tmdcli.test_command_show_ap(self.zd, self.zd_cli)
        if self.errmsg:
            logging.info('[Error][show ap]: %s' % self.errmsg)
            return

    def _test_command_show_station(self):
        self._configWLAN()
        self._verifyStationConnection()
        if self.errmsg:
            raise Exception(self.errmsg)

        sta_info = (self.sta_wifi_mac_addr.lower(), self.sta_wifi_ip_addr)
        self.passmsg, self.errmsg = tmdcli.test_command_show_station(self.zd_cli, [sta_info])
        if self.errmsg:
            logging.info('[Error][show station]: %s' % self.errmsg)
            return

    def _cfgTargetStation(self):
        if not self.conf['target_station']:
            return
        # Find the target station object and remove all Wlan profiles on it
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                                                       , self.testbed.components['Station']
                                                       , check_status_timeout = self.conf['check_status_timeout']
                                                       , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _verifyStationConnection(self):
        """
        """
        tmethod.assoc_station_with_ssid(self.target_station, self.wlan_cfg,
                                     self.conf['check_status_timeout'], self.conf['break_time'])

        val, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.conf['check_status_timeout'])
        if not val:
            self.errmsg = val2
        else:
            self.sta_wifi_ip_addr, self.sta_wifi_mac_addr = val1, val2

    def _configAuthenServer(self):
        lib.zd.aaa.create_server(self.zd, **self.auth_server)

    def _configAccountingServer(self):
        lib.zd.aaa.create_server(self.zd, **self.acct_server)

    def _configWLAN(self):
        lib.zd.wlan.create_wlan(self.zd, self.wlan_cfg)

    def _create_user(self):
        self.zd.create_user(self.user_cfg['username'], self.user_cfg['password'])

    def _collectExpectedInfoOnWebUI(self):
        vap_in_webui = []
        for ap in self.testbed.components['AP']:
            ap_info_wlans = lib.zd.aps.get_ap_detail_wlans_by_mac_addr(self.zd, ap.base_mac_addr, 'bssid')
            for (wlan, wlan_info) in ap_info_wlans.iteritems():
                vap_in_webui.append((wlan_info['wlan'], wlan_info['bssid']))
        logging.debug("VAP in WebUI: %s" % vap_in_webui)
        return vap_in_webui

    def _collectAPByStatus(self, expected_status):
        ap_list = []
        all_ap_info_in_webui = self.zd.get_all_ap_info()
        for ap in all_ap_info_in_webui:
            if ap['status'] == expected_status:
                ap_list.append(ap['mac'])

        return ap_list

    def _collectMeshAP(self):
        mesh_ap_list = []
        mesh_ap_list.extend(self._collectAPByStatus('Connected (Root AP)'))
        mesh_ap_list.extend(self._collectAPByStatus('Connected (Mesh AP, 1 hop)'))
        mesh_ap_list.extend(self._collectAPByStatus('Connected (Root AP, 2 hops)'))

        return mesh_ap_list

    def get_station_download_ip_addr(self, vlan_id="301"):
        vlan_ip_table = self.testbed.components['L3Switch'].get_vlan_ip_table()
        ip_addr = [ ll['ip_addr'] for ll in vlan_ip_table if ll['vlan_id'] == vlan_id]
        return ".".join("".join(ip_addr).split(".")[:-1]) + ".50"

