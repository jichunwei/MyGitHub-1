'''
Description: 
    This script supplys several methods to disconnect client and get the
    disconnect time from ZD GUI -> Monitor -> All Events/Activities page.

Disconnect methods:
    1. Remove all wlan profiles on client.
    2. Delete client on ZD.
    3. Set the wlan group of a AP radio to Default.
    4. Delete client by radius server.
    5. Wait for session timeout.
    
Procedure:
    +Synchronize the time of ZD with test agent.
    +Clear all events from ZD.
    +Disconnect the client.
    +Get the disconnect time from ZD GUI -> Monitor -> All Events/Activities page.
    
Create on 2011-12-14
@author: serena.tan@ruckuswireless.com
'''


import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.components.lib.zd import access_points_zd as AP


class CB_ZD_Disconnect_Client(Test):
    required_components = ['ZoneDirector', 'Station', 'AP']
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        try:
            if self.conf['pause_before_disconnect']:
                logging.info("Wait for %s seconds" % self.conf['pause_before_disconnect'])
                time.sleep(self.conf['pause_before_disconnect'])
            
            logging.info("Synchronize ZD time with PC time.")
            self.zd.get_current_time(True)
            time.sleep(5)
            
            if self.conf['clear_events']:
                logging.info("Clear all events in ZD.")
                self.zd.clear_all_events()
                
            if self.conf['disconnect_method'] == 'remove_profiles_on_client':
                self.remove_all_wlan_profiles_from_station()
            
            elif self.conf['disconnect_method'] == 'delete_client_on_zd':
                logging.info("Delete client[%s] in ZD" % self.sta_wifi_mac_addr)
                self.zd.delete_clients(self.sta_wifi_mac_addr)
            
            elif self.conf['disconnect_method'] == 'set_wg_to_default':
                AP.assign_to_wlan_group(self.zd, 
                                        self.ap_mac,
                                        self.conf['radio_mode'], 
                                        'Default')
            
            elif self.conf['disconnect_method'] == 'delete_client_by_radius':
                self.disconnect_client_by_radius_server()
            
            elif self.conf['disconnect_method'] == 'wait_for_session_timeout':
                session_timeout = int(self.conf['session_timeout']) * 60
                logging.info("Wait %s seconds for client session timeout" % session_timeout)
                time.sleep(session_timeout)
        
            else:
                raise Exception("Wrong disconnect type: %s" % self.conf['disconnect_method'])
            
            self.get_disconnect_time()
            
        except Exception, ex:
            self.errmsg = ex.message
        
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
            
        self._update_carribag()
        
        self.passmsg = "Disconnect client[%s] from WLAN[%s] and get the disconnect time successfully." \
                       % (self.conf['sta_tag'], self.conf['wlan_cfg']['ssid'])
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
  
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        '''
        'disconnect_method': ['remove_profiles_on_client', 'delete_client_on_zd',
                             'set_wg_to_default', 'delete_client_by_radius',
                             'wait_for_session_timeout']
        '''
        self.conf = {'sta_tag': '',
                     'ap_tag': '',
                     'username': '',
                     'guest_name': '',
                     'wlan_cfg': {},
                     'radio_mode': '',
                     'clear_events': True,
                     'disconnect_method': 'remove_profiles_on_client',
                     'radius_share_secret': '',
                     'check_status_timeout': 30,
                     'pause_before_disconnect': 0,
                     'session_timeout': 0,
                     }
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        if self.conf['disconnect_method'] == 'delete_client_by_radius':
            self.linux_server = self.testbed.components['LinuxServer']
            self.radius_share_secret = self.conf['radius_share_secret']
            
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrieve_carribag(self):
        self.target_sta = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        self.sta_wifi_mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.ap_mac = self.active_ap.base_mac_addr
        
    def _update_carribag(self):
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
            
    def remove_all_wlan_profiles_from_station(self):
        logging.info("Disconnect the station by removing all WLANs profiles")
        tconfig.remove_all_wlan_from_station(self.target_sta, 
                                             check_status_timeout = self.conf['check_status_timeout'])
        time.sleep(3)
        timeout = 10
        while True:
            time.sleep(3)
            timeout = timeout - 3
            if tmethod.get_active_client_by_mac_addr(self.sta_wifi_mac_addr, self.zd):
                msg = "Found info of client[%s] in ZD after removed all wlan profiles from the client." \
                      % self.sta_wifi_mac_addr
                self.target_sta.disconnect_from_wlan()      
                if timeout < 0:
                    raise Exception(msg)
            else:
                break
    
    def disconnect_client_by_radius_server(self):
        cmd = "echo User-Name=%s | radclient -x %s:3799 disconnect %s" \
              % (self.conf['username'], self.zd.ip_addr, self.radius_share_secret)
        logging.info("Execute command in the radius server:\n%s" % cmd)
        self.linux_server.do_cmd(cmd)
    
    def get_disconnect_time(self):
        logging.info("Verify client disconnect event log and get the disconnect time in ZD events table.")
        if self.conf['wlan_cfg'].get('type') == 'guest':
            username = self.conf['guest_name']
        else:
            username = self.conf['username']
            
        if username == '':
            username = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
        
        if self.conf['disconnect_method'] == 'remove_profiles_on_client':
            #{user} disconnects from {wlan} at {ap}
            disconnect_msg = self.zd.messages['MSG_client_disconnect']
            disconnect_msg = disconnect_msg.replace("{user}", "User[%s]" % username)
            disconnect_msg = disconnect_msg.replace("{wlan}", "WLAN[%s]" % self.conf['wlan_cfg'].get('ssid'))
            disconnect_msg = disconnect_msg.replace("{ap}", "AP[%s]" % self.ap_mac)
        
        elif self.conf['disconnect_method'] == 'wait_for_session_timeout':
            #{user} session time limit exceeded; session terminated
            disconnect_msg = self.zd.messages['MSG_client_session_expired']
            disconnect_msg = disconnect_msg.replace("{user}", "User[%s]" % username)
            
        else:
            #{user} disconnected by admin from {wlan} at {ap}
            disconnect_msg = self.zd.messages['MSG_client_del_by_admin']
            #@author: li.pingping@odc-ruckuswireless.com 2013.05.31 to fix variable doesn't define 
            disconnect_msg = disconnect_msg.replace("{user}", "User[%s]" % username)
            disconnect_msg = disconnect_msg.replace("{wlan}", "WLAN[%s]" % self.conf['wlan_cfg'].get('ssid'))
            disconnect_msg = disconnect_msg.replace("{ap}", "AP[%s]" % self.ap_mac)
        
        #In 9.5, MSG_client_del_by_admin={user} disconnects from {wlan} at {ap} with {uptime} {rx_bytes} {tx_bytes}
        msg_split = disconnect_msg.split('with')
        disconnect_msg = msg_split[0]

        all_events = self.zd.get_events()
        disconnect_time_txt = ''
        for e in all_events:
            #@author: li.pingping@odc-ruckuswireless.com 2013.05.31 to adapter upper case to lower case
            if disconnect_msg.lower() in e[3].lower():
                disconnect_time_txt = e[0]
                break
        
        if not disconnect_time_txt:
            raise Exception("There is no event log: %s" % disconnect_msg)
        
        logging.info("Station disconnect time: %s" % disconnect_time_txt)
        
        #disconnect_time_txt: u'2011/12/31  13:10:40'
        tmptime = time.strptime(disconnect_time_txt, "%Y/%m/%d  %H:%M:%S")
        self.disconnect_time = time.mktime(tmptime)
        
