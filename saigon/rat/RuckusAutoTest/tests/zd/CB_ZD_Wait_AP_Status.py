"""

    Wait AP status changes to expected status: Connected(check WLAN service enabled or not, bug ZF-3354) or Disconnect 

author: kevin.tan@ruckuswireless.com
date: 2013-04-19
"""

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Wait_AP_Status(Test):
    def config(self, conf):
        self.conf={}
        self.conf.update(conf)
        self.zd=self.testbed.components['ZoneDirector']
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.apmac = self.active_ap.base_mac_addr

        self.passmsg = ''
        self.errmsg = ''

    def test(self):
        time0 = time.time()
        wait_time = 180

        expected_status = self.conf['expected_status'].lower()
        logging.info('Wait AP status changes to expected status <%s>' % expected_status)

        while(True):
            current_time = time.time()
            if  (current_time-time0) >wait_time:
                self.errmsg += '[Incorrect behavior] Active AP status not changed to expected status <%s> after %s second' % (expected_status, wait_time)
                return self.returnResult("FAIL", self.errmsg)

            try:
                ap_info= lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, self.apmac)

                if not ap_info['state'].lower().startswith(expected_status):
                    time.sleep(10)
                    continue

                if expected_status == 'connected' and self.conf.has_key('ap_cfg'):
                    logging.info('Check active AP radio parameter after AP recovers from disconnected to connected')
                    supported_radio = lib.zd.ap.get_supported_radio(self.zd, self.apmac)
                    radio_info = lib.zd.ap.get_ap_radio_config_by_mac(self.zd, self.apmac, supported_radio)
                    
                    for r in supported_radio:
                        if r == self.conf['ap_cfg']['radio']:
                            if radio_info[r]['wlan_service'] != self.conf['ap_cfg']['wlan_service']:
                                self.errmsg += '[Incorrect behavior] Active AP radio is %s, should be %s' % (radio_info['wlan_service'], self.conf['ap_cfg']['wlan_service'])
                                return self.returnResult("FAIL", self.errmsg)
                        else:
                            if radio_info[r]['wlan_service'] != False:
                                self.errmsg += '[Incorrect behavior] Active AP radio of not tested radio type is %s, should be False' % (radio_info['wlan_service'])
                                return self.returnResult("FAIL", self.errmsg)

                break
            except:
                pass

        return self.returnResult("PASS", 'Wait AP status changes to expected status <%s> successfully' % expected_status)

    def cleanup(self):
        pass

