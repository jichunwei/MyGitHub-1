'''
Verify AP Ethernet Information by GUI.
'''
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Verify_AP_Detail_Info(Test):
    '''
    '''

    def config(self, conf):
        '''
        '''
        self._cfg_init_test_params(conf)


    def test(self):
        '''
        '''
        info = lib.zd.aps.get_ap_detail_by_mac_addr(self.zd, self.ap_mac_addr)
        if not info:
            self.errmsg = 'Get AP[%s] detail info by its MAC failed!' % self.ap_mac_addr 
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)

        self._verify_ap_lan_status(info['lan_status'])
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)

        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        '''
        '''
        self._update_carrier_bag()


    def _cfg_init_test_params(self, conf):
        '''
        '''
        self.conf = {'port_status': 'enable'}
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']
        self.ap_tag = self.conf['ap_tag']
        self.active_ap = self.carrierbag[self.ap_tag]['ap_ins']
        self.ap_mac_addr = self.active_ap.base_mac_addr

        self.errmsg = ""
        self.passmsg = ""


    def _verify_ap_lan_status(self, info_list):
        '''
        '''
        for info in info_list:
            logical = info['logical'].lower()
            physical = info['physical'].lower()
            
            if info['port'] == '0' and self.conf['port_status'] == 'enable':
                flag = True
                if 'up' not in logical:
                    self.errmsg += 'AP[%s] Ethernet port 0 logical status is down, unexpected value !' % (self.ap_mac_addr)
                if 'up' not in physical:
                    self.errmsg += 'AP[%s] Ethernet port 0 physical status is down, unexpected value !' % (self.ap_mac_addr)
            else:
                if 'up' in logical:
                    self.errmsg += 'AP[%s] Ethernet port [%s] logical status is up, unexpected value!' % (self.ap_mac_addr, info['port'])
                if 'up' in physical:
                    self.errmsg += 'AP[%s] Ethernet port [%s] physical status is up, unexpected value!' % (self.ap_mac_addr, info['port'])

            if info['interface'] != ('eth%s' % info['port']):
                self.errmsg += 'AP[%s] Ethernet port [%s] name is %s, unexpected value!' % (self.ap_mac_addr, info['port'], info['interface'])


    def _update_carrier_bag(self):
        '''
        '''
