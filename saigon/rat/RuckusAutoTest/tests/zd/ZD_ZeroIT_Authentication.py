# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_ZeroIT_Authentication Test class verifies if the feature zero-it against ras/ad server
             was implemented correctly.

Product Line: ZoneDirector

Test_bed_type: ZoneDirector Test Bed

References

Test_ID/Customer_bug_ID:
     - ZD_ZERO_IT_ACTIVATION_MISC_0002
     - ZD_ZERO_IT_ACTIVATION_MISC_0003

Pre-requisite:
     - Radius/Active Directory server must be available in the testbed.

Configuration and Parameters:
     {'ip': 'ip to ping from the client',
      'target_station': 'ip address of target station',
      'username':'username for zero-it activation',
      'password':'password for zero-it activation',
      'ras_ip_addr':'ip address of the radius server',
      'ras_port':'port of the radius server',
      'ras_secret':'secret of the radius server',
      'ad_ip_addr':'ip address of the Active Directory server',
      'ad_port':'port of the Active Directory server',
      'ad_domain':'domain name of the Active Directory server'}

Test Procedure:
     - Config:
         + Look for the target station and remove all WLAN(s) on that station.
         + On the ZoneDirector, remove all configuration .
     - Test:
         + On the Zone Director, create a WLAN with Zero-IT enabled.
         + On the Zone Director, create an authentication server.
         + On the Zone Director, choose an authentication server for Zero-IT Activation.
         + From the client, get the prov.exe and run it.
         + Make sure that the target station associates successfully.
         + Verify if the target station can get the IP and the MAC addresses.
         + Ping from the target station to the station with IP address 'ip',
           make sure that this ping succeeds.
     - Cleanup:
         + On the ZoneDirector, remove all configuration.
         + Remove all WLAN profiles on the target station. Make sure that it completely disconnects from the WLAN.

Observable Result:
     - The prov.exe file is run on the client.
     - The target asscociates and gets IP and MAC addresses and can ping to the station with 'ip'.
     - The target station disconnects from the WLAN.

Pass/Fail Criteria (including pass/fail messages)
     - The test case passes if all of the verification steps in the test case are met.

How it was tested:
     -

"""

import os
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.common import Ratutils as utils

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_ZeroIT_Authentication(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'ip': 'ip to ping from the client',
                           'target_station': 'ip address of target station',
                           'username':'username for zero-it activation',
                           'password':'password for zero-it activation',
                           'ras_ip_addr':'ip address of the radius server',
                           'ras_port':'port of the radius server',
                           'ras_secret':'secret of the radius server',
                           'ad_ip_addr':'ip address of the Active Directory server',
                           'ad_port':'port of the Active Directory server',
                           'ad_domain':'domain name of the Active Directory server'}

    def config(self, conf):
        # Testing parameters
        self.wlan_cfg = {'username': '', 'sta_auth': 'open', 'ras_port': '', 'key_index': '', 'auth': 'open',
                         'sta_encryption': 'none', 'ras_addr': '', 'password': '', 'ad_domain': '',
                         'ad_port': '', 'ssid': 'zero_it_activation_with_auth', 'key_string': '',
                         'sta_wpa_ver': '', 'encryption': 'none', 'ad_addr': '', 'wpa_ver': '',
                         'ras_secret': '', 'use_radius':False , 'use_zero_it':True}
        self.ping_timeout = 150
        self.check_status_timeout = 120
        self.conf = conf
        self.zd_ip_addr = self.testbed.components['ZoneDirector'].ip_addr
        self.sta_ip_addr = self.get_station_download_ip_addr()
        self.sta_net_mask = utils.get_subnet_mask(self.zd_ip_addr, False)

        logging.info("Get the zero-it activation url.")
        self.activate_url = self.testbed.components['ZoneDirector'].get_zero_it_activate_url()

        logging.info("Find the target station object and remove all Wlan profiles ")
        self.target_station = None
        for station in self.testbed.components['Station']:
            if station.get_ip_addr() == conf['target_station']:
                # Target station is found.
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
                break
        if not self.target_station:
            raise Exception("Target station %s not found" % conf['target_station'])

        logging.info("Remove all configuration on the Zone Director")
        #self.testbed.components['ZoneDirector'].remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

    def test(self):
        logging.info("Configure a WLAN with SSID %s on the Zone Director" % self.wlan_cfg['ssid'])
        self.testbed.components['ZoneDirector'].cfg_wlan(self.wlan_cfg)

        try:
            if self.conf['ras_ip_addr']:
                logging.info("Create a radius authentication server.")
                self.testbed.components['ZoneDirector'].create_radius_server(self.conf['ras_ip_addr'],
                                                                     self.conf['ras_port'], self.conf['ras_secret'])

                logging.info("Choose radius authentication server for Zero-IT Activation.")
                self.testbed.components['ZoneDirector'].set_zero_it_cfg(self.conf['ras_ip_addr'])

            elif self.conf['ad_ip_addr']:
                logging.info("Create an Active Directory authentication server.")
                self.testbed.components['ZoneDirector'].create_ad_server(self.conf['ad_ip_addr'],
                                                                 self.conf['ad_port'], self.conf['ad_domain'])

                logging.info("Choose Active Directory authentication server for Zero-IT Activation.")
                self.testbed.components['ZoneDirector'].set_zero_it_cfg(self.conf['ad_ip_addr'])
        except Exception, e:
            logging.info(e.message)
            return ("FAIL", e.message)
        
        try:
            logging.info("From the client, get the prov.exe file and run it")
            self.target_station.cfg_wlan_with_zero_it(self.target_station.get_ip_addr(), self.sta_ip_addr,
                                                     self.sta_net_mask, self.wlan_cfg['auth'], self.wlan_cfg['use_radius'],
                                                     self.activate_url, self.conf['username'], self.conf['password'],
                                                     self.wlan_cfg['ssid'])
        except Exception, e:
            if e.message.startswith('ERROR: Invalid username or password given'):
                msg = "Invalid username or password given or there is no authentication server in the testbed"
                raise Exception(msg)
            else:
                raise Exception(e.message)

        logging.info("Make sure the station associates to the WLAN")
        start_time = time.time()
        while True:
            if self.target_station.get_current_status() == "connected":
                break
            time.sleep(1)
            if time.time() - start_time > self.check_status_timeout:
                msg = "The station did not associate to the wireless network within %d seconds" % \
                      self.check_status_timeout
                raise Exception(msg)

        logging.info("Renew IP address of the wireless adapter on the target station")
        self.target_station.renew_wifi_ip_address()

        logging.info("Get IP and MAC addresses of the wireless adapter on the target station %s" %
                     self.target_station.get_ip_addr())
        start_time = time.time()
        sta_wifi_ip_addr = None
        sta_wifi_mac_addr = None
        while time.time() - start_time < self.check_status_timeout:
            sta_wifi_ip_addr, sta_wifi_mac_addr = self.target_station.get_wifi_addresses()
            if sta_wifi_mac_addr and sta_wifi_ip_addr and sta_wifi_ip_addr != "0.0.0.0":
                break
            time.sleep(1)
        logging.debug("Wifi IP: %s ---- Wifi MAC: %s" % (sta_wifi_ip_addr, sta_wifi_mac_addr))
        if not sta_wifi_mac_addr:
            msg = "Unable to get MAC address of the wireless adapter of the target station %s" % \
                  self.target_station.get_ip_addr()
            raise Exception(msg)
        if not sta_wifi_ip_addr:
            msg = "Unable to get IP address of the wireless adapter of the target station %s" % \
                  self.target_station.get_ip_addr()
            raise Exception(msg)
        if sta_wifi_ip_addr == "0.0.0.0" or sta_wifi_ip_addr.startswith("169.254"):
            msg = "The target station %s could not get IP address from DHCP server" % \
                  self.target_station.get_ip_addr()
            return ("FAIL", msg)

        logging.info("Ping to %s from the target station (timeout: %s)." %
                     (self.conf['ip'], self.ping_timeout))
        ping_result = self.target_station.ping(self.conf['ip'], self.ping_timeout * 1000)
        if ping_result.find("Timeout") != -1:
            logging.info("Ping FAILED. Incorrect behavior")
            return ("FAIL", "The target station could not send traffic to the station '%s'." %
                    self.conf['ip'])
        else:
            logging.info("Ping OK. Correct behavior!")

        return ("PASS", "")

    def cleanup(self):
        logging.info("Remove all configuration on the Zone Director.")
        #self.testbed.components['ZoneDirector'].remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        if self.target_station:
            logging.info("Remove all WLAN profiles on the target station")
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

    def get_station_download_ip_addr(self, vlan_id="301"):
        vlan_ip_table = self.testbed.components['L3Switch'].get_vlan_ip_table()
        ip_addr = [ ll['ip_addr'] for ll in vlan_ip_table if ll['vlan_id'] == vlan_id]
        return ".".join("".join(ip_addr).split(".")[:-1]) + ".50"
