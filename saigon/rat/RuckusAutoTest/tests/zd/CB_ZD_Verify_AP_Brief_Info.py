'''
Verify AP Brief Information.
Exclude:
  . Radio
  . Mesh mode
  . IP/IPv6
which should be in each individual CB)
'''
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Verify_AP_Brief_Info(Test):
    '''
    '''

    def config(self, conf):
        '''
        '''
        self._cfg_init_test_params(conf)


    def test(self):
        '''
        '''
        info = self._get_ap_info_when_connected(
            self.conf['check_status_timeout'], self.conf['break_time']
        )
        if info.get('errmsg'):
            self.errmsg = info['errmsg']

        else:
            result = self._verify_ap_info(info)
            if result['status'] == True:
                self.passmsg = " ".join(result['msg'])

            else:
                self.errmsg = " ".join(result['msg'])

        self._update_carrier_bag()

        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)

        logging.debug(self.passmsg)
        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        '''
        '''


    def _cfg_init_test_params(self, conf):
        '''
        '''
        self.conf = {
            'ap_tag': "",
            'expected_info': {
                'mgmt_vlan': "1",
                'description': "",
                'devname': "RuckusAP",
                'state': "Connected",
                'location': "",
            },
            'check_status_timeout': 300,
            'break_time': 30,
        }
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']

        self.ap_tag = self.conf['ap_tag']
        self.active_ap = self.carrierbag[self.ap_tag]['ap_ins']
        self.ap_mac_addr = self.active_ap.base_mac_addr
        self.expected_info = self.conf['expected_info']

        self.errmsg = ""
        self.passmsg = ""


    def _get_ap_info_when_connected(
            self, check_status_timeout, break_time
        ):
        '''
        '''
        info = {}

        start_time = time.time()
        while True:
            info = lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, self.ap_mac_addr)
            if info and info.get('state') and \
            info['state'].lower().startswith("connected"):
                break

            time.sleep(break_time)
            if time.time() - start_time > check_status_timeout:
                info['errmsg'] = "The AP %s status is NOT connected after %d seconds" % \
                                 (self.ap_tag, check_status_timeout)

        return info


    def _verify_ap_info(self, info):
        '''
        '''
        result = {
            'status': False,
            'msg': [],
        }

        logging.debug("AP brief information:")
        logging.debug(info)

        for k, v in self.expected_info.iteritems():
            if not info.has_key(k):
                result['msg'].append("AP Info does not have '%s' information." % k)

            elif v != info.get(k):
                result['msg'].append("The value of %s is not %s as expected." % (k, v))

        if result.get('msg'):
            return result

        result['status'] = True
        result['msg'].append("All AP information is correct. %s" % self.expected_info)

        return result


    def _update_carrier_bag(self):
        '''
        '''

