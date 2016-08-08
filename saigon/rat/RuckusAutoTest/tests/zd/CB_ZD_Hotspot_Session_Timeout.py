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
        
        
Create on 2011-8-9
@author: cwang@ruckuswireless.com
'''

import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_ZD_Hotspot_Session_Timeout(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(sta_tag = 'sta_1',
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
                         relogin_before_timer_expired = None,
                         ping_timeout_ms = 30,
                         check_status_timeout = 120,
                         )
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.t0 = time.time()
        self.errmsg = ''
        self.msg = ''
    
    def _retrieve_carribag(self):
        self.target_station = self.carrierbag.get(self.conf['sta_tag'])['sta_ins']
        self.wifi_mac_addr = self.carrierbag.get(self.conf['sta_tag'])['wifi_mac_addr']
        self.wifi_ip_addr = self.carrierbag.get(self.conf['sta_tag'])['wifi_ip_addr']
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        self._testSessionTimeout()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.msg)
        
    
    def cleanup(self):
        self._update_carribag()
    
    def _testSessionTimeout(self):
        zd_t = self.conf['hotspot_cfg']['session_timeout'] if self.conf['hotspot_cfg'].has_key('session_timeout') else 0
        svr_t = self.conf['auth_info']['session_timeout'] if self.conf['auth_info'].has_key('session_timeout') else 0
        zd_t = int(zd_t) * 60
        svr_t = int(svr_t) * 60
        # Quit if none of the timers are specified
        if not zd_t and not svr_t: return

        logging.info("Verify Session Timeout behaviour")
        if svr_t:
            logging.info("The Session Timeout attribute is configured on the Radius server. It overrides the Hotspot configuration.")
            t = svr_t
        else:
            logging.info("The Session Timeout value configured in the Hotspot profile takes effect.")
            t = zd_t
        wait_t = t - (time.time() - self.t0) + 5

        logging.info("Remove all log entries on the ZD")
        self.zd.clear_all_events()

        logging.info("Wait in %d seconds ..." % wait_t)
        time.sleep(wait_t)

        self._testSessionTimeoutStationStatusOnZD()
        if self.errmsg: return
        self._testSessionTimeoutStationConnectivity()
        if self.errmsg: return
        self._testSessionTimeoutEventLog()
        if self.errmsg: return

    def _testSessionTimeoutStationConnectivity(self):
        logging.info("Verify the connectivity from the station after its session is terminated")
        self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.conf['target_ip'],
                                                           ping_timeout_ms = self.conf['ping_timeout_ms'])
        if self.errmsg: return
        self.msg += "The station could not transmit traffic after its session was terminated. "

    def _testSessionTimeoutStationStatusOnZD(self):
        logging.info("Verify information of the target station shown on the Zone Director after its session is terminated")
        exp_client_info = {"ip": self.wifi_ip_addr, "status": "Unauthorized", "wlan": self.conf['wlan_cfg']['ssid']}

        self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd, self.wifi_mac_addr,
                                                                           exp_client_info, self.conf['check_status_timeout'])
        if not self.errmsg:
            self.msg += "The status of the station was 'Unauthorized' after its session was terminated. "

    def _testSessionTimeoutEventLog(self):
        logging.info("Verify the Event Logs")

        #MSG_client_session_expired={user} session time limit exceeded; session terminated
        event = self.zd.messages['MSG_client_session_expired']
        event = event.replace('{user}', '')

        all_logs = self.zd.get_events()
        match = [l for l in all_logs \
                 if event in l[3] and l[2] == self.conf['auth_info']['username']]
        if not match:
            self.errmsg = "There was no log entry to record the event that the station has terminated due to timed out session"
        else:
            self.msg += "Found a log entry indicates that the station has been terminated due to session timed out. "    