# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

'''
Description: Verify the downlink traffic go to the right media queue

Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:
   'active_ap' : Mac address of the active AP
   'target_sta' : target station IP address
   'tos' : ToS of the packets that will be sent
   'num_of_pkts' : Number of packet will be sent out
   'expect_queue' : The appropriate media queue with the ToS classify on AP

   Result type: PASS/FAIL
   Results:
   FAIL:
   - If the packet go to the wrong queue
   PASS:
   - All packet go to the right queue

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
         1. Config:
            - Create the associate between the ZD system with the target station via active AP
         2. Test procedure:
            - Send out traffic downlink with ToS
            - On AP check the traffic go to right queue or not.
         3. Cleanup:
            - Remove all configuration
            - Note: When cleanup test environment the active AP might be reboot by bug 1915, so we
            will reboot AP affter finish testing to make sure the next script will not be hang.
    How it was tested:
'''

import time
import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.models import Test

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_AP_TOS_Classification(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'target_station': 'ip address of target station',
                           'active_ap': 'mac address (NN:NN:NN:NN:NN:NN) of target ap which client will associate to',
                           'wlan_list': 'list of dictionary of encryption parameters'}

    def config(self, conf):
        self.zd = self.testbed.components['ZoneDirector']

        if conf.has_key('timeout'):
            self.timeout = conf['timeout']
        else:
            self.timeout = 180

        if conf.has_key('expect_result'):
            self.expect_result = conf['expect_result']
        else:
            self.expect_result = 95

        self.ap_cfg = None
        self.ap = None
        self.mac_addr = None
        self.target_station = None
        self.expect_queue = conf['expect_queue']
        self.expect_column = 'enq'
        self.num_of_pkts = conf['num_of_pkts']
        self.tos = conf['tos'].lower()
        self.run_time = conf['run_time'] if conf.get('run_time') else 30
        self.server = None

        # Starting the zing server
        # PHANNT@20100525:
        # re-use components['LinuxServer'] instead of creating a new one
        self.server = self.testbed.components['LinuxServer']
        self.server.re_init()
        self.host = self.server.ip_addr
        logging.info('Telnet to the server at IP address %s successfully' %
                     self.server.ip_addr)
        self.server.kill_zing()
        self.server.start_zing_server(tos = self.tos)

        self.test_wlan = dict(ssid = 'qos_test', auth = 'open', wpa_ver = '', encryption = 'none',
                   sta_auth = 'open', sta_wpa_ver = '', sta_encryption = 'none',
                   key_index = '' , key_string = '', username = '', password = '',
                   ras_addr = '', ras_port = '', ras_secret = '', use_radius = False)

        self.zd.remove_all_wlan()
        time.sleep(5)

        self.zd.cfg_wlan(self.test_wlan)
        logging.info('Create wlan \'%s\' for associate successfully' % self.test_wlan['ssid'])

        self._cfgActiveAP(conf)

        self._cfgTargetStation(conf)

    def test(self):
        # Check if we could ping from target station to server.
        if self.target_station.get_current_status() != 'connected':
            return 'FAIL', 'There no association between target station and ZD system'

        logging.info("Renew IP address of the wireless adapter on the target station")
        self.target_station.renew_wifi_ip_address()

        logging.info('Get IP and MAC addresses of the wireless adapter on the target station %s' %
                     self.target_station.get_ip_addr())

        start_time = time.time()
        sta_wifi_ip_addr = None
        sta_wifi_mac_addr = None
        while time.time() - start_time < self.timeout:
            sta_wifi_ip_addr, sta_wifi_mac_addr = self.target_station.get_wifi_addresses()
            if sta_wifi_mac_addr and sta_wifi_ip_addr and sta_wifi_ip_addr != '0.0.0.0':
                break

            time.sleep(1)

        logging.debug('Wifi IP: %s ---- Wifi MAC: %s' % (sta_wifi_ip_addr, sta_wifi_mac_addr))
        if not sta_wifi_mac_addr:
            raise Exception('Unable to get MAC address of the wireless adapter of the target station %s' %
                            self.target_station.get_ip_addr())

        elif not sta_wifi_ip_addr:
            raise Exception('Unable to get IP address of the wireless adapter of the target station %s' %
                            self.target_station.get_ip_addr())

        elif sta_wifi_ip_addr == '0.0.0.0' or sta_wifi_ip_addr.startswith('169.254'):
            raise Exception('The target station %s could not get IP address from DHCP server' %
                            self.target_station.get_ip_addr())

        logging.info("Verify information of the target station shown on the Zone Director")
        timed_out = False
        start_time = time.time()
        while True:
            all_good = True
            client_info_on_zd = None
            for client_info in self.zd.get_active_client_list():
                logging.debug("Found info of a station: %s" % client_info)
                if client_info['mac'].upper() == sta_wifi_mac_addr.upper():
                    client_info_on_zd = client_info
                    if client_info['status'] != 'Authorized':
                        if timed_out:
                            msg = "The station status shown on ZD was %s instead of 'Authorized'" % \
                                  client_info['status']
                            return ("FAIL", msg)

                        all_good = False
                        break

                    if client_info['ip'] != sta_wifi_ip_addr:
                        if timed_out:
                            msg = "The station wifi IP address shown on ZD was %s instead of %s" % \
                                  (client_info['ip'], sta_wifi_ip_addr)
                            return ("FAIL", msg)

                        all_good = False
                        break

            # End of for
            # Quit the loop if everything is good
            if client_info_on_zd and all_good: break
            # Otherwise, sleep
            time.sleep(1)
            timed_out = time.time() - start_time > self.timeout
            # And report error if the info is not available
            if not client_info_on_zd and timed_out:
                msg = "Zone Director didn't show any info about the target station while it had been associated"
                return ("FAIL", msg)

            # Or give it another try
        # End of while

        logging.info('Verify information of the target station shown on the AP %s' % self.ap.get_base_mac())
        start_time = time.time()
        station_list_on_ap = None
        while time.time() - start_time < self.timeout:
            station_list_on_ap = self.ap.get_station_list(self.wlan_name)
            if station_list_on_ap: break
            time.sleep(1)

        if not station_list_on_ap:
            return ('FAIL', 'AP %s didn\'t have any info about the stations' % self.ap.get_base_mac())

        found = False
        for sta_info in station_list_on_ap:
            if sta_info[0].upper() == sta_wifi_mac_addr.upper():
                if sta_info[1] == 0:
                    return ('FAIL', 'Target station\'s AID status is zero on the AP %s' % self.ap.get_base_mac())

                if sta_info[2] != client_info_on_zd['channel'] and sta_info[3] != client_info_on_zd['channel']:
                    return ('FAIL', 'Target station\'s channel info on AP (%s) is not %s as shown on ZD' %
                            (sta_info[2], client_info_on_zd['channel']))

                found = True
                break

        if not found:
            return ('FAIL', 'Not found station %s on the AP %s' % (sta_wifi_mac_addr, self.ap.get_base_mac()))

        # Send downlink traffic (use Zing)
        self.ap.clear_mqstats(self.wlan_name)
        logging.info('Clear the mqstats on interface %s of the active AP successfully' % self.wlan_name)
        logging.debug('MQSTATS Info: %s' % self.ap.get_media_queue_stats(self.wlan_name))

        traffic_result = self.target_station.send_zing(host = self.host, num_of_pkts = self.num_of_pkts,
                                                      tos = self.tos, sending_time = self.run_time)
        media_queue_info = self.ap.get_media_queue_stats(self.wlan_name)
        logging.info('Sent traffic from target station successfully')

        total_pkts_send_out = int(traffic_result['Batches']) * int(traffic_result['Batch Size'])
        logging.info('%s packets with %s tos bit set are send out' % (total_pkts_send_out, self.tos))


        logging.debug('MQSTATS Info: %s' % media_queue_info)
        num_of_pkts_go_to_media_queue = media_queue_info['%s_%s_%s' % (sta_wifi_mac_addr.lower(), self.expect_queue, self.expect_column)]
        pass_percent = float(int(num_of_pkts_go_to_media_queue) * 100) / float(total_pkts_send_out)
        logging.info('Number of packets go to the %s queue is %d'
                     % (self.expect_queue.upper(), int(num_of_pkts_go_to_media_queue)))

        if pass_percent < self.expect_result:
            msg = '[%s TOS Classification] There are %d [%0.2f %%] packets go to the %s queue'
            msg = msg % (self.expect_queue.upper(), int(num_of_pkts_go_to_media_queue),
                         pass_percent, self.expect_queue.upper())
            logging.info(msg)
            return ('FAIL', msg)

        else:
            msg = '[%s TOS Classification] There are %d [%0.2f %%] packets go to the %s queue'
            msg = msg % (self.expect_queue.upper(), int(num_of_pkts_go_to_media_queue),
                         pass_percent, self.expect_queue.upper())
            logging.info(msg)
            return ('PASS', msg)

    def cleanup(self):
        logging.info('Clean up environment')
        if self.server:
            self.server.close()

        if self.target_station:
            self.target_station.remove_all_wlan()
            logging.info("Make sure the target station disconnects from the wireless networks")
            start_time = time.time()
            current_time = start_time
            while current_time - start_time <= self.timeout:
                res = self.target_station.get_current_status()
                if res == "disconnected":
                    break

                time.sleep(5)
                current_time = time.time()

            if current_time - start_time > self.timeout:
                raise Exception("The station did not disconnect from wireless network within %d seconds" %
                                self.timeout)

        logging.info("Remove all the WLANs on the Zone Director")
        self.zd.remove_all_wlan()
        if self.mac_addr:
            self.zd.remove_approval_ap(self.mac_addr)

        # Reboot the active AP after remove all wlan. ( Working around to avoid bug 1915)
        if self.ap:
            self.ap.reboot()
            while True:
                try:
                    for ap_comp in self.testbed.components['AP']:
                        ap_comp.login()
                        logging.debug('%s' % ap_comp.get_base_mac())
                    break

                except:
                    time.sleep(10)

        # Verify if the APs is still connected on ZD
        start_time = time.time()
        timeout = 150
        while True:
            connected = 0
            aps_info = self.zd.get_all_ap_info()
            for ap in aps_info:
                if ap['status'].lower().startswith("connected"):
                    connected += 1

            if connected == len(self.testbed.components['AP']):
                break

            if time.time() - start_time > timeout:
                raise Exception("There are %d APs disconnecting from the ZD"
                                % (len(self.testbed.components['AP']) - connected))

            time.sleep(1)

        if self.ap_cfg:
            self.zd.set_ap_cfg(self.ap_cfg)

    def _cfgActiveAP(self, conf):
        self.ap = tconfig.get_testbed_active_ap(self.testbed, conf['active_ap'], "Active AP")
        self.mac_addr = self.ap.get_base_mac().lower()
        self.ap_cfg = self.zd.get_ap_cfg(self.mac_addr)
        self.wlan_name = self.ap.ssid_to_wlan_if(self.test_wlan['ssid'])
        for ap in self.testbed.components['AP']:
            if ap.get_base_mac().lower() != self.mac_addr:
                ap.remove_all_wlan()
                logging.info('Turn off all WLAN interfaces on the non-active AP (%s)' % ap.ip_addr)

    def _cfgTargetStation(self, conf):
        # Find the target station object and remove all Wlan profiles
        for station in self.testbed.components['Station']:
            if station.get_ip_addr() == conf['target_station']:
                # Found the target station
                self.target_station = station
                break

        if not self.target_station:
            raise Exception('Target station %s not found' % conf['target_station'])

        self.target_station.cfg_wlan(self.test_wlan)
        basetime = time.time()
        while True:
            if self.target_station.get_current_status() == 'connected':
                break

            if time.time() - basetime > 180:
                raise Exception("The station didn't associate to the system")

            time.sleep(5)

        logging.info('The station associated to the system successfully')

