import time
import logging
import tempfile

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.Ratutils import *
from libIPTV_TestConfig import *
from libIPTV_TestMethods import *

class IPTV_NonIP_Packet(Test):
    required_components = ['RuckusAP', 'StationLinuxPC']
    parameter_description = {'active_ap':'',
                             'remote_station':'',
                             'local_station':'',
                             'verify_stp':'',
                             'verify_lwapp':'',
                             'verify_eapol':''}

    def config(self, conf):

        if conf.has_key('verify_stp'):
            self.verify_stp = conf['verify_stp']
            self.stp_packet_replay = conf['stp_packet_replay']
        else: self.verify_stp = False

        if conf.has_key('verify_lwapp'):
            self.verify_lwapp = conf['verify_lwapp']
            self.lwapp_packet_replay = conf['lwapp_packet_replay']
        else: self.verify_lwapp = False

        if conf.has_key('verify_eapol'):
            self.verify_eapol = conf['verify_eapol']
            self.eapol_packet_replay = conf['eapol_packet_replay']
        self.verify_eapol = False
        self.queue = conf['queue']
        self.wlan_if = conf['wlan_if']
        self.ap_channel = conf['ap_channel']

        self._getStations(conf)
        self._get_ip_addrs(conf)

        logging.info("Find the active AP object")
        self.active_ap = getTestbedActiveAP(self.testbed,
                                            conf['active_ap'],
                                            self.testbed.components['AP'],
                                            self.ap_channel,
                                            self.wlan_if)

        logging.info("Get active adapter configuration information")
        self.ad_config = getADConfig(self.testbed, conf['active_ad'], self.testbed.ad_list)

        self.ad_model = self.remote_station.get_ad_device_type(self.ad_config)
        self.ad_mac = self.remote_station.get_ad_wireless_mac(self.ad_config)

        logging.info("Save encryption information")
        self.current_ap_encryption = self.active_ap.get_encryption(self.wlan_if)
        self.current_ap_encryption['wlan_if'] = self.wlan_if

        self.current_ad_encryption = self.remote_station.get_ad_encryption(self.ad_config, 'wlan0')
        self.current_ad_encryption['wlan_if'] = 'wlan0'

    def test(self):
        wlan_cfg = dict(auth="PSK",
                        wpa_ver="WPA",
                        encryption="AES",
                        key_string="AES_12345678",
                        ssid='IPTV',
                        wlan_if='%s' % self.wlan_if)
        logging.info("Configure a WLAN with SSID %s on the active AP" % wlan_cfg['ssid'])
        self.active_ap.cfg_wlan(wlan_cfg)

        ad_wlan_cfg = wlan_cfg.copy()
        ad_wlan_cfg['wlan_if'] = 'wlan0'
        logging.info("Configure a WLAN with SSID %s  on the active adapter" % wlan_cfg['ssid'])
        self.remote_station.cfg_wlan(self.ad_config, ad_wlan_cfg)

        logging.info("Turn on svcp interface on this adapter")
        self.remote_station.set_ruckus_ad_state(self.ad_config, 'up', 'wlan0')
        if self.ad_model.lower() == 'vf7111': time.sleep(60)
        else: time.sleep(2)

        # Verify connection between stations
        verifyStaConnection(self.local_station, self.local_sta_ip_addr, self.remote_sta_ip_addr)

        logging.info("Clear media queue statistics on the active ap")
        self.active_ap.clear_mqstats(self.wlan_if)

        kind_of_traffic = ""
        if self.verify_stp:
            kind_of_traffic = "Spanning Tree"
            logging.info("Use tcpreplay to simulate sending Spanning Tree packets to network")
            self.local_station.start_tcp_replay(if_name = self.local_if_name,
                                              file_name = self.stp_packet_replay,
                                              rate = '0.5')

        if self.verify_eapol:
            kind_of_traffic = "EAPOL"
            logging.info("Use tcpreplay to simulate sending EAPOL packets to network")
            self.local_station.start_tcp_replay(if_name = self.local_if_name,
                                              file_name = self.eapol_packet_replay,
                                              rate = '0.5')

        if self.verify_lwapp:
            kind_of_traffic = "LWAPP"
            logging.info("Use tcpreplay to simulate sending LWAPP packets to network")
            self.local_station.start_tcp_replay(if_name = self.local_if_name,
                                              file_name = self.lwapp_packet_replay,
                                              rate = '0.5')
        time.sleep(2)

        # Get mq statistics
        ad_mqstats = getStaMQStatistics(self.active_ap, self.ad_mac, self.wlan_if)

        # Get traffic information on each queue
        queue_info, empty_queue_list, empty_deq = get_mqstatsInfo(ad_mqstats, self.queue)
        logging.info("Verify that %s packets will be inserted to the %s queue" % (kind_of_traffic, self.queue))
        res, msg = verifyMQStats(self.queue, queue_info, empty_queue_list, empty_deq, 2, self.ad_mac)
        if res == "FAIL":
            return [res, msg]

        return ["PASS", ""]

    def cleanup(self):
        if self.active_ap:
            logging.info("Down %s interface on the active AP" % self.wlan_if)
            self.active_ap.set_state(self.wlan_if, 'down')

            logging.info("Return the previous encryption for AP")
            self.active_ap.cfg_wlan(self.current_ap_encryption)

        if self.local_station and self.remote_station:
            logging.info("Down svcp interface on the active Adapter")
            self.remote_station.set_ruckus_ad_state(self.ad_config, 'down', 'wlan0')
            self.remote_station.cfg_wlan(self.ad_config, self.current_ad_encryption)

            verifyStaConnection(self.local_station,
                                self.local_sta_ip_addr,
                                self.remote_sta_ip_addr,
                                5000, False)

    def _getStations(self, conf):
        # Find exactly stations
        station_list = self.testbed.components['Station']
        self.remote_station = getStation(conf['remote_station'], station_list)
        self.local_station = getStation(conf['local_station'], station_list)

    def _get_ip_addrs(self, conf):

        self.ap_ip_addr = self.testbed.getAPIpAddrBySymName(conf['active_ap'])
        self.ad_ip_addr = self.testbed.getAdIpAddrBySymName(conf['active_ad'])

        # Find the ip address of interface that connected to the adapter on the local station and remote station
        self.local_sta_ip_addr, self.local_if_name = getLinuxIpAddr(self.local_station, self.testbed.sta_wifi_subnet, True)
        self.remote_sta_ip_addr = getLinuxIpAddr(self.remote_station, self.testbed.sta_wifi_subnet)

        if not self.local_sta_ip_addr or not self.remote_sta_ip_addr:
            raise Exception("Can not find any ip address belongs to subnet %s" % self.testbed.sta_wifi_subnet['network'])

