'''
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify if the station could associate with WLANs and ping target IP.
'''

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_AP_Associate_Station_With_Wlans(Test):
    def config(self, conf):
        self._init_test_params(conf)    
        self._retrive_carrier_bag()    

    def test(self):
        self._associate_station_to_wlans()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(wlan_cfg_list = [],
                         target_station = "",
                         target_ip = '192.168.0.252',
                         check_status_timeout = 90,
                         ping_timeout = 60
                         )
        self.conf.update(conf)
        
        self.errmsg = ""
        self.passmsg = ""
        
    def _retrive_carrier_bag(self):
        self.sta_list = self.testbed.components['Station']
        if self.carrierbag.has_key('ap_fw_upgrade_cfg'):
            self.conf['ap_fw_upgrade_cfg'] = self.carrierbag['ap_fw_upgrade_cfg']
    
    def _update_carrier_bag(self):
        pass
        
 
    def _associate_station_to_wlans(self):
        '''
        Associate to specify wlans.
        '''
        logging.info('Starting associate to wlans')
        try:
            #Get station instance.
            target_station = self.sta_list[0]
            
            target_ip_list = []
            if self.conf.has_key('target_ip_list'):
                target_ip_list = self.conf['target_ip_list']
            else:
                if self.conf.has_key('ap_fw_upgrade_cfg'):
                    target_ip_list = self.conf['ap_fw_upgrade_cfg']['target_ip_list']
            
            wlans_cfg_list = self.conf['wlans_cfg_list']
            
            if not wlans_cfg_list:
                raise Exception("No wlan need to verify")
            
            all_err_dict = {}
            for wlan_cfg in wlans_cfg_list:
                res_ssid_dict = {}
                
                logging.info("Remove all WLANs from target station")
                tconfig.remove_all_wlan_from_station(target_station, check_status_timeout = self.conf['check_status_timeout'])
                
                #If wpa_ver is 'auto', will verify WPA and WPA2.
                if wlan_cfg['wpa_ver'].lower().find('auto') > -1:
                    is_wpa_auto = True
                    wpa_ver_list = ['WPA', 'WPA2']
                else:
                    is_wpa_auto = False
                    wpa_ver_list = [wlan_cfg['wpa_ver']]
                
                #If encryption is auto for wpa, verify TKIP and AES.
                if wlan_cfg['encryption'].lower() == 'auto' and wlan_cfg.has_key('wpa_ver'):
                    is_encrypt_auto = True
                    encrypt_list = ['TKIP', 'AES']                    
                else:
                    is_encrypt_auto = False
                    encrypt_list = [wlan_cfg['encryption']]
                    
                #Associate to wlans.
                for wpa_ver in wpa_ver_list:
                    wlan_cfg['wpa_ver'] = wpa_ver
                    for encrypt in encrypt_list:
                        wlan_cfg['encryption'] = encrypt    
                        logging.info('Verify station [%s] associate to wlan %s' % (target_station.get_ip_addr(), wlan_cfg))
                        
                        res_wlan = self._sta_assoc_and_ping(target_station, wlan_cfg, target_ip_list)
                        if res_wlan:
                            #Generate the key for error dict.
                            err_key = ''
                            if is_wpa_auto:
                                err_key = err_key + 'WPA-Auto:'
                            if is_encrypt_auto:
                                err_key = err_key + 'Auto:'
                            err_key = err_key + '%s-%s' % (wpa_ver, encrypt)
                            res_ssid_dict[err_key] = res_wlan       
                    
                if res_ssid_dict:
                    logging.warning('Associate wlans failed: %s' % (res_ssid_dict,))
                    all_err_dict[wlan_cfg['ssid']] = res_ssid_dict
                    
            if wlans_cfg_list:
                ssid_list = [wlan_cfg['ssid'] for wlan_cfg in wlans_cfg_list]
            else:
                ssid_list = []
                
            self.passmsg = "Client associate with wlan %s and ping target IP [%s] successfully" % (ssid_list, target_ip_list)
            
            self.errmsg = all_err_dict
        
        except Exception, ex:
            self.errmsg = ex.message
            
    def _sta_assoc_and_ping(self, target_station, wlan_cfg, target_ip_list):
        '''
        Use station assoicate to wlan based on configuration and ping target ip list.
        '''
        res_wlan = {}                                     
        res_assoc_wlan = tmethod.assoc_station_with_ssid(target_station, wlan_cfg, self.conf['check_status_timeout'])
                                
        if res_assoc_wlan:
            logging.warning('Associate wlan [%s] failed: %s' % (wlan_cfg['ssid'], res_wlan))                                 
            res_wlan['Associate'] = res_assoc_wlan
            
        #Wait for some minutes then to do ping.
        time.sleep(20)
            
        res_ping = {}
        for target_ip in target_ip_list:
            logging.info('Ping target IP address: %s' % (target_ip,))
            res_ping_target_ip = tmethod.client_ping_dest_is_allowed(target_station,target_ip,
                                                                     ping_timeout_ms = self.conf['ping_timeout'] * 1000)
            if res_ping_target_ip: 
                logging.warning('Ping %s failed: %s' % (target_ip, res_ping_target_ip)) 
                res_ping[target_ip] = res_ping_target_ip
                
        if res_ping:
            res_wlan['Ping'] = res_ping
            
        return res_wlan