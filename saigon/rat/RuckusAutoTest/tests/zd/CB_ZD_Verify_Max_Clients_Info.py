"""
   Two clients connecet to Autonoumous WLAN and then AP lost contact with ZD, and AP can still server client.
   Config max clients number permitted to one only by WLAN config or AP group AP model config.
   After AP reconnected to ZD again, check whether the clients can access Autonoumous WLAN or not.
   
   Expeected:
       Only 1 client in client_mac_list is permitted to access the WLAN, and the other should be refused to access with warning event.

author: kevin.tan@ruckuswireless.com
date: 2013-04-17
"""


import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_ZD_Verify_Max_Clients_Info(Test):
    required_components = ['ZoneDirector']
    parameter_description = {'check_status_timeout':'Timeout for checking status',
                             'status': 'Expected client status in ZD, authorized, unauthorized',
                             'sta_tag_list':'Station tag list, and will get station instance and information from carrier bag based on sta_tag',
                             'wlan_cfg': 'WLAN configuration',
                             'ap_tag':'Active Point tag, and will get active point instance and information from carrier bag based on ap_tag',
                             }

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyStationInfoOnZD()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)

        self.passmsg = 'Verify Autonomous WLAN max clients shown on ZD successfully'
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'check_status_timeout':60,
                     'status':'Authorized',
                     'sta_tag_list':['sta_1', 'sta_2'],
                     'wlan_cfg':{},
                     'ap_tag':'',
                     }

        self.conf.update(conf)
        self.wlan_cfg = conf['wlan_cfg']
        self.zd = self.testbed.components["ZoneDirector"]
        self._retrieve_carribag()
        self.errmsg = ''
        self.passmsg = ''

    def _retrieve_carribag(self):
        self.client_mac_list = []
        for i in self.conf['sta_tag_list']:
            self.client_mac_list.append(self.carrierbag[i]['wifi_mac_addr'])
            
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']

    def _verifyStationInfoOnZD(self):
        exp_client_info = {"status": self.conf['status'],
                           "wlan": self.wlan_cfg['ssid'],
                           "apmac": self.active_ap.base_mac_addr,
                           'mac': self.client_mac_list,
                           }

        start_time = time.time()
        match = False
        logging.info("Verify that only one active client is shown on Zone Director")

        while True:
            time.sleep(10)
            current_time = time.time()
            if (current_time - start_time) > self.conf['check_status_timeout']:
                self.errmsg += "No client info shown on ZD after %s second" % self.conf['check_status_timeout']
                return
            
            if not match:
                client_info_list = self.zd.get_active_client_list()
                length = len(client_info_list)
                if length > 1:
                    self.errmsg += "Two clients' info shown on ZD, unexpected behavior, should be one only"
                    return
                elif length == 0:
                    continue
                else:
                    info = client_info_list[0]
                    for key, value in exp_client_info.iteritems():
                        if type(value) in [list, tuple]:
                            if info[key].lower() not in [x.lower() for x in value]:
                                self.errmsg += "Client info [%s] is unexpected [%s]" % (key, info[key])
                                return
                        else:
                            if info[key].lower() != value.lower():
                                self.errmsg += "Client info [%s] is unexpected [%s], should be [%s]" % (key, info[key], value)
                                return
                
                    self.client_mac_list.remove(info['mac'])
                    match = True

            logging.info("Check event that another client[%s] should be refused to access WLAN[%s] from active AP[%s]"\
                          % (self.client_mac_list[0], self.wlan_cfg['ssid'], self.active_ap.base_mac_addr))
            self._verify_client_access_refused_event(self.client_mac_list[0])
            if self.passmsg:
                return

    def _verify_client_access_refused_event(self, sta_mac):
        logging.info('Client[%s] access refused event verification' % sta_mac)
        all_events = self.zd.getEvents()

        #MSG_client_join_failed_AP_busy={user} is refused access to {wlan} from {ap} because there are too many users on that AP, WLAN, or Radio.
        expected_event = self.zd.messages['MSG_client_join_failed_AP_busy']
        expected_event = expected_event.replace("{user}", r"User[%s]" )
        expected_event = expected_event.replace("{wlan}", r"WLAN[%s]" )
        expected_event = expected_event.replace("{ap}", r"AP[%s]" )
        
        expected_event = expected_event % (sta_mac, self.wlan_cfg['ssid'], self.active_ap.base_mac_addr)

        for event in all_events:
            if expected_event in event:
                self.passmsg = '[Correct behavior] %s' % event
                return

        errmsg = '[Incorrect behavior] There is no event about client[%s] refused to access WLAN[%s] from AP[%s] '
        self.errmsg += errmsg % (sta_mac, self.wlan_cfg['ssid'], self.active_ap.base_mac_addr)
