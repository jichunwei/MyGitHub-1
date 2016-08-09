'''
Enable AP Ethernet interface from L3 switch
'''
import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Enable_AP_Interface(Test):
    '''
    '''

    def config(self, conf):
        '''
        '''
        self._cfg_init_test_params(conf)


    def test(self):
        '''
        '''
        logging.info("Enable the switch port %s connected to the AP [%s]" \
                    % (self.active_ap_connection_port,
                       self.apmac))
        try:
            self.l3switch.enable_interface(self.active_ap_connection_port)
        except:
            self.errmsg = 'Disable the switch port failed!'
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)

        time0 = time.time()
        wait_time = 180
        while(True):
            current_time = time.time()
            if  (current_time-time0) >wait_time:
                self.errmsg += 'active AP not connected to ZD when enable AP interface in L3 switch, '
                break

            try:
                ap_info= lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, self.apmac)
                if ap_info['state'].lower().startswith('connected'):
                    break
            except:
                pass

            time.sleep(3)

        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        '''
        '''
        self._update_carrier_bag()


    def _cfg_init_test_params(self, conf):
        '''
        '''
        self.conf = {}
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']
        self.l3switch = self.testbed.components['L3Switch']

        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.apmac = self.active_ap.base_mac_addr
        self.active_ap_connection_port = self.testbed.mac_to_port[self.apmac]

        self.errmsg = ""
        self.passmsg = ""


    def _update_carrier_bag(self):
        '''
        '''