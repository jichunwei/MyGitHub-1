'''
This is a simple tea for data plane test (ping test).
. device_type: one of these: ap, zd, client

tea.py u.fm.fmdv_ping_test fm_ip=192.168.0.124 ap_ip=192.168.0.236 client_ip=192.168.1.11"
'''

import logging
import re
from pprint import pformat

from RuckusAutoTest.common.utils import dict_by_keys
from RuckusAutoTest.components import (
    create_fm_by_ip_addr, clean_up_rat_env, create_ap_by_model,
    create_station_by_ip_addr
)
from RuckusAutoTest.common.utils import (
        get_unique_name, is_matched, try_times, log_cfg,
)
from RuckusAutoTest.tests.fm.lib_FM import init_aliases, assoc_client

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

errmsg = None
def do_config(cfg):
    p = _cfg_test_params(cfg)
    #_cfg_ap_monitoring(p)
    _cfg_wlan(p)

    return p


def do_test(p):
    logging.info('Data plane test - ping test')

    _assoc_client(p)
    if errmsg: return dict(result='FAIL', message=errmsg)

    _ping_test(p)
    return dict(
        result='PASS', message='Can ping ap %s from client %s' % (p['ap_ip'], p['client_ip'])
    )


def do_clean_up(p):
    _unassoc_client(p)
    _uncfg_wlan(p)
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res


def _cfg_test_params(cfg):
        p = dict(
            fm_ip =     '192.168.20.252',
            ap_ip =     '192.168.20.171',
            model =     'ZF7942',
            client_ip = '192.168.1.11',
            is_client_associated = True,
            # -- internal variables -----
            get_assoc_client_timeout = 60,
        )
        p.update(cfg)

        p['fm'] = create_fm_by_ip_addr(p.pop('fm_ip'), version='9')
        p['ap'] = create_ap_by_model(p['model'], p['ap_ip'])
        p['client'] = create_station_by_ip_addr(p['client_ip'])
        p['dv'] = p['fm'].get_device_view(ip=p['ap_ip'])

        p.update(dict(
            wlanId=1,
            wlanSsid=get_unique_name(p['ap_ip']),
        ))
        p.update(dict(
            wlanCfg=lib.fm.cfg.get_wlan_cfg('fm', dict(wlan_ssid=p['wlanSsid'])),
            clientWlanCfg=lib.fm.cfg.get_wlan_cfg('client', dict(wlan_ssid=p['wlanSsid'])),
            deviceCfg=dict(
                inform_interval = '10ms',
            ),
        ))
        return p
        logging.debug('Test Configs:\n%s' % pformat(p))


def _cfg_wlan(p):
    lib.fmdv.wlan.cfgWLAN(p['dv'], p['wlanId'], p['wlanCfg'])


def _cfg_ap_monitoring(p):
        logging.info('Configure inform interval and monitoring mode')
        # In case nothing changes then submision is not allowed
        # catch and ignore that exception here
        try:
            lib.fmdv.dev.set(p['dv'], p['deviceCfg'])
        except Exception, e:
            if re.search('Element .*Task #.*', str(e)):
                p['dv'].navigate_to(p['dv'].DETAILS, p['dv'].DETAILS_DEVICE, force=True)
                return
            raise


def _assoc_client(p, tries=3):
    assoc_client(p['client'], p['clientWlanCfg'])


def _ping_test(p, success='ok'):
    msg = p['client'].ping(p['ap_ip'])

    if msg.lower() != success:
        errmsg = ('Cannot ping ap %s from client %s. Detail: %s' %
                  (p['ap_ip'], p['client_ip'], msg))


def _unassoc_client(p):
    p['client'].remove_all_wlan()


def _uncfg_wlan(p):
    lib.fmdv.wlan.cfgWLAN(p['dv'], p['wlanId'],
                         dict(avail='disabled', encrypt_method='disabled',))


def _is_assoc(mac, clients):
    for r in clients:
        if is_matched(row=r, criteria=dict(macaddress=mac), op='seq'):
            return True
    return False


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












