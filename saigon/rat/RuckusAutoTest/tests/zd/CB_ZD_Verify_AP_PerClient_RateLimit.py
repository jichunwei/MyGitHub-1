
"""
Description: To verify if ZD could authenticate to an exist radius authentication server
"""

import time
import logging

from RuckusAutoTest.models import Test

class CB_ZD_Verify_AP_PerClient_RateLimit(Test):
    required_components = ['ZoneDirector']
    parameter_description = {}

    def config(self, conf):
        self.conf = conf.copy()
        self.zd = self.testbed.components['ZoneDirector']
        self.server = self.testbed.components['LinuxServer']

        self.errmsg = ""
        self.passmsg = ""

        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.active_ap_mac = self.active_ap.get_base_mac()

    def test(self):
        logging.info('Verify Per Client Rate Limiting value AP shell.')
        time.sleep(15)
        try:
            ap_info_list = self.active_ap.get_perclient_rate_limit()
            
            client_mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
            client_ul_rate  = "up_rate:%s" %(self.conf['client_ul_rate'])
            client_dl_rate  = "dn_rate:%s" %(self.conf['client_dl_rate'])

            for ap_info in ap_info_list:
                self.passmsg = 'The per-client rate limit is correct in ActiveAP[%s], ' % (self.active_ap_mac)
                if client_mac_addr.lower() in ap_info:
                    if client_ul_rate not in ap_info:
                        self.errmsg = "client uplink rate(%s) not in AP shell(ap_info:%s)" % (client_ul_rate, ap_info)
                    if client_dl_rate not in ap_info:
                        self.errmsg = "client downlink rate(%s) not in AP shell(ap_info:%s)" % (client_dl_rate, ap_info)
                    if self.errmsg:
                        break
                    self.passmsg += 'client ul_rate:%s, dl_rate:%s, ap_info: %s' % (client_ul_rate,client_dl_rate,ap_info)
                
        except Exception, ex:
            self.errmsg = ex.message
            
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult("PASS", self.passmsg)

    def cleanup(self):
        pass
