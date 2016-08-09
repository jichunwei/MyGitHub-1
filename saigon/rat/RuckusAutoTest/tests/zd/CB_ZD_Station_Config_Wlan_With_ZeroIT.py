"""
"""

import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils

class CB_ZD_Station_Config_Wlan_With_ZeroIT(Test):
    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        try:
            logging.info("From the client, get the prov.exe file and run it")
            self._cfg_wlan_with_zero_it()
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
            self.errmsg = "Unable to get MAC address of the wireless adapter of the target station %s" % \
                  self.target_station.get_ip_addr()
            raise Exception(self.errmsg)
        if not sta_wifi_ip_addr:
            self.errmsg = "Unable to get IP address of the wireless adapter of the target station %s" % \
                  self.target_station.get_ip_addr()
            raise Exception(self.errmsg)
        if sta_wifi_ip_addr == "0.0.0.0" or sta_wifi_ip_addr.startswith("169.254"):
            self.errmsg = "The target station %s could not get IP address from DHCP server" % \
                  self.target_station.get_ip_addr()

        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            self.passmsg = 'Associate station [%s] successfully via Zero IT.' % self.conf['sta_tag']
            return self.returnResult('PASS', self.passmsg)
                
    def cleanup(self):
        pass

    def _get_station_download_ip_addr(self, vlan_id="301"):
        vlan_ip_table = self.testbed.components['L3Switch'].get_vlan_ip_table()
        ip_addr = [ ll['ip_addr'] for ll in vlan_ip_table if ll['vlan_id'] == vlan_id]
        return ".".join("".join(ip_addr).split(".")[:-1]) + ".50"

    def _init_test_parameters(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        
        self.conf = {'sta_tag': '',
                     'wlan_cfg': '',
                     'check_status_timeout': 120}
        self.conf.update(conf)
        
        self.check_status_timeout = self.conf['check_status_timeout']
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        self.zd = self.testbed.components['ZoneDirector']
        
        # Mar 2012, An Nguyen modified to let the script use the wlan configuration from carrier bag
        if self.conf.get('wlan_cfg'):
            self.wlan_cfg = self.conf['wlan_cfg']
        elif self.conf.get('wlan_ssid'):
            self.wlan_cfg = self.carrierbag[self.conf['wlan_ssid']]
        else:
            raise Exception('WLAN configuration parameter is not exist. Please check!')
         
        self.activate_url = self.zd.get_zero_it_activate_url()

        self.sta_ip_addr = self._get_station_download_ip_addr()

        self.zd_ip_addr = self.testbed.components['ZoneDirector'].ip_addr
        self.sta_net_mask = utils.get_subnet_mask(self.zd_ip_addr, False)
        
    def _update_carrier_bag(self):
        sta_wifi_ip_addr, sta_wifi_mac_addr = self.target_station.get_wifi_addresses()
        self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr'] = sta_wifi_mac_addr
        self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr'] = sta_wifi_ip_addr
        self.carrierbag[self.conf['sta_tag']]['authen'] = 'zeroit'

    def _cfg_wlan_with_zero_it(self):
        logging.info('Configure WLAN with Zero-IT application to station')
        
        self.target_station.cfg_wlan_with_zero_it(self.target_station.get_ip_addr(), self.sta_ip_addr,
                                    self.sta_net_mask, self.wlan_cfg['auth'], self.wlan_cfg['use_radius'],
                                    self.activate_url, self.wlan_cfg['username'], self.wlan_cfg['password'],
                                    self.wlan_cfg['ssid'])
                    
        self.passmsg = 'Configure Zero-IT application successfully on %s.' % (self.conf['sta_tag'],)         
        
    