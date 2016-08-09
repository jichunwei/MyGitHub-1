'''
Verify ZD Ethernet Information by GUI.
'''
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.zd import system_info as sys

class CB_ZD_Verify_ZD_Ethernet_Info(Test):
    '''
    '''

    def config(self, conf):
        '''
        '''
        self._cfg_init_test_params(conf)


    def test(self):
        '''
        '''
        info = sys.get_all_zd_ethernet_info(self.zd)
        if not info:
            self.errmsg = 'Get ZD Ethernet info from monitor page failed!' 
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)

        self._verify_zd_ethernet_info(info)
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

        self.errmsg = ""
        self.passmsg = ""


    def _verify_zd_ethernet_info(self, info_list):
        '''
        '''
        zd_mac = self.zd.mac_addr

        for info in info_list:
            status = info['status'].lower()
            if info['port_id'] == '0':
                if status != 'up':
                    self.errmsg += 'ZD Ethernet port 0 status is down, unexpected value!'

                if info['mac'].lower() != zd_mac.lower():
                    self.errmsg += 'ZD[%s] Ethernet port 0 MAC is shown as [%s], unexpected value!' % (zd_mac, info['mac'])

                if info['input_pkts'] == '0':
                    self.errmsg += 'ZD Ethernet port 0 input packets num is 0, unexpected value!'

                if info['input_bytes'] == '0':
                    self.errmsg += 'ZD Ethernet port 0 input bytes num is 0, unexpected value!'

                if info['output_pkts'] == '0':
                    self.errmsg += 'ZD Ethernet port 0 output packets num is 0, unexpected value!'

                if info['output_bytes'] == '0':
                    self.errmsg += 'ZD Ethernet port 0 output bytes num is 0, unexpected value!'
            else:
                if status == 'up':
                    self.errmsg += 'AP[%s] Ethernet port [%s] status is up, unexpected value!' % (self.ap_mac_addr, info['port'])

                if info['input_pkts'] != '0':
                    self.errmsg += 'ZD Ethernet port [%s] input packets num[%s] should be 0!' % (info['input_pkts'], info['port'])

                if info['input_bytes'] != '0':
                    self.errmsg += 'ZD Ethernet port [%s] input bytes num[%s] should be 0!' % (info['input_bytes'], info['port'])

                if info['output_pkts'] != '0':
                    self.errmsg += 'ZD Ethernet port [%s] output packets num[%s] should be 0!' % (info['output_pkts'], info['port'])

                if info['output_bytes'] != '0':
                    self.errmsg += 'ZD Ethernet port [%s] output bytes num[%s] should be 0!' % (info['output_bytes'], info['port'])

            if info['eth_name'] != ('eth%s' % info['port_id']):
                self.errmsg += 'ZD Ethernet port [%s] name is %s, unexpected value!' % (info['port'], info['interface'])

            if info['speed'].lower() != '1000mbps':
                self.errmsg += 'ZD Ethernet port [%s] speed is %s, unexpected value!' % (info['port'], info['speed'])

    def _update_carrier_bag(self):
        '''
        '''
