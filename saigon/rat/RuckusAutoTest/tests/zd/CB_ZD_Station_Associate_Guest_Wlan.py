'''

Created on 2014-2-21

@author: jluh
'''
from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from copy import deepcopy
import re
import logging


class CB_ZD_Station_Associate_Guest_Wlan(Test):

    def config(self, conf):
        self._init_test_parameters(conf)


    def test(self):
        if self.conf['is_restart_adapter']:
            tmethod.restart_station_adapter(self.target_station)
        self._test_assoc_station_with_ssid()
        if self.errmsg:
            if not self.conf['expected_failed']:
                return self.returnResult('FAIL', self.errmsg)
            else:
                return self.returnResult('PASS', self.errmsg)
            
        self._test_verify_station_info_on_zd()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)

        if not self.passmsg:
            self.passmsg = 'Associate station successfully'

        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        self._update_carrier_bag()


    def _init_test_parameters(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = {'check_status_timeout': 120,
                     'break_time': 10,
                     'restart_cnt': 6,
                     'is_negative': False,
                     'is_restart_adapter': False,
                     'expected_failed':False,
                     'failed_event':'',
                     }
        self.conf.update(conf)
        self.wlan_cfg = conf['wlan_cfg']
        self.target_station = self.carrierbag['station']
        self.is_negative = self.conf['is_negative']
        self.zd = self.testbed.components['ZoneDirector']


    def _test_assoc_station_with_ssid(self):
        wlan_cfg = deepcopy(self.wlan_cfg)

        if wlan_cfg.has_key("wpa_ver") and wlan_cfg.get("wpa_ver").lower() == "wpa_mixed":
            wlan_cfg['wpa_ver'] = wlan_cfg['sta_wpa_ver']

        if wlan_cfg.has_key("encryption") and wlan_cfg.get("encryption").lower() == "auto":
            wlan_cfg['encryption'] = wlan_cfg['sta_encryption']

        self.errmsg = tmethod.assoc_station_with_ssid(self.target_station, 
                                                      wlan_cfg, 
                                                      self.conf['check_status_timeout'],
                                                      self.conf['break_time'], 
                                                      self.conf['restart_cnt'], 
                                                      )
        if not self.errmsg:
            if self.is_negative:
                self.refused_user_mac = ''
                
                if self.conf['failed_event'] == 'max_client_exceed':
                    self._veirfy_assoc_failed_event_max_users_excceed()
                    if  self.errmsg: 
                        return self.returnResult('FAIL', self.errmsg)

                    exp_client_info = {"wlan": self.wlan_cfg['ssid']}
                    self.errmsg, client_info_on_zd = tmethod.verify_zd_client_status(self.zd, 
                                                                                     self.refused_user_mac,
                                                                                     exp_client_info, 
                                                                                     check_status_timeout=30)
                    if self.errmsg:
                        self.errmsg = ''
                        self.passmsg = 'The station cannot connect because of max users exceed'
                    else:
                        self.errmsg = '[Incorrect behavior]The station is connected in ZD event though max users exceed'
                    
                    return
                
                self.errmsg = "The stations was associated although it was not allowed to."

            return

        self.errmsg = tmethod.verify_wlan_in_the_air(
            self.target_station, wlan_cfg['ssid']
        )

        if self.is_negative:
            if "couldn't associate" in self.errmsg:
                self.errmsg = ""
                self.passmsg = "The station was not allowed to associate due to ACL."

    def _veirfy_assoc_failed_event_max_users_excceed(self):
        logging.info('Verify Max clients number exceed event on ZD WebUI')
        all_events = self.zd.getEvents()

        #MSG_client_join_failed_AP_busy={user} is refused access to {wlan} from {ap} because there are too many users on that AP, WLAN, or Radio.
        expected_event = 'refused access to WLAN[%s]' % self.wlan_cfg['ssid']

        for event in all_events:
            if expected_event in event[-1]:
                self.refused_user_mac = re.search('User\[([\w|:]*)\]', event[-1], re.I).groups()[0] 
                return

        self.errmsg += '[Incorrect behavior] There is no event about Max clients number exceed event'
        
        
    def _test_verify_station_info_on_zd(self):
        '''
        '''
        res, self.var1, self.var2 = tmethod.renew_wifi_ip_address(self.target_station, 
                                                                  self.conf['check_status_timeout']
                                                                  )
        if not res:
            self.errmsg = self.var2


    def _update_carrier_bag(self):
        '''
        '''
        self.carrierbag['sta_wifi_ip_addr'] = self.var1
        self.carrierbag['sta_wifi_mac_addr'] = self.var2.lower()
