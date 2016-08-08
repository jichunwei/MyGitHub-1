import logging
import re
from pprint import pformat

from RuckusAutoTest.common.utils import (
        get_unique_name, is_matched, try_times, log_cfg,
)
from RuckusAutoTest.tests.fm.lib_FM import init_aliases, assoc_client

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib


class FMDV_ClientAssocs(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = ''
        self._cfg_test_params(conf)
        self._cfg_ap_monitoring()
        self._cfgWlan()


    def test(self):
        if self.p['is_client_associated']:
            self._assoc_client()
            if self.errmsg: return ('FAIL', self.errmsg)

        self._testDvAssocStatus()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)


    def cleanup(self):
        self._unassoc_client()
        self._uncfgWlan()
        self.aliases.fm.cleanup_device_view(self.dv)
        self.aliases.fm.logout()


    def _cfg_test_params(self, cfg):
        self.p = dict(
            ap_ip =     '192.168.20.171',
            client_ip = '192.168.1.11',
            mode =      'active',
            interval =  '5', # secs
            is_client_associated = True,
            # -- internal variables -----
            get_assoc_client_timeout = 60,
        )
        self.p.update(cfg)

        if self.p['mode'] == 'disabled' or not self.p['is_client_associated']:
            self.p['get_assoc_client_timeout'] = 20

        self.aliases = init_aliases(testbed=self.testbed)
        self.ap = self.aliases.tb.getApByIp(self.p['ap_ip'])
        self.dv = self.aliases.fm.get_device_view(ip=self.p['ap_ip'])
        self.client = self.aliases.tb.get_clientByIp(self.p['client_ip'])

        self.p.update(dict(
            wlanId=1,
            wlanSsid=get_unique_name(self.p['ap_ip']),
        ))
        self.p.update(dict(
            wlanCfg=lib.fm.cfg.get_wlan_cfg('fm', dict(wlan_ssid=self.p['wlanSsid'])),
            clientWlanCfg=lib.fm.cfg.get_wlan_cfg('client', dict(wlan_ssid=self.p['wlanSsid'])),
            deviceCfg=dict(
                inform_interval = '10ms',
            ),
        ))
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _cfgWlan(self):
        lib.fmdv.wlan.cfgWLAN(self.dv, self.p['wlanId'], self.p['wlanCfg'])


    def _cfg_ap_monitoring(self):
        logging.info('Configure inform interval and monitoring mode')
        # In case nothing changes then submision is not allowed
        # catch and ignore that exception here
        try:
            lib.fmdv.dev.set(self.dv, self.p['deviceCfg'])
        except Exception, e:
            if re.search('Element .*Task #.*', str(e)):
                self.dv.navigate_to(self.dv.DETAILS, self.dv.DETAILS_DEVICE, force=True)
                return
            raise


    def _assoc_client(self, tries=3):
        assoc_client(self.client, self.p['clientWlanCfg'])


    def _unassoc_client(self):
        self.client.remove_all_wlan()


    def _uncfgWlan(self):
        lib.fmdv.wlan.cfgWLAN(self.dv, self.p['wlanId'],
                              dict(avail='disabled', encrypt_method='disabled',))


    def _is_assoc(self, mac, clients):
        for r in clients:
            if is_matched(row=r, criteria=dict(macaddress=mac), op='seq'):
                return True
        return False


    def _testDvAssocStatus(self):
        '''
        . Try 3 times to make sure getting the latest info
        '''
        result_map = {
            (True, True):   (True,  'Client (%s) is found on the associated client list'),
            (False, False): (True,  'Client (%s) is NOT found on the associated client list'),
            (True, False):  (False, 'Client (%s) is NOT found on the associated client list'),
            (False, True):  (False, 'Client (%s) is found on the associated client list'),
        }
        client_mac = self.client.get_wifi_addresses()[1]
        logging.info('Find the client (%s) in the client list:' % client_mac)
        for t in try_times(3, 1):
            assoc_clients = lib.fmdv.summary.getAssocClients(
                self.dv, self.p['wlanId'], self.p['get_assoc_client_timeout']
            )
            log_cfg(assoc_clients)
            is_pass, msg = result_map[(self.p['is_client_associated'],
                                       self._is_assoc(client_mac, assoc_clients))]
            msg %= client_mac
            if is_pass:
                self.passmsg = msg
                return
            logging.info('Unexpected result (%s times). Try to get it again.' % t)
        self.errmsg = msg
        return



