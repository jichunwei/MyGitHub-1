"""
"""
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
import libZD_TestConfig as tconfig

class CB_ZD_Verify_Active_Client(Test):

    def config(self, conf):
        self._cfg_init_test_params(conf)


    def test(self):
        self._test_verify_client_info()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)

        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        pass


    def _cfg_init_test_params(self, conf):
        self.conf = {'sta_tag': '',
                     'expected_info': {},
                     'info_cat': 'brief' #['brief', 'detail']
                     }
        self.conf.update(conf)
        self.expected_info = self.conf['expected_info']
        
        if self.expected_info.has_key('ap_tag') and self.expected_info['ap_tag']:
            active_ap = tconfig.get_testbed_active_ap(self.testbed, self.expected_info['ap_tag'])
            self.expected_info['ap'] = active_ap.base_mac_addr
            self.expected_info.pop('ap_tag')

        sta = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        self.sta_mac = sta.get_wifi_addresses()[1]

        self.zd = self.testbed.components['ZoneDirector']

        self.errmsg = ''
        self.passmsg = ''


    def _test_verify_client_info(self):
        '''
        '''
        if 'brief' == self.conf['info_cat']:
            sta_info = lib.zd.cac.get_client_brief_by_mac_addr(
                           self.zd, self.sta_mac
                       )

        elif 'detail' == self.conf['info_cat']:
            sta_info = lib.zd.cac.get_client_detail_by_mac_addr(
                           self.zd, self.sta_mac
                       )

        else:
            self.errmsg = 'Invalid info_cat provided'
            return

        logging.debug(sta_info)
        err_keys = []
        for k, v in self.expected_info.iteritems():
            if str(sta_info[k]) != str(v):
                err_keys.append(k)

        if not err_keys:
            self.passmsg = 'All client info is as expected.'

        else:
            self.errmsg = 'Not all client info are as expected: %s' % err_keys

