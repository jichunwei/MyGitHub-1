'''
Descriptiong:
    This script is used to make client roam to another AP.

Procedure:
    +Clear all events in ZD.
    +Set the channel of another AP to 'Auto' and TX. power to 'Full'.
    +Change the channel of current AP and set the TX. power of current AP to 'Min'.
    +Check if the client roamed to another AP.
    +Check the event log if the client roamed to another AP.

@author: Serena.tan@ruckuswireless.com
'''


import logging
import time
from copy import deepcopy
import random

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.components.lib.zd import access_points_zd


class CB_ZD_Client_Roam_To_Another_AP(Test):
    required_components = ['ZoneDirector', 'AP']
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        try:
            self.zd.clear_all_events()
            self.passmsg += 'Clear all events from ZD successfully.'
            
            self.change_ap_setting_to_make_client_roam()
            self.passmsg += 'Client roamed to another AP successfully.'
            
            self.check_roaming_event_log()
            self.passmsg += 'Check the roaming event log in events table successfully.'
            
        except Exception, e:
            self.errmsg = e.message
        
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
            
        self._update_carribag()
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
  
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'wlan_cfg': {},
                     'current_ap_tag': '',
                     'current_radio_mode': '',
                     'target_ap_tag': '',
                     'target_radio_mode': '',
                     'sta_tag': '',
                     'username': '',
                     'guest_name': '',
                     'tries': 5,
                     }
        self.conf.update(conf)
        
        self.wlan_cfg = self.conf['wlan_cfg']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrieve_carribag(self):
        self.current_ap = self.carrierbag[self.conf['current_ap_tag']]['ap_ins']
        self.current_ap_mac = self.current_ap.base_mac_addr
          
        self.target_ap = self.carrierbag[self.conf['target_ap_tag']]['ap_ins']
        self.target_ap_mac = self.target_ap.base_mac_addr
          
        self.sta_wifi_mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr'].lower()
        
    def _update_carribag(self):
        pass
    
    def change_ap_setting_to_make_client_roam(self):
        radio_param = {'channel': 'Auto',
                       'power': 'Full',
                       }
        ap_radio_config = access_points_zd.get_ap_radio_config_by_mac(self.zd, self.current_ap_mac)
        radio_param['wlangroups'] = ap_radio_config[self.conf['target_radio_mode']]['wlangroups']
        
        access_points_zd.set_ap_radio_by_mac_addr(self.zd, 
                                                  self.target_ap_mac, 
                                                  self.conf['target_radio_mode'], 
                                                  radio_param)
        
        ap_radio_cfg_options = access_points_zd.get_radio_cfg_options(self.zd, self.current_ap_mac)
        channel_options = ap_radio_cfg_options['radio_%s' % self.conf['current_radio_mode']]['channel']

        tries = self.conf['tries']
        while tries:
            current_radio_cfg = access_points_zd.get_ap_radio_config_by_mac(self.zd, 
                                                                            self.current_ap_mac, 
                                                                            [self.conf['current_radio_mode']])
            current_channel_cfg = current_radio_cfg[self.conf['current_radio_mode']]['channel']
            
            current_channel_options = deepcopy(channel_options)
            current_channel_options.remove(current_channel_cfg)
            
            radio_param = {'channel': random.choice(current_channel_options),
                           'power': 'Min',
                           }
            access_points_zd.set_ap_radio_by_mac_addr(self.zd, 
                                                      self.current_ap_mac, 
                                                      self.conf['current_radio_mode'], 
                                                      radio_param)
            
            time.sleep(10)
            result = self.check_client_info_on_zd()
            if not result:
                tries -= 1
            
            else:
                break
        
        if tries == 0:
            raise Exception("Cannot make client roam to another AP after %s tries." % self.conf['tries'])    
            
    def check_client_info_on_zd(self):
        if self.conf['target_radio_mode'] == 'bg' or self.conf['target_radio_mode'] == 'g' \
        or self.wlan_cfg['encryption'].upper() in ['TKIP', 'WEP-64', 'WEP-128','WEP64','WEP128']:
            expected_radio_mode = ['802.11b/g', '802.11a']
            
        else:
            expected_radio_mode = ['802.11ng', '802.11g/n', '802.11a/n', '802.11an']
        
        exp_client_info = {'wlan': self.wlan_cfg['ssid'],
                           'apmac': self.target_ap_mac,
                           "radio": expected_radio_mode,
                           }
        
        if self.wlan_cfg.get('vlan'):
            exp_client_info['vlan'] = self.wlan_cfg['vlan']
        
        errmsg, client_info = tmethod.verify_zd_client_status(self.zd, 
                                                              self.sta_wifi_mac_addr,
                                                              exp_client_info,
                                                              1)
        
        if errmsg:
            logging.info('Client not roamed to AP[%s]' % self.target_ap_mac)
            logging.info('Client info in ZD: %s' % client_info)
            return False
        
        else:
            logging.info('Client already roamed to AP[%s]' % self.target_ap_mac)
            logging.info('Client info in ZD: %s' % client_info)
            return True
    
    def check_roaming_event_log(self):
        logging.info("Verify if the roaming event log exists")
        if self.conf['username']:
            username = self.conf['username']
        
        elif self.conf['guest_name']:
            username = self.conf['guest_name']
        
        else:
            username = ''
        
        if self.conf['target_radio_mode'] == 'bg':
            expect_radio_mode = '11b/g'
            
        elif self.conf['target_radio_mode'] == 'ng':
            expect_radio_mode = '11g/n'
            
        elif self.conf['target_radio_mode'] == 'na':
            expect_radio_mode = '11a/n'
            
        # MSG_client_roam_in={ap} radio {radioto} detects {user} in {wlan} roams from {apfrom}   
        expected_msg = self.zd.messages['MSG_client_roam_in']
        expected_msg = expected_msg.replace('{ap}', 'AP[%s]' % self.target_ap_mac)
        expected_msg = expected_msg.replace('{radioto}', '[%s]' % expect_radio_mode)
        if username:
            expected_msg = expected_msg.replace('{user}', 'User[%s]' % username)
        
        else:
            expected_msg = expected_msg.replace('{user}', 'User[%s]' % self.sta_wifi_mac_addr)
            
        expected_msg = expected_msg.replace('{wlan}', 'WLAN[%s]' % self.wlan_cfg['ssid'])
        expected_msg = expected_msg.replace('{apfrom}', 'AP[%s]' % self.current_ap_mac)
        
        all_events = self.zd.get_events()
        find_roaming_event = False
        for event in all_events:
            if expected_msg in repr(event):
                find_roaming_event = True
                logging.info('Found the roaming event log successfully: [%s]' % repr(event))
                break

        if find_roaming_event:
            return True
        
        else:
            logging.info('Not found the roaming event log in the event table.')
            return False
        
