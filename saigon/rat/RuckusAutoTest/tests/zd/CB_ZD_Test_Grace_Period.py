'''
Description:
    This script is used to test the grace period functionality.

Procedure:
    +Synchronize the time of ZD with test agent.
    +Clear all events from ZD.
    +Disconnect the client.
    +Get the disconnect time from ZD GUI -> Monitor -> All Events/Activities page.
    +Wait or change ZD system time to expire grace period.
    +Configure the WLAN profile on client.
    +Check client connect status.
    +Renew WIFI address in client.
    +Check client information ZD GUI -> Monitor -> Currently Active Clients page.
    +Verify client MAC in the MAC table of L3Switch if tunnel mode is enabled in WLAN.
    +Verify the traffic from client a target IP.
    +Check event log in ZD GUI -> Monitor -> Currently Active Clients page.
    
Create on 2011-12-14
@author: serena.tan@ruckuswireless.com
'''


import logging
import time
import datetime
import os
from copy import deepcopy
import re

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig


class CB_ZD_Test_Grace_Period(Test):
    required_components = ['ZoneDirector', 'Station', 'AP']
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        try:
            if self.conf['disconnect_from_wlan']:
                self.zd.get_current_time(True)
                time.sleep(5)

            if self.conf['clear_events']:
                self.zd.clear_all_events()
                self.passmsg += 'Clear all events from ZD successfully.'
            time.sleep(2)
            if self.conf['disconnect_from_wlan']:
                if self.conf['disconnect_method'] == 'remove_profiles_on_client':
                    self.remove_all_wlan_from_station()
                    time.sleep(2)
                    timeout = 3
                    while True:
                        time.sleep(1)
                        timeout = timeout - 1
                        if tmethod.get_active_client_by_mac_addr(self.sta_wifi_mac, self.zd):
                            msg = "Found info of client[%s] in ZD after removed all wlan profiles from the client." \
                                  % self.sta_wifi_mac
                            self.target_sta.disconnect_from_wlan()      
                            if timeout < 0:
                                raise Exception(msg)
                        else:
                            break
                
                elif self.conf['disconnect_method'] == 'delete_client_on_zd':
                    self.zd.delete_clients(self.sta_wifi_mac)
                
                else:
                    raise Exception("Wrong desconnect type: %s" % self.conf['disconnect_method'])
                
                self.get_disconnect_time()
                self.passmsg += 'Disconnect the client and get the disconnect time successfully.'
                
            if self.conf['expire_grace_period']:
                pass_sec = time.time() - self.disconnect_time
                logging.info("grace period is %s seconds, has pasted %s seconds" % (int(self.grace_period)*60,pass_sec))
                if self.conf['reconnect_within_gp']:
                    self.wait_sec = int(self.grace_period) * 60 - int(pass_sec)
                    self.wait_sec = self.wait_sec - self.conf['check_status_timeout']
                    self.wait_sec = self.wait_sec - self.conf['additional_exe_time']
                    
                else:
                    self.wait_sec = int(self.grace_period) * 60 - int(pass_sec)
                
                self.expire_grace_period()
                self.passmsg += 'Expire the grace period successfully.'
            
            if self.conf['reconnect_to_wlan']:
                self.config_wlan_on_station()
                self.passmsg += 'Reconnect to the WLAN successfully.'
            
            if self.conf['verify_connectivity']:
                errmsg = tmethod.check_station_is_connected_to_wlan(self.target_sta,
                                                                    self.conf['check_status_timeout'])
                if errmsg:
                    raise Exception(errmsg)
                
                self.renew_station_wifi_addr()
                self.check_station_status_on_zd()
                if self.conf['wlan_cfg'].get('do_tunnel'):
                    self.testbed.verify_station_mac_in_tunnel_mode(self.ap_mac, 
                                                                   self.sta_wifi_mac.lower(), 
                                                                   True)                                                            
                self.station_ping_target_ip()
                self.passmsg += 'Verify the client connectivity successfully.'
                
                self.check_event_log()
                self.passmsg += 'Verify the event log on ZD successfully.'
                
        except Exception, e:
            self.errmsg = e.message
        
        finally:
            if self.conf['expire_grace_period'] and self.wait_sec > 600:
                logging.debug("Restore the previous system time of ZD")
                tmptime = datetime.datetime.now() - datetime.timedelta(seconds = self.wait_sec)
                os.system("date %s-%s-%s" % (str(tmptime.month), str(tmptime.day), str(tmptime.year)))
                os.system("time %s:%s:%s" % (str(tmptime.hour), str(tmptime.minute), str(tmptime.second)))
                time.sleep(5)
                self.zd.get_current_time(True)
            
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
            
        self._update_carribag()
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
  
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'sta_tag': '',
                     'ap_tag': '',
                     'grace_period': None,
                     'reconnect_within_gp': True,
                     'no_need_auth': True,
                     'wlan_cfg': {},
                     'username': '',
                     'use_guestpass_auth': True,
                     'guest_name': '',
                     'radio_mode': '',
                     'target_ip': '172.16.10.252',
                     'ping_timeout_ms': 60 * 1000,
                     'check_status_timeout': 60,
                     'additional_exe_time': 3,
                     'clear_events': True,
                     'disconnect_from_wlan': True,
                     'disconnect_method': 'remove_profiles_on_client', #"delete_client_on_zd"
                     'expire_grace_period': True,
                     'reconnect_to_wlan': True,
                     'verify_connectivity': True,
                     }
        self.conf.update(conf)
        
        self.grace_period = self.conf['grace_period']
        self.no_need_auth = self.conf['no_need_auth']
        self.radio_mode = self.conf['radio_mode']
        #For radio mode is 'bg', need to set it to 'g'.
        if self.radio_mode == 'bg':
            self.radio_mode = 'g'

        self.zd = self.testbed.components['ZoneDirector']
        self.wait_sec = 0
        self.errmsg = ''
        self.passmsg = ''
        #@ZJ 20150410 ZF-12714
        self.ap_device_name = ''
        
    def _retrieve_carribag(self):
        if self.conf['ap_tag']:
            self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
            self.ap_mac = self.active_ap.base_mac_addr
            
        if self.conf['sta_tag']:
            self.target_sta = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        
        if self.conf['disconnect_from_wlan']:
            self.sta_wifi_mac = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
            
        if self.conf['expire_grace_period']:
            sta_tag = self.conf['sta_tag']
            ssid = self.conf['wlan_cfg']['ssid']
            if not self.grace_period and self.carrierbag.has_key('zd_grace_period'):
                self.grace_period = self.carrierbag['zd_grace_period']
           
            if self.carrierbag.has_key('sta_disconnect_time') \
            and self.carrierbag['sta_disconnect_time'].has_key(sta_tag) \
            and self.carrierbag['sta_disconnect_time'][sta_tag].has_key(ssid):
                self.disconnect_time = self.carrierbag['sta_disconnect_time'][sta_tag][ssid]
        
    def _update_carribag(self):
        if self.conf['disconnect_from_wlan']:
            sta_tag = self.conf['sta_tag']
            ssid = self.conf['wlan_cfg']['ssid']
            wlan_t = {}
            wlan_t[ssid] = self.disconnect_time
            if self.carrierbag.has_key("sta_disconnect_time"):
                if self.carrierbag['sta_disconnect_time'].has_key(sta_tag):
                    self.carrierbag['sta_disconnect_time'][sta_tag].update(wlan_t)
                
                else:
                    self.carrierbag['sta_disconnect_time'][sta_tag] = wlan_t
                    
            else:
                sta_t = {}
                sta_t[sta_tag] = wlan_t
                self.carrierbag['sta_disconnect_time'] = sta_t
        
        if self.conf['verify_connectivity']:
            self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr'] = self.sta_wifi_mac
            self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr'] = self.sta_wifi_ip
        
    def remove_all_wlan_from_station(self):
        logging.info("Disconnect the station by removing all WLANs profiles")
        tconfig.remove_all_wlan_from_station(self.target_sta, 
                                             check_status_timeout = self.conf['check_status_timeout'])
        
    def get_disconnect_time(self):
        if self.conf['wlan_cfg'].get('type') == 'guest':
            username = self.conf['guest_name']
        
        else:
            username = self.conf['username']
            
        if self.conf['disconnect_method'] == 'remove_profiles_on_client':
            #{user} disconnects from {wlan} at {ap}
            disconnect_msg = self.zd.messages['MSG_client_disconnect']
            
        elif self.conf['disconnect_method'] == 'delete_client_on_zd':
            #{user} disconnected by admin from {wlan} at {ap}
            disconnect_msg = self.zd.messages['MSG_client_del_by_admin']


        msg_split = disconnect_msg.split('with')
        disconnect_msg = msg_split[0].replace("{user}", "User[%s]" % username)
        disconnect_msg = disconnect_msg.replace("{wlan}", "WLAN[%s]" % self.conf['wlan_cfg']['ssid'])
        #@ZJ 20150410 ZF-12714 
        self.ap_device_name = self.active_ap.get_device_name()
        if self.ap_device_name and not self.ap_device_name == "RuckusAP" :
            disconnect_msg = disconnect_msg.replace("{ap}", "AP[%s]" % self.ap_device_name)
        else:
            disconnect_msg = disconnect_msg.replace("{ap}", "AP[%s]" % self.ap_mac)
        #    
        all_events = self.zd.get_events()
        disconnect_time_txt = ''
        #Updated by cwang@20120723, behavior change while do delete client action.
        for e in all_events:
            if disconnect_msg in e[3]:
                disconnect_time_txt = e[0]
                break
            #res = re.search(disconnect_msg, e[3], re.I)
            #if res:
            #    disconnect_time_txt = e[0]
            #    break
        
        if not disconnect_time_txt:
            raise Exception("There is no event log: %s" % disconnect_msg)
        
        logging.info("Station disconnect time: %s" % disconnect_time_txt)
        
        #disconnect_time_txt: u'2011/12/31  13:10:40'
        tmptime = time.strptime(disconnect_time_txt, "%Y/%m/%d  %H:%M:%S")
        self.disconnect_time = time.mktime(tmptime)
        
    def expire_grace_period(self):
        if self.wait_sec < 0:
            raise Exception("Already beyond the grace period")
        
        if self.wait_sec <= 600:
            logging.info('Wait for %s seconds' % self.wait_sec)
            time.sleep(self.wait_sec)
        
        else:
            if self.conf['reconnect_within_gp']:
                self.wait_sec = self.wait_sec - 20
                
            logging.info("Change the system time of ZD to add %s seconds" % self.wait_sec)
            tmptime = datetime.datetime.now() + datetime.timedelta(seconds = self.wait_sec)
            os.system("date %s-%s-%s" % (str(tmptime.month), str(tmptime.day), str(tmptime.year)))
            os.system("time %s:%s:%s" % (str(tmptime.hour), str(tmptime.minute), str(tmptime.second)))
            time.sleep(5)
            self.zd.get_current_time(True)
            
    def config_wlan_on_station(self):
        wlan_cfg = deepcopy(self.conf['wlan_cfg'])
        if (wlan_cfg.has_key("wpa_ver") and wlan_cfg['wpa_ver'] == "WPA_Mixed") or \
           (wlan_cfg.has_key("encryption") and wlan_cfg['encryption'] == "Auto"):
            wlan_cfg['wpa_ver'] = wlan_cfg['sta_wpa_ver']
            wlan_cfg['encryption'] = wlan_cfg['sta_encryption']
        
        logging.info("Configure a WLAN with SSID '%s' on the target station: %s" \
                     % (wlan_cfg['ssid'], self.target_sta.get_ip_addr()))
        self.target_sta.cfg_wlan(wlan_cfg)
        
    def renew_station_wifi_addr(self):
        res, var1, var2 = tmethod.renew_wifi_ip_address(
            self.target_sta, 
            self.conf['check_status_timeout']
            )
        
        if not res:
            raise Exception(var2)
        
        self.sta_wifi_ip = var1
        self.sta_wifi_mac = var2
        
    def check_station_status_on_zd(self):
        logging.info("Verify information of the target station shown on ZD")
        wlan_cfg = self.conf['wlan_cfg']
        if self.radio_mode == 'g' \
        or wlan_cfg['encryption'].upper() in ['TKIP', 'WEP-64', 'WEP-128','WEP64','WEP128']:
            expected_radio_mode = ['802.11b/g', '802.11a']
            
        else:
            expected_radio_mode = ['802.11ng', '802.11g/n', '802.11a/n', '802.11an']
        
        if self.no_need_auth:
            status = "Authorized"
            if wlan_cfg.get('web_auth') or wlan_cfg.get('do_webauth') \
            or wlan_cfg.get('type') == 'hotspot':
                exp_ip = self.conf['username']
            
            elif wlan_cfg.get('type') == 'guest':
                exp_ip = self.conf['guest_name'] if self.conf['use_guestpass_auth'] else 'guest'
            
            else:
                raise Exception("WLAN[%s] doesn't support grace period" \
                                % self.conf['wlan_cfg']['ssid'])
        
        else:
            status = "Unauthorized"
            exp_ip = self.sta_wifi_ip
            
        exp_client_info = {'wlan': self.conf['wlan_cfg']['ssid'],
                           'apmac': self.ap_mac,
                           "radio": expected_radio_mode,
                           'ip': exp_ip,
                           'status': status
                           }
        
        if wlan_cfg.get('vlan'):
            exp_client_info['vlan'] = wlan_cfg['vlan']
        
        errmsg, client_info = tmethod.verify_zd_client_status(self.zd, 
                                                              self.sta_wifi_mac,
                                                              exp_client_info,
                                                              self.conf['check_status_timeout'])
        
        if errmsg:
            raise Exception(errmsg)
        
        logging.info("The target station info on ZD is correct: %s" % client_info)
    
    def station_ping_target_ip(self):
        logging.info("Verify the connectivity of the target station")
        if self.no_need_auth:
            errmsg = tmethod.client_ping_dest_is_allowed(
                        self.target_sta, 
                        self.conf['target_ip'],
                        ping_timeout_ms = self.conf['ping_timeout_ms']
                        )
            
            if errmsg: 
                raise Exception(errmsg)
            
            msg = "The station can ping ip[%s] before doing authentication"
            logging.info(msg % self.conf['target_ip'])
            
        else:
            errmsg = tmethod.client_ping_dest_not_allowed(
                        self.target_sta, 
                        self.conf['target_ip'],
                        ping_timeout_ms = self.conf['ping_timeout_ms']
                        )
            
            if errmsg: 
                raise Exception(errmsg)
            
            msg = "The station can not ping ip[%s] before doing authentication"
            logging.info(msg % self.conf['target_ip'])

    def check_event_log(self):
        logging.info("Verify the Event Logs")
        all_logs = self.zd.get_events()

        #MSG_client_reconnect_within_grace_period=
        # {user} reconnects to {ap} within grace period. \
        # No additional authentication is required.

        msg = self.zd.messages['MSG_client_reconnect_within_grace_period']
        msg = msg.replace('  ', ' ')
        
        #@ZJ  ZF-12714 20150423
        self.ap_device_name = self.active_ap.get_device_name()
        if self.ap_device_name and not self.ap_device_name == "RuckusAP" :
            msg = msg.replace('{ap}', 'AP\[%s\]' % self.ap_device_name) 
        else:
            msg = msg.replace('{ap}', 'AP\[%s\]' % self.ap_mac)
          
        
#        msg = msg.replace('{ap}', 'AP\[%s\]' % self.ap_mac)
        
        if self.conf['wlan_cfg'].get('type') == 'guest':
            username = self.conf['guest_name']
        
        else:
            username = self.conf['username']
            
        msg_without_sta_mac = msg.replace('{user}', 'User\[%s\]' % username)
        msg_with_sta_mac = msg.replace('{user}', 'User\[%s@%s\]' % 
                                       (username, self.sta_wifi_mac))
        
        match = []
        for l in all_logs:
            if re.search(msg_without_sta_mac, l[3], re.I) and l[2] == username:
                match.append(l)
            
        # backward compability
        if not match:
            for l in all_logs:
                if re.search(msg_with_sta_mac, l[3], re.I) and l[2] == username:
                    match.append(l)
        
        if match:
            msg = "Found a log entry indicates that the station " \
                  "reconnects within grace period. "
            if self.no_need_auth:
                logging.info(msg)
            
            else:
                raise Exception(msg)

        else:
            errmsg = "There was no log entry to record the event that " \
                     "the station reconnects within grace period. "
            if self.no_need_auth:
                raise Exception(errmsg)
            
            else:
                logging.info(errmsg)
        
