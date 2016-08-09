'''
NOTES:
3.6.1.4    Change the AP channel via Device View with wireless radio 1 2.4GHz mode.
3.6.1.6    Change the AP Country Code via Device View with wireless radio 1 2.4GHz mode
3.6.1.8    Change the AP channel band width to 20MHz via Device View with wireless radio 1 2.4GHz mode
3.6.1.10    Change the AP channel band width to 40MHz via Device View with wireless radio 1 2.4GHz mode.
3.6.1.12    Enable the Wireless Interface availability via Device View with wireless radio 1 2.4GHz mode
3.6.1.14    Enable the Wireless Broadcast SSID via Device View with wireless radio 1 2.4GHz mode
3.6.1.16    Change the Wireless encryption to WEP via Device View with wireless radio 1 2.4GHz mode
3.6.1.18    Change the Wireless encryption to WPA via Device View with wireless radio 1 2.4GHz mode

3.6.2.4    Change the AP channel via Device View with radio mode for 5GHz only
3.6.2.6    Change the AP Country Code via Device View with wireless radio 2 for 5GHz.
3.6.2.8    Change the AP channel band width to 20MHz via Device View with wireless radio 2 for 5GHz
3.6.2.10    Change the AP channel band width to 40MHz via Device View with wireless radio 2 for 5GHz
3.6.2.12    Enable the Wireless Interface availability via Device View with wireless radio 2 5GHz mode
3.6.2.14    Enable the Wireless Broadcast SSID via Device View with wireless radio 2 5GHz mode
3.6.2.16    Change the Wireless encryption to WEP via Device View with wireless radio 2 5GHz mode
3.6.2.18    Change the Wireless encryption to WPA via Device View with wireless radio 2 5GHz mode


Procedure for 3.6.1.1.1, 3.6.1.2.1, 3.6.2.1.1, 3.6.2.2.1:
   It's very simple. Just to make sure channel list/country code are consistent
   between the cfg template for 7962 and 7962 AP web UI.

Test Procedure for the orther ones: The procedure should be the same with
CfgUpgrade testsuite
    1. Log in FM as admin account
    2. Create a configuration template
    3. Go to Configure > Configuration Upgrade, create a config upgrade to
       provision the config template to that AP.
    4. Make sure the task is success and all configured items provisioned
       to that AP.

Pass/Fail/Error Criteria (including pass/fail messages):
+ Pass: if all of the verification steps in the test case are met.
+ Fail: if one of verification steps is failed.
+ Error: Other unexpected events happen.
'''

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.fm.lib_FM import *
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.fm.config_mapper_fm_old import *

class FMDV_Dalmatian_CfgUpgrade(Test):
    def config(self, cfg):
        self.errmsg = self.passmsg = None
        self._cfg_test_params(cfg)

    def test(self):
        self._do_pre_cfg_wlan()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._cfg_wlan()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_result()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        logging.info('Cleaning up the test...')
        self._reset_ap_factory()
        self._set_fm_url()
        self.fm.cleanup_device_view(self.dv)
        self.fm.logout()

    def _cfg_test_params(self, cfg):
        self.p = dict(
            ap_ip = '',
            model = 'ZF7962',
            input_cfg = {},
            test_name = '',
            radio_mode = '2.4',
            pre_cfg = {},
        )
        self.p.update(cfg)
        self.radio_mode = {
            '2.4G': lib.ap.wlan.DUAL_BAND_RD_MODE_1,
            '5G': lib.ap.wlan.DUAL_BAND_RD_MODE_2,
        }[self.p['radio_mode'].upper()]

        init_coms(self, dict(tb=self.testbed, ap_ip=self.p['ap_ip']))
        self.dv = self.fm.get_device_view(ip=self.p['ap_ip'])

        logging.info('Test configs:\n%s' % pformat(self.p))

    def _wait_for_ap_cpu_free(self):
        '''
        This function is to check CPU usage of AP and wait for each ready to test.
        Note: if provide username password, this function will use that username/password
        instead of username/password from ap instance to connect to AP and monitor its CPU usage.
        '''
        # monitor AP CPU usage to wait for its load < 40% after rebooting or provisioning
        MONITOR_CPU_USAGE = 0

        monitor_cpu_cfg= {
            #'config': config,
            'monitor': MONITOR_CPU_USAGE,
            'threshold': 10, # default % CPU Usage
            'timeout': 20, # in minute
            'interval': 2,
            'times_to_check': 3,
        }

        monitor_cpu_cfg.update(dict(config={'ip_addr': self.p['ap_ip']}))
        msg = 'CPU of AP %s looks free for the test' % self.p['ap_ip']\
                if wait4_ap_stable(**monitor_cpu_cfg) else \
                ('WARNING: The CPU usage of AP %s is still too high' % self.p['ap_ip'])
        logging.info(msg)

    def _wait_for_ap_ready(self):
        '''
        This function will check if provision some configuration items which
        require AP rebooted. In this case it will sleep a moment to wait for
        AP ready to use again.
        Note: Current we only have some items which take time to provision.
            1. 'wmode', 'country_code': take time to reboot
            2. 'downlink', 'uplink': Rate Limiting takes time to apply.

            If there are more items, we will add more
        '''
        k = 'wlan_common' #a.cfm['PRO_WLAN_COMMON_TITLE']
        item1 = 'wmode'
        item2 = 'country_code'

        logging.info('Wait for AP ready to test')

        if self.p['input_cfg'].has_key(k) and \
           (self.p['input_cfg'][k].has_key(item1) or\
           self.p['input_cfg'][k].has_key(item2)):
            # sleep to wait for the first AP enter into reboot progress.
            logging.info('The test requires AP reboot...')
            config = get_ap_default_cli_cfg()
            ap_config = self.ap.get_cfg()
            config.update(ap_config)

            if not wait4_ap_up(**{'config': config, 'timeout': 6}):
                self.errmsg += 'Cannot login to AP via cli %s after 6 mins waiting' \
                                % (config['ip_addr'])

        self._wait_for_ap_cpu_free()

    def _do_pre_cfg_wlan(self):
        # if the pre_cfg is empty, return
        if not self.p['pre_cfg']: return
        try:
            if lib.fmdv.wlan.set(self.dv, self.p['pre_cfg'], self.radio_mode):
                logging.info('Did pre-configure successfully')
            else:
                logging.info('Warning: Cannot do pre-configure')
        except Exception, e:
            log_trace()
            logging.info(
                'Warning: Exception occurs while doing pre-configure. Detail: %s' %
                e.__str__()
            )

    def _cfg_wlan(self):
        if lib.fmdv.wlan.set(self.dv, self.p['input_cfg'], self.radio_mode):
            logging.info('Configured from Device View successfully')
        else:
            self._fill_error_msg('Cannot configure from Device View')

    def _filter_unused_keys_on_ap(self, fm_cfg):
        '''
        This function is to remove unnecessary items of WLAN detail before doing
        the comparison with info got from AP.
        Input:
        - kwargs is the list of WLAN Det parameters
        '''
        removed_items = ['client_isolation', 'rate_limiting', 'cwep_pass',
                        'cpsk_passphrase', 'cauth_secret', 'cacct_secret', 'wlan_num']

        options = copy.deepcopy(fm_cfg)
        MIN_WLAN = 1
        MAX_WLAN = 16
        # Remove unnecessary forr wlan 1 to 16
        for i in range(MIN_WLAN, MAX_WLAN+1):
            k = 'wlan_%d' % i # a.cfm['PRO_WLAN_%d_TITLE' % i]
            if options.has_key(k):
                # Add necessary items first
                #if temp.has_key('rate_limiting') and temp['rate_limiting'].lower() == 'disabled':
                #    # Add uplink/donwlink key for commparison
                #    # Zero is value of uplink/downlink when Rate Limiting is DISABLED
                #    temp['downlink'], temp['uplink'] = '0', '0'

                # Then remove unused items for comparison
                for item in removed_items:
                    if options[k].has_key(item): del options[k][item]

        removed_items = ['password', 'cpassword']
        k = 'device_general' # a.cfm['PRO_DEV_GENERAL_TITLE']
        if options.has_key(k):
            for item in removed_items:
                if options[k].has_key(item): del options[k][item]

        return options

    def _test_result(self):
        ''''''
        logging.info('Verify AP web ui after provisioning cfg from Device View')

        # TODO: currently, makefmtestbed only supports to add one ap for each test.
        # Hence, we need to consider supporting to verify more than one ap here
        input_cfg, MAX_RETRIES, PAUSE_TIME = self.p['input_cfg'], 3, 20
        input_cfg = self._filter_unused_keys_on_ap(input_cfg)
        # define ap, dv keys from input config to get the config from DV and AP UI
        ap_cfg_ks, dv_cfg_ks = {}, {}
        for item, ks in input_cfg.iteritems():
            ap_cfg_ks[item] = input_cfg[item].keys()
            dv_cfg_ks[item] = input_cfg[item].keys()

        self._wait_for_ap_cpu_free()
        self.ap.start(15)

        for i in try_times(MAX_RETRIES, PAUSE_TIME):
            msg = None
            try:
                ap_data, dv_data = {}, {}
                ap_data = lib.ap.wlan.get(self.ap, ap_cfg_ks, True, True, self.radio_mode)
                dv_data = lib.fmdv.wlan.get(self.dv, dv_cfg_ks, self.radio_mode)
                logging.info('DV cfg: %s. \nAP cfg: %s' %
                             (pformat(dv_data), pformat(ap_data)))
                msg = compare_dict(dv_data, ap_data, tied_compare=False)
            except Exception, e:
                msg = e.__str__()
                log_trace()
            if not msg:
                    break
            elif i < MAX_RETRIES:
                logging.info('Found error: %s. Sleep %s(s) a try again...' %
                             (pformat(msg), PAUSE_TIME))
            else:
                self._fill_error_msg(msg)

        self.ap.stop()
        if not self.errmsg:
            logging.info('All APs are provisioned config successully')
            self._fill_pass_msg()

    def _fill_error_msg(self, errmsg):
        self.errmsg = 'The test "%s" has error:" %s' % (self.p['test_name'], errmsg)
        logging.info(self.errmsg)

    def _fill_pass_msg(self):
        self.passmsg = 'The test "%s" works correctly' % self.p['test_name']
        logging.info(self.passmsg)

    def _reset_ap_factory(self):
        ''''''
        logging.info('Reset factory the test ap...')
        # Next, wait for the test AP boot up
        ap_cli_cfg = get_ap_default_cli_cfg()
        ap_cli_cfg.update(self.ap.get_cfg())
        if not set_ap_factory(config=ap_cli_cfg):
                logging.info('Warning: Cannot set factory the test AP')

    def _set_fm_url(self):
        ''''''
        try:
            fm_url = 'http://%s/intune/server' % self.fm.get_cfg()['ip_addr']
            logging.info('Set fm url %s for the test ap' % fm_url)
            self._wait_for_ap_cpu_free()
            self.ap.start(15)
            lib.ap.acc.set(self.ap, dict(fm_url=fm_url))
            self.ap.stop()
        except Exception, e:
            log_trace()
            logging.info('Warning: Unexpected error happens: %s' % e.__str__())
