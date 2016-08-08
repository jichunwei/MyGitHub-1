'''
This test script is to verify following authentication types:
5    ZF2925 8.0 wireless Authentication
5.1    Open System
5.2.1    Open-WEP-64-5 ascii
5.2.2    Open-WEP-64-10 hex
5.3.1    Open-WEP-128-13 ascii
5.3.2    Open-WEP-128-26 hex
5.4.1    Shared-WEP-64-5 ascii
5.4.2    Shared-WEP-64-10 hex
5.5.1    Shared-WEP-128-5 ascii
5.5.2    Shared-WEP-128-10 hex
5.6    WPA-PSK-TKIP
5.7    WPA-PSK-AES
5.8    WPA2-PSK-TKIP
5.9    WPA2-PSK-AES
5.10    WPA-TKIP
5.11    WPA-AES
5.12    WPA2-TKIP
5.13    WPA2-AES

Test Procedure:
1.    Login the FlexMaster webUI by admin account.
2.    Go to Inventory page, click on a device to enter Device View page.
3.    Go to Details > Wireless tab and configure a wlan with above authentication types
4.    Use a laptop to associcate to that wlan and ping a target and make sure it does successfully
5.    Log out the FlexMaster web UI.

Pass/Fail/Error Criteria (including pass/fail messages):
+ Pass: if all of the verification steps in the test case are met.
+ Fail: if one of verification steps is failed.
+ Error: Other unexpected events happen.

'''
import logging
import re
import copy
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.fm.lib_FM import init_aliases, assoc_client
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.fm.config_mapper_fm_old import map_station_cfg


class FMDV_WlanManager(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = None
        self._cfgTestParams(**conf)
        self._unassoc_client()


    def test(self):
        self._cfgWlan()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._assoc_client()
        if self.errmsg: return ('FAIL', self.errmsg)

        # Only test association for this testing
        #self._testConsistentUI()
        #if self.errmsg: return ('FAIL', self.errmsg)

        self._testPingStatus()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)


    def cleanup(self):
        self._unassoc_client()
        self._uncfgWlan()
        self.aliases.fm.cleanup_device_view(self.dv)
        self.aliases.fm.logout()


    def _cfgTestParams(self, **kwa):
        self.p = {
            'ap_ip':     '192.168.0.222',
            'client_ip': '192.168.1.11',
            'cfg':  {},
            'rad_cfg': dict(
                username = 'user.eap',
                password = '123456',
            ),
            'test_name': 'Open System'
        }
        self.p.update(kwa)

        if 'encrypt_method' not in self.p['cfg']:
            self.p['cfg']['encrypt_method'] = 'disabled'

        self.aliases = init_aliases(testbed=self.testbed)
        self.ap = self.aliases.tb.getApByIp(self.p['ap_ip'])
        self.dv = self.aliases.fm.get_device_view(ip=self.p['ap_ip'])
        self.client = self.aliases.tb.get_clientByIp(self.p['client_ip'])
        #self.p['wlan'] = int(self.p['cfg'].pop('wlan_num'))

        # remove items, which are not available on AP web ui, in the test cfg
        ap_unsupported_items = ['client_isolation']
        for k in ap_unsupported_items:
            if k in self.p['cfg']: del self.p['cfg'][k]

        logging.info('Test configs:\n%s' % pformat(self.p))


    def _cfgWlan(self):
        try:
            ret, msg = lib.fmdv.wlan.cfgWLANDet(self.dv, self.p['cfg'])
            if ret != self.dv.TASK_STATUS_SUCCESS:
                self.errmsg = msg
                logging.info(msg)
        except Exception, e:
            # Filtered Exception: Element ".*Task.*" is not found
            # xpath: //div[contains(@class, 'displayDiv')]//*[contains(tr, 'Task #')]
            if re.search('Element ".*Task.*" is not found', str(e)):
                self.dv.navigate_to(self.dv.DETAILS, self.dv.DETAILS_WIRELESS, force=True)
                return
            raise


    def _assoc_client(self):
        client_cfg = copy.deepcopy(self.p['cfg'])
        client_cfg.update(self.p['rad_cfg'])

        client_cfg = map_station_cfg(client_cfg)
        logging.info('Client config: %s' % pformat(client_cfg))
        assoc_client(self.client, client_cfg)


    def _compareTwoDicts(self, dict_1, dict_2):
        '''
        This function is to compare values of two dictionaries. Note, two dictionaries
        has the same keys.
        '''
        msg = ''
        for k in dict_1.iterkeys():
            if dict_1[k].lower() != dict_2[k].lower():
                msg += 'Error: Item "%s" has difference (%s,%s)\n' % (k, dict_1[k], dict_2[k])
                #return False

        return msg


    def _testConsistentUI(self):
        '''
        This function is to make sure Device View and AP web UI show
        the input cfg exactly
        '''
        logging.info('Test conistent FM Device View and AP Web UI')
        # Get cfg from Device View in simple input values
        cfg = copy.deepcopy(self.p['cfg'])
        wlan = int(cfg.pop('wlan_num'))

        dv_ui_cfg = lib.fmdv.wlan.getWLAN(self.dv, wlan, cfg.keys())
        logging.info('Got configs from Device View:\n%s' % pformat(dv_ui_cfg))

        self.ap.start()
        # convert from fm keys to ap keys before getting the cfg from AP
        apKs = lib.ap.wlan.convert_key_input_wlan_det_cfg_fm_ap(cfg.keys(), to_ap=True)
        ap_ui_cfg = lib.ap.wlan.getWLAN(self.ap, wlan, apKs, fm_return=True)

        logging.info('After map to simple value: AP cfg: %s' % pformat(ap_ui_cfg))
        self.ap.stop()

        # Come here, two dv_ui_cfg and ap_ui_cfg will have the same keys
        msg = self._compareTwoDicts(dv_ui_cfg, ap_ui_cfg)
        if msg:
            self.errmsg = msg
            return

        logging.info('Device View and AP Web UI is consistent')


    def _testPingStatus(self):
        '''
        '''
        msg = self.client.ping(self.p['ap_ip'], 5000)
        if re.match('.*timeout.*', msg, re.I):
            self.errmsg = 'Cannot ping the target ip "%s"' % self.p['ap_ip']
            return

        self.passmsg = 'The wireless authentication "%s" works correctly' % self.p['test_name']


    def _unassoc_client(self):
        self.client.remove_all_wlan()


    def _uncfgWlan(self):
        # We should copy to another variable to avoid changing the input cfg. In case
        # the test fail, the input cfg will be used again so if we change the input
        # cfg here it causes the rat failed to re-run again.
        default_cfg = copy.deepcopy(self.p['cfg'])
        default_cfg.update(dict(
            wlan_name         = 'Wireless %s' % self.p['cfg'].get('wlan_num', ''),
            wlan_ssid         = 'Wireless %s' % self.p['cfg'].get('wlan_num', ''),
            avail             = 'disabled',
            encrypt_method = 'disabled'
        ))
        try:
            lib.fmdv.wlan.cfgWLANDet(self.dv, default_cfg)
        except Exception, e:
            logging.info('Warning: Cannot restore default config for this wlan. '
                         'Error: %s' % e.__str__())

