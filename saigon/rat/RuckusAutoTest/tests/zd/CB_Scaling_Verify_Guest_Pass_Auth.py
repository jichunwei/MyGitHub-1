'''
Description:Perform Guest Pass Auth from station.
Created on 2010-9-20
@author: cwang@ruckuswireless.com
'''
import logging
import random
import time
from copy import deepcopy

from RuckusAutoTest.models import Test
import libZD_TestConfig as tconfig
import libZD_TestMethods as tmethod

class CB_Scaling_Verify_Guest_Pass_Auth(Test):
    '''
    Verify the first, random, last guest passes if can authenticate.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        f_gp_cfg = self.gp_cfg_list[1]
        res = self._chk_gp_w_sta(f_gp_cfg)
        if not res:
            return self.returnResult("FAIL", "Do guest pass authenticate failure [%s]" % f_gp_cfg)
        
        l_gp_cfg = self.gp_cfg_list[-1]
        res = self._chk_gp_w_sta(l_gp_cfg)
        if not res:
            return self.returnResult("FAIL", "Do guest pass authenticate failure [%s]" % f_gp_cfg)
        
        index = random.randrange(2, len(self.gp_cfg_list)-1)
        rnd_gp_cfg = self.gp_cfg_list[index]
        res = self._chk_gp_w_sta(rnd_gp_cfg)
        if not res:
            return self.returnResult("FAIL", "Do guest pass authenticate failure [%s]" % f_gp_cfg)
        
        self._update_carrier_bag()
        return self.returnResult('PASS', 'Guest Passes [%s, %s, %s] authenticate successfully' % (f_gp_cfg, rnd_gp_cfg, l_gp_cfg))
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.gp_cfg_list = self.carrierbag['existed_guest_passes_record']
        self.target_station = self.carrierbag['station']
        
    
    def _update_carrier_bag(self):
        pass
    
    
    def _init_test_params(self, conf):
        self.conf = dict(check_status_timeout = 100,
                         use_tou = False,
                         redirect_url = '')
        self.conf.update(conf)
        self.wlan_cfg = self.conf['wlan_cfg']
        self.check_status_timeout = self.conf['check_status_timeout']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''


    def _assoc_sta_w_ssid(self):
        wlan_cfg = deepcopy(self.wlan_cfg)
        if self.wlan_cfg.has_key("wpa_ver") and self.wlan_cfg['wpa_ver'] == "WPA_Mixed":
            wlan_cfg['wpa_ver'] = wlan_cfg['sta_wpa_ver']
            wlan_cfg['encryption'] = wlan_cfg['sta_encryption']
       
        self.errmsg = tmethod.assoc_station_with_ssid(self.target_station, wlan_cfg, self.conf['check_status_timeout'])
        if self.errmsg:
            self.errmsg = tmethod.verify_wlan_in_the_air(self.target_station, wlan_cfg['ssid'])

        start_time = time.time()

        while time.time() - start_time < self.conf['check_status_timeout']:
            self.sta_wifi_ip_addr, self.sta_wifi_mac_addr = self.target_station.get_wifi_addresses()
            if self.sta_wifi_mac_addr and self.sta_wifi_ip_addr and self.sta_wifi_ip_addr != "0.0.0.0" and \
               not self.sta_wifi_ip_addr.startswith("169.254"):
                break

            time.sleep(1)


    def _rm_wlan_from_sta(self):
        try:
            tconfig.remove_all_wlan_from_station(self.target_station, check_status_timeout = self.conf['check_status_timeout'])       
        except Exception, e:
            self.errmsg = '[Removing wlan from target station failed] %s' % e.message
            logging.error(self.errmsg)


    def _chk_gp_w_sta(self, gp_cfg):
        time.sleep(2)
        self.zd.remove_all_active_clients()
        self.zd.refresh()        
#        import pdb
#        pdb.set_trace()        
        self._rm_wlan_from_sta()
        if self.errmsg:
            return False        
#        time.sleep(2)        
        self._assoc_sta_w_ssid()
        if self.errmsg:
            logging.error(self.errmsg)
            return False
#        time.sleep(2)
        guest_pass = gp_cfg[1]
        self._perform_gp_auth(guest_pass)
        
        return True


    def _perform_gp_auth(self, guest_pass = ''):
        logging.info("Perform Guest Pass authentication on the target station %s" % self.target_station.get_ip_addr())
        time.sleep(5)

        arg = tconfig.get_guest_auth_params(self.zd, guest_pass, self.conf['use_tou'], self.conf['redirect_url'])
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
                    return False

                if not client_info_on_zd:
                    logging.debug("Active Client list: %s" % str(active_client_list))
                    errmsg = "ZD didn't show any info about the target station (with MAC %s). " % self.sta_wifi_mac_addr
                    self.errmsg = self.errmsg + errmsg
                    logging.debug(errmsg)
                    return False  
                        
        return True