'''
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Verify_AP_Port_Override(Test):

    def config(self, conf):
        '''
        '''
        self._cfg_init_test_params(conf)


    def test(self):
        '''
        '''
        info = lib.zd.ap.get_ap_port_config_by_mac(self.zd, self.ap_mac_addr)

        result = self._test_verify_ap_port_override(info)
        if result['status'] == True:
            self.passmsg = " ".join(result['msg'])

        else:
            self.errmsg = " ".join(result['msg'])

        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)

        logging.debug(self.passmsg)
        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        '''
        '''
        pass


    def _cfg_init_test_params(self, conf):
        '''
        '''
        self.conf = {
            'ap_tag': "",
            'expected_info': {},
        }
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']

        self.ap_tag = self.conf['ap_tag']
        self.active_ap = self.carrierbag[self.ap_tag]['ap_ins']
        self.ap_mac_addr = self.active_ap.base_mac_addr
        self.expected_info = self.conf['expected_info']

        self.errmsg = ""
        self.passmsg = ""


    def _test_verify_ap_port_override(self, info):
        '''
        '''
        result = {
            'status': False,
            'msg': [],
        }

        logging.debug("AP Port settings:")
        logging.debug(info)

        for k, v in self.expected_info.iteritems():
            if not info.has_key(k):
                result['msg'].append("AP Port does not have '%s' information." % k)

            elif v != info.get(k):
                result['msg'].append("The value of %s is not %s as expected." % (k, v))

        if result.get('msg'):
            return result

        result['status'] = True
        result['msg'].append("All AP Port information is correct. %s" % self.expected_info)

        return result

