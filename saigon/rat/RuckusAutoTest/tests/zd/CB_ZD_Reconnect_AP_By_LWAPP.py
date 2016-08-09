'''
Description: This script is used to reboot AP onm ZD WebUI: Monitor -> Access Points -> Reboot.
@author: An Nguyen, an.nguyen@ruckuswireless.com
@since: May 2012


From 9.4 the ZD support FQDN which makes this API out of date. Use this by risk.
'''

import logging

from RuckusAutoTest.models import Test

class CB_ZD_Reconnect_AP_By_LWAPP(Test):
    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._reconnect_ap_to_zd_by_lwapp()
                
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'ap_tag': '',
                     'mode': 'l3',
                     'discovery_method': '',
                     }
        self.conf.update(conf)
        
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.zd = self.testbed.components['ZoneDirector']
        
        self.errmsg = ''
        self.passmsg = ''
    
    def _update_carrier_bag(self):
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins'] = self.active_ap

    def _reconnect_ap_to_zd_by_lwapp(self):
        logging.info('Configure VLAN assignment for connected AP port')
        try:
            self.testbed.configure_ap_connection_mode(self.active_ap.base_mac_addr, 
                                                      self.conf['mode'], 
                                                      self.conf['discovery_method'])
            self.passmsg = 'The AP[%s] reconnected to ZD as expected setting' % self.active_ap.base_mac_addr
            logging.info(self.passmsg)
        except Exception, e:
            self.errmsg = '[Reconnect AP as %s mode failed] %s' % (self.conf['mode'], e.message)
            logging.info(self.errmsg)              