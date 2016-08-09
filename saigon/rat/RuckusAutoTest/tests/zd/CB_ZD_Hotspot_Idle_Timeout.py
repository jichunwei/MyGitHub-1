'''
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 
   Result type: PASS/FAIL
   Results: PASS:
            FAIL:  

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - 
   2. Test:
       -            
   3. Cleanup:
       - 
    How it was tested:
        
        
Create on 2011-8-10
@author: cwang@ruckuswireless.com
'''

import logging
import time
import re

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_ZD_Hotspot_Idle_Timeout(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(sta_tag = 'sta_1',
                         ap_tag = 'tap',
                         wlan_cfg = dict(ssid = "RAT-Open-None", auth = "open", encryption = "none", 
                                         type="hotspot", hotspot_profile = 'A Sampe Hotspot Profile'),
                         auth_info = {
                                      'username':'local.username',
                                      'password':'local.password',                                                                         
                                      },
                         hotspot_cfg = {'login_page': 'http://192.168.0.250/login.html', 
                                        'name': 'A Sampe Hotspot Profile',                                        
                                        },
                         target_ip = '172.126.0.252',
                         ping_timeout_ms = 30,
                         check_status_timeout = 120,
                         )
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self._retrieve_carribag()
        self.errmsg = ''
        self.msg = ''
    
    def _retrieve_carribag(self):
        self.target_station = self.carrierbag.get(self.conf['sta_tag'])['sta_ins']
        self.wifi_mac_addr = self.carrierbag.get(self.conf['sta_tag'])['wifi_mac_addr']
        self.wifi_ip_addr = self.carrierbag.get(self.conf['sta_tag'])['wifi_ip_addr']
        self.active_ap = self.carrierbag.get(self.conf['ap_tag'])['ap_ins']      
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)        
    
    def test(self):
        self._testIdleTimeout()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.msg)
    
    def cleanup(self):
        self._retrieve_carribag()
        
            
    def _testIdleTimeout(self):
        zd_t = self.conf['hotspot_cfg']['idle_timeout'] if self.conf['hotspot_cfg'].has_key('idle_timeout') else 0
        svr_t = self.conf['auth_info']['idle_timeout'] if self.conf['auth_info'].has_key('idle_timeout') else 0
        zd_t = int(zd_t) * 60
        svr_t = int(svr_t) * 60
        # Quit if none of the timers are specified
        if not zd_t and not svr_t: return

        msg = "Verify Idle Timeout behaviour: Station reassociates %s the timer gets expired" % \
              ("BEFORE" if self.conf['relogin_before_timer_expired'] else "AFTER")
        logging.info(msg)
        if svr_t:
            logging.info("The Idle Timeout attribute is configured on the Radius server. It overrides the Hotspot configuration.")
            t = svr_t
        else:
            logging.info("The Idle Timeout value configured in the Hotspot profile takes effect.")
            t = zd_t

        self._cfgDisconnectStationFromWLAN()

        logging.info("Remove all log entries on the ZD")
        self.zd.clear_all_events()

        #wait_t = (t - (time.time() - self.t0)) / 4 if self.conf['relogin_before_timer_expired'] else t * 2 - (time.time() - self.t0)
        #wait_t = (t - self.auth_time - (time.time() - self.t0)) / 4 if self.conf['relogin_before_timer_expired'] else t + t * 1/3
        #JLIN@20100624 since zd check hotspot client if expired every 10 minutes, wait more 10 minutes to make sure client expired.
        #wait_t = 0 if self.conf['relogin_before_timer_expired'] else t + t * 1 / 3
        wait_t = t - 60 if self.conf['relogin_before_timer_expired'] else t + 600
        logging.info("Wait in %d seconds ..." % wait_t)
        time.sleep(wait_t)
        self._cfgConnectStationToWLAN()
        self._testIdleTimeoutStationStatusOnZD(timer_expired = not self.conf['relogin_before_timer_expired'])
        if self.errmsg: return
        self._testIdleTimeoutStationConnectivity(timer_expired = not self.conf['relogin_before_timer_expired'])
        if self.errmsg: return
        self._testIdleTimeoutEventLog(timer_expired = not self.conf['relogin_before_timer_expired'])
        if self.errmsg: return

    def _cfgDisconnectStationFromWLAN(self):
        logging.info("Disconnect the station from the currently associated WLAN")
        self.target_station.disconnect_from_wlan()
        # Record the time when the station starts disassociating from the WLAN
        # This value is used to verify the Idle Timeout behaviour
        self.t0 = time.time()

    def _cfgConnectStationToWLAN(self):        
        logging.info("Connect the station back to the configured WLAN [%s]" % self.conf['wlan_cfg']['ssid'])
        self.target_station.connect_to_wlan(ssid = self.conf['wlan_cfg']['ssid'])

    def _testIdleTimeoutStationConnectivity(self, timer_expired):
        logging.info("Verify the connectivity from the station after it reassociates back to the WLAN")
        time.sleep(3)        
        if timer_expired:
            self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.conf['target_ip'],
                                                               ping_timeout_ms = self.conf['ping_timeout_ms'])
            if self.errmsg: return
            self.msg += "The station could not transmit traffic after it reassociates back to the WLAN. "
        else:
            self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.conf['target_ip'],
                                                              ping_timeout_ms = self.conf['ping_timeout_ms'])
            if self.errmsg: return
            self.msg += "The station could transmit traffic after it reassociates back to the WLAN. "

    def _testIdleTimeoutStationStatusOnZD(self, timer_expired):
        logging.info("Verify information of the target station shown on the Zone Director after it reassocicates back to the WLAN")
        if timer_expired:
            exp_client_info = {"ip": self.wifi_ip_addr, "status": "Unauthorized", "wlan": self.conf['wlan_cfg']['ssid']}

            self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd, self.wifi_mac_addr,
                                                                               exp_client_info, self.conf['check_status_timeout'])
            if not self.errmsg:
                self.msg += "The status of the station was 'Unauthorized' after it reassociates back to the WLAN. "
        else:
            exp_client_info = {"ip": self.conf['auth_info']['username'], "status": "Authorized", "wlan": self.conf['wlan_cfg']['ssid']}

            self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd, self.wifi_mac_addr,
                                                                               exp_client_info, self.conf['check_status_timeout'])
            if not self.errmsg:
                self.msg += "The status of the station was 'Authorized' after it reassociates back to the WLAN. "

    def _testIdleTimeoutEventLog(self, timer_expired):
        logging.info("Verify the Event Logs")
        all_logs = self.zd.get_events()

        #MSG_client_reconnect_within_grace_period=
        # {user} reconnects to {ap} within grace period.  \
        # No additional authentication is required.

        msg = self.zd.messages['MSG_client_reconnect_within_grace_period']
        msg = msg.replace('  ', ' ')
        msg_with_mac = msg
        msg = msg.replace('{user}', 'User\[%s\]' % self.conf['auth_info']['username'])

        if self.conf.has_key('active_ap'):
            msg = msg.replace('{ap}', 'AP\[%s\]' % self.active_ap.base_mac_addr)
        else:
            msg = msg.replace('{ap}', 'AP\[%s\]' % '.*')


        msg_with_mac = msg_with_mac.replace('{user}', 'User\[%s@%s\]' %
                                            (self.conf['auth_info']['username'],
                                             self.wifi_mac_addr))

        if self.conf.has_key('active_ap'):
            msg_with_mac = msg_with_mac.replace('{ap}', 'AP\[%s\]' %
                                                self.active_ap.base_mac_addr)
        else:
            msg_with_mac = msg_with_mac.replace('{ap}', 'AP\[%s\]' % '.*')

        match = [l for l in all_logs \
                 if re.search(msg, l[3]) and l[2] == self.conf['auth_info']['username']]

        # backward compability
        if not match:
            match = [l for l in all_logs \
                 if re.search(msg_with_mac, l[3])
                 and l[2] == self.conf['auth_info']['username']]

        if match:
            if timer_expired:
                self.errmsg = "There was a log entry to record the event that "\
                              "the station reconnects within grace period. "
            else:
                self.msg += "Found a log entry indicates that the station "\
                            "reconnects within grace period. "

        else:
            if timer_expired:
                self.msg += "Not found any log entries indicate that "\
                            "the station reconnects within grace period. "
            else:
                self.errmsg = "There was no log entry to record the event that "\
                              "the station reconnects within grace period. "        