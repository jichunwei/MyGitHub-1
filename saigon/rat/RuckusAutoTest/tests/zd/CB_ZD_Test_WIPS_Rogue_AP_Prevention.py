"""
   Description: 
   @author: Kevin Tan
   @contact: kevin.tann@ruckuswireless.com
   @since: August 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters:
   
   Test procedure:
    1. Config:
        -         
    2. Test:
        - Verify if the mesh tree are match with expected 
    3. Cleanup:
        -
   
   Result type: PASS/FAIL
   Results: PASS: WIPS rogue AP prevent succeeded
            FAIL: WIPS rogue AP prevent failed

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import time
import logging
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components.lib.zd import rogue_devices_zd as rogue
from RuckusAutoTest.components.lib.zd import service_zd as service

class CB_ZD_Test_WIPS_Rogue_AP_Prevention(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                            }

    def config(self, conf):
        self._init_test_parameter(conf)

    def test(self):
        try:
            #disable 2.4G or 5G background scanning options for fast detecting of rogue AP
            if self.conf.get('radio') == 'na':
                service.set_background_scan_options(self.zd, option_2_4G='', option_5G='5')
            else:
                service.set_background_scan_options(self.zd, option_2_4G='5', option_5G='')
    
            
            if self.conf.get('type') == 'ssid_spoof':
                self.test_ssid_spoof()
            elif self.conf.get('type') == 'same_network':
                self.test_same_network()
            else:
                #bssid(MAC) spoof
                pass
    
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
    
            return self.returnResult('PASS', self.passmsg)
        finally:
            service.set_background_scan_options(self.zd, option_2_4G='20', option_5G='20')
    
    def cleanup(self):
        #recover background scanning options
        pass
        
    
    def _init_test_parameter(self, conf):
        self.conf = dict({'check_status_timeout':60})
        self.conf.update(conf)

        self.errmsg = ""
        self.passmsg = ""
        self.ssid = self.conf['wlan_cfg']['ssid']
        
        self.ap_tag1 = self.conf['under_zd_ap_tag']
        self.ap_tag2 = self.conf['standalone_ap_tag']

        self.under_zd_ap = self.carrierbag[self.ap_tag1]['ap_ins']
        self.standalone_ap = self.carrierbag[self.ap_tag2]['ap_ins']
        self.rouge_ap_mac = self.standalone_ap.get_base_mac().lower()

        self.zd = self.testbed.components['ZoneDirector']

        if self.conf.get('radio') == 'na':
            self.rouge_bssid = self.standalone_ap.get_wlan_info_dict()['wlan8']['bssid']
        else:
            self.rouge_bssid = self.standalone_ap.get_wlan_info_dict()['wlan0']['bssid']
        
        self.rouge_ip = self.standalone_ap.get_ip_addr()

    def test_ssid_spoof(self):
        #verify local wired network event detection for Rogue AP
        target = self.standalone_ap.get_ip_addr()
        ping_time = 10 * 1000
        try:
            res = self.under_zd_ap.ping_from_ap(target, ping_time)
            if not res.startswith('Ping OK'):
                self.errmsg = 'ping %s timeout within %s second' % (target_ip, ping_timeout/1000)
                return
        except:
            pass

        #verify rogue AP information in Monitor-->Rogue Devices page
        self._verify_rogue_ap_info('SSID-spoof')
        if self.errmsg: 
            return

        #verify SSID spoofing detection event for Rogue AP
        self._verify_wips_event_ssid_spoof()
        if self.errmsg: 
            return
        
        #verify local wired network event detection for Rogue AP
        if self.conf.get('client_join') == True:
            self._verify_client_join_zd()
            if self.errmsg: 
                return

    def test_same_network(self):
        #verify local wired network event detection for Rogue AP
        target = self.standalone_ap.get_ip_addr()
        ping_time = 10 * 1000
        res = self.under_zd_ap.ping_from_ap(target, ping_time)
        if not res.startswith('Ping OK'):
            self.errmsg = 'ping %s timeout within %s second' % (target_ip, ping_timeout/1000)
            return
                
        #verify rogue AP information in Monitor-->Rogue Devices page
        self._verify_rogue_ap_info('Same-Network Rogue AP')
        if self.errmsg: 
            return

        #verify local wired network event detection event for Rogue AP
        self._verify_wips_event_same_network_spoof()
        if self.errmsg:
            return

        #verify local wired network event detection for Rogue AP
        if self.conf.get('client_join') == True:
            self._verify_client_join_zd()
            if self.errmsg: 
                return

    def _verify_wips_event_ssid_spoof(self):
        logging.info('Verify WIPS event about spoofing AP detection')

        #MSG_SSID_spoofing_AP_detected=A new SSID-spoofing {rogue} with {ssid} is first detected by {ap}
        expected_event1 = self.zd.messages['MSG_SSID_spoofing_AP_detected']
        expected_event1 = expected_event1.replace("{rogue}", r"Rogue[%s]" )
        expected_event1 = expected_event1.replace("{ssid}", r"SSID[%s]")
        expected_event1 = expected_event1.replace("{ap}", r"AP[%s]")
        expected_event1 = expected_event1 % (self.rouge_bssid, self.ssid, self.under_zd_ap.base_mac_addr.lower())

        #MSG_lanrogue_AP_detected={rogue}/{ip} with {ssid} is detected by {ap} on the local wired network
        expected_event2 = self.zd.messages['MSG_lanrogue_AP_detected']
        expected_event2 = expected_event2.replace("{rogue}", r"Rogue[%s]" )
        expected_event2 = expected_event2.replace("{ip}", r"[%s]" )
        expected_event2 = expected_event2.replace("{ssid}", r"SSID[%s]")
        expected_event2 = expected_event2.replace("{ap}", r"AP[%s]")
        expected_event2 = expected_event2 % (self.rouge_bssid, self.rouge_ip, self.ssid, self.under_zd_ap.base_mac_addr.lower())

        #MSG_rogue_interference_detected=A {rogue} with {ssid} interferes with {ap} on channel {channel}.
        expected_event3 = self.zd.messages['MSG_rogue_interference_detected']
        expected_event3 = expected_event3.replace("{rogue}", r"Rogue[%s]" )
        expected_event3 = expected_event3.replace("{ssid}", r"SSID[%s]")
        expected_event3 = expected_event3.replace("{ap}", r"AP[%s]")
        expected_event3 = expected_event3.replace("{channel}", r"")
        expected_event3 = expected_event3 % (self.rouge_bssid, self.ssid, self.under_zd_ap.base_mac_addr.lower())
        
        #MSG_malicious_AP_disappears=A Malicious {rogue} detection by {ap} goes away 
        expected_event4 = self.zd.messages['MSG_malicious_AP_disappears']
        expected_event4 = expected_event4.replace("{rogue}", r"Rogue[%s]" )
        expected_event4 = expected_event4.replace("{ap}", r"AP[%s]")
        expected_event4 = expected_event4 % (self.rouge_bssid, self.under_zd_ap.base_mac_addr.lower())
        
        expected_event_list = [expected_event1, expected_event2]

        all_events = self.zd.get_events()
        for event in all_events:
            if event in expected_event_list or expected_event3 in event or expected_event4 in event:
                self.passmsg += '[Correct behavior] %s' % event
                return

    def _verify_wips_event_interferes(self):
        logging.info('Verify WIPS event about spoofing AP detection')

        #MSG_rogue_interference_detected=A {rogue} with {ssid} interferes with {ap} on channel {channel}.
        expected_event = self.zd.messages['MSG_rogue_interference_detected']
        expected_event = expected_event.replace("{rogue}", r"Rogue[%s]" )
        expected_event = expected_event.replace("{ssid}", r"SSID[%s]")
        expected_event = expected_event.replace("{ap}", r"AP[%s]")
        expected_event = expected_event.replace("{channel}", r"")
        expected_event = expected_event % (self.rouge_bssid, self.ssid, self.under_zd_ap.base_mac_addr.lower())

        all_events = self.zd.get_events()
        for event in all_events:
            if expected_event in event:
                self.passmsg += '[Correct behavior] %s' % event
                return

    def _verify_wips_event_bssid_spoof(self):
        logging.info('Verify WIPS event about spoofing AP detection')

        #MSG_MAC_spoofing_AP_detected=A new MAC-spoofing {rogue} with {ssid} is first detected by {ap}
        expected_event1 = self.zd.messages['MSG_MAC_spoofing_AP_detected']
        expected_event1 = expected_event1.replace("{rogue}", r"Rogue[%s]" )
        expected_event1 = expected_event1.replace("{ssid}", r"SSID[%s]")
        expected_event1 = expected_event1.replace("{ap}", r"AP[%s]")
        expected_event1 = expected_event1 % (self.rouge_bssid, self.ssid, self.under_zd_ap.base_mac_addr.lower())

        #MSG_lanrogue_AP_detected={rogue}/{ip} with {ssid} is detected by {ap} on the local wired network
        expected_event2 = self.zd.messages['MSG_lanrogue_AP_detected']
        expected_event2 = expected_event2.replace("{rogue}", r"Rogue[%s]" )
        expected_event2 = expected_event2.replace("{ip}", r"[%s]" )
        expected_event2 = expected_event2.replace("{ssid}", r"SSID[%s]")
        expected_event2 = expected_event2.replace("{ap}", r"AP[%s]")
        expected_event2 = expected_event2 % (self.rouge_bssid, self.rouge_ip, self.ssid, self.under_zd_ap.base_mac_addr.lower())

        #MSG_rogue_interference_detected=A {rogue} with {ssid} interferes with {ap} on channel {channel}.
        expected_event3 = self.zd.messages['MSG_rogue_interference_detected']
        expected_event3 = expected_event3.replace("{rogue}", r"Rogue[%s]" )
        expected_event3 = expected_event3.replace("{ssid}", r"SSID[%s]")
        expected_event3 = expected_event3.replace("{ap}", r"AP[%s]")
        expected_event3 = expected_event3.replace("{channel}", r"")
        expected_event3 = expected_event3 % (self.rouge_bssid, self.ssid, self.under_zd_ap.base_mac_addr.lower())
        
        #MSG_malicious_AP_disappears=A Malicious {rogue} detection by {ap} goes away 
        expected_event4 = self.zd.messages['MSG_malicious_AP_disappears']
        expected_event4 = expected_event4.replace("{rogue}", r"Rogue[%s]" )
        expected_event4 = expected_event4.replace("{ap}", r"AP[%s]")
        expected_event4 = expected_event4 % (self.rouge_bssid, self.under_zd_ap.base_mac_addr.lower())
        
        expected_event_list = [expected_event1, expected_event2]

        all_events = self.zd.get_events()
        for event in all_events:
            if event in expected_event_list or expected_event3 in event or expected_event4 in event:
                self.passmsg += '[Correct behavior] %s' % event
                return

    def _verify_wips_event_same_network_spoof(self):
        logging.info('Verify WIPS event about same network spoofing AP detection')

        #MSG_same_network_spoofing_AP_detected=A new Same-Network Rogue AP {rogue} with {ssid} is first detected by {ap}
        expected_event1 = self.zd.messages['MSG_same_network_spoofing_AP_detected']
        expected_event1 = expected_event1.replace("{rogue}", r"Rogue[%s]" )
        expected_event1 = expected_event1.replace("{ssid}", r"SSID[%s]")
        expected_event1 = expected_event1.replace("{ap}", r"AP[%s]")
        expected_event1 = expected_event1 % (self.rouge_bssid, self.ssid, self.under_zd_ap.base_mac_addr.lower())

        #MSG_lanrogue_AP_detected={rogue}/{ip} with {ssid} is detected by {ap} on the local wired network
        expected_event2 = self.zd.messages['MSG_lanrogue_AP_detected']
        expected_event2 = expected_event2.replace("{rogue}", r"Rogue[%s]" )
        expected_event2 = expected_event2.replace("{ip}", r"[%s]" )
        expected_event2 = expected_event2.replace("{ssid}", r"SSID[%s]")
        expected_event2 = expected_event2.replace("{ap}", r"AP[%s]")
        expected_event2 = expected_event2 % (self.rouge_bssid, self.rouge_ip, self.ssid, self.under_zd_ap.base_mac_addr.lower())

        #MSG_rogue_interference_detected=A {rogue} with {ssid} interferes with {ap} on channel {channel}.
        expected_event3 = self.zd.messages['MSG_rogue_interference_detected']
        expected_event3 = expected_event3.replace("{rogue}", r"Rogue[%s]" )
        expected_event3 = expected_event3.replace("{ssid}", r"SSID[%s]")
        expected_event3 = expected_event3.replace("{ap}", r"AP[%s]")
        expected_event3 = expected_event3.replace("{channel}", r"")
        expected_event3 = expected_event3 % (self.rouge_bssid, self.ssid, self.under_zd_ap.base_mac_addr.lower())
        
        #MSG_malicious_AP_disappears=A Malicious {rogue} detection by {ap} goes away 
        expected_event4 = self.zd.messages['MSG_malicious_AP_disappears']
        expected_event4 = expected_event4.replace("{rogue}", r"Rogue[%s]" )
        expected_event4 = expected_event4.replace("{ap}", r"AP[%s]")
        expected_event4 = expected_event4 % (self.rouge_bssid, self.under_zd_ap.base_mac_addr.lower())
        
        expected_event_list = [expected_event1, expected_event2]

        all_events = self.zd.get_events()
        for event in all_events:
            if event in expected_event_list or expected_event3 in event or expected_event4 in event:
                self.passmsg += '[Correct behavior] %s' % event
                return

    def _verify_wips_event_local_wired_network(self):
        logging.info('Verify WIPS event about local wired network AP detection')

        #MSG_lanrogue_AP_detected={rogue}/{ip} with {ssid} is detected by {ap} on the local wired network
        expected_event1 = self.zd.messages['MSG_lanrogue_AP_detected']
        expected_event1 = expected_event1.replace("{rogue}", r"Rogue[%s]" )
        expected_event1 = expected_event1.replace("{ip}", r"[%s]" )
        expected_event1 = expected_event1.replace("{ssid}", r"SSID[%s]")
        expected_event1 = expected_event1.replace("{ap}", r"AP[%s]")
        expected_event1 = expected_event1 % (self.rouge_bssid, self.rouge_ip, self.ssid, self.under_zd_ap.base_mac_addr.lower())
        
        #MSG_rogue_interference_detected=A {rogue} with {ssid} interferes with {ap} on channel {channel}.
        expected_event2 = self.zd.messages['MSG_rogue_interference_detected']
        expected_event2 = expected_event2.replace("{rogue}", r"Rogue[%s]" )
        expected_event2 = expected_event2.replace("{ssid}", r"SSID[%s]")
        expected_event2 = expected_event2.replace("{ap}", r"AP[%s]")
        expected_event2 = expected_event2.replace("{channel}", r"")
        expected_event2 = expected_event2 % (self.rouge_bssid, self.ssid, self.under_zd_ap.base_mac_addr.lower())
        
        #MSG_malicious_AP_disappears=A Malicious {rogue} detection by {ap} goes away 
        expected_event3 = self.zd.messages['MSG_malicious_AP_disappears']
        expected_event3 = expected_event3.replace("{rogue}", r"Rogue[%s]" )
        expected_event3 = expected_event3.replace("{ap}", r"AP[%s]")
        expected_event3 = expected_event3 % (self.rouge_bssid, self.under_zd_ap.base_mac_addr.lower())
        
        expected_event_list = [expected_event1]

        all_events = self.zd.get_events()
        for event in all_events:
            if event in expected_event_list or expected_event2 in event or expected_event3 in event:
                self.passmsg += '[Correct behavior] %s' % event
                return

    def _verify_rogue_ap_info(self, type):
        wait_time=1800
        t0=time.time()
        
        while(True):
            current_time = time.time()
            if (current_time - t0)>wait_time:
                self.errmsg = "[Incorrect behavior] There is no Rogue AP info found in page Monitor-->Rouge Devices-->Currently Active Rogue Devices after %s minutes" % (wait_time/60)
                return
        
            rogue_list = rogue.get_active_rouge_devices_list(self.zd, mac = self.rouge_ap_mac)
            for info in rogue_list:
                #info type: 'SSID-spoof', 'MAC-spoof', 'Same-Network Rogue AP'
                if info['ssid'] == self.ssid:# or info['mac'] == self.standalone_ap.base_mac_addr.lower() or type in info['type']:
                    self.passmsg += "Rogue AP with type %s info was found in page Monitor-->Rouge Devices-->Currently Active Rogue Devices" % type
                    return

            logging.info('No Rogue AP with type %s mac[%s] info was found, wait for a few seconds...' % (type, self.rouge_ap_mac))
            time.sleep(15)

    def _verify_client_join_zd(self):
        self.sta_wifi_mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
        self.sta_wifi_ip_addr  = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']

        # MSG_client_join={user} joins {wlan} from {ap}
        expected = self.zd.messages['MSG_client_join']            
        expected = expected.replace('{user}', 'User[%s]' % self.sta_wifi_mac_addr.lower())
        expected = expected.replace('{wlan}', 'WLAN[%s]' % self.ssid)
        expected = expected.replace('{ap}', 'AP[%s]' % self.under_zd_ap.base_mac_addr)

        exp_client_info = {"ip": self.sta_wifi_ip_addr,
                           "status": 'Authorized',
                           "wlan": self.ssid,
                           "apmac": self.under_zd_ap.base_mac_addr,
                           }

        self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd,
                                                                              self.sta_wifi_mac_addr,
                                                                              exp_client_info,
                                                                              self.conf['check_status_timeout'])
        
        logging.info('Client information in ZD is %s' % (self.client_info_on_zd))
        
        self.errmsg = ''
        self.passmsg += 'Client de-authenticated from Rogue AP[%s] and join genuine AP[%s]' % (self.standalone_ap.base_mac_addr, self.under_zd_ap.base_mac_addr)
