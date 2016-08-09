'''
NOTES:
3.6.1.1.1    The AP Country Code list via Template should be consist with wireless radio 1 2.4GHz by standalone AP
3.6.1.2.1    The AP Channel List via Template should be consist with standalone AP with wireless radio 1 2.4GHz.
3.6.1.3    Change the AP channel via Template with Wireless radio 1 2.4GHz mode.
3.6.1.5    Change the AP Country Code via Template with wireless radio 1 2.4GHz mode
3.6.1.7    Change the AP channel band width to 20MHz via Template with wireless radio 1 2.4GHz mode
3.6.1.9    Change the AP channel band width to 40MHz via Template with wireless radio 1 2.4GHz mode.
3.6.1.11    Enable the Wireless Interface availability via Template with wireless radio 1 2.4GHz mode
3.6.1.13    Enable the Wireless Broadcast SSID via Template with wireless radio 1 2.4GHz mode
3.6.1.15    Change the Wireless encryption to WEP via Template with wireless radio 1 2.4GHz mode
3.6.1.17    Change the Wireless encryption to WPA via Template with wireless radio 1 2.4GHz mode

3.6.2.1.1    The AP Country Code via Template list should be consist with wireless radio 2 for 5GHz  by standalone AP
3.6.2.2.1    The AP Channel List via Template should be consist with standalone AP with wireless radio 2 for 5GHz.
3.6.2.3    Change the AP channel via Template with wireless radio 2 for 5GHz
3.6.2.5    Change the AP Country Code via Template with wireless 2 radio for 5GHz
3.6.2.7    Change the AP channel band width to 20MHz via Template with radio mode for 5GHz only.
3.6.2.9    Change the AP channel band width to 40MHz via Template with wireless radio 2 for 5GHz.
3.6.2.11    Enable the Wireless Interface availability via Template with wireless radio 2 5GHz mode.
3.6.2.13    Enable the Wireless Broadcast SSID via Template with wireless radio 2 5GHz mode.
3.6.2.15    Change the Wireless encryption to WEP via Template with wireless radio 2 5GHz mode
3.6.2.17    Change the Wireless encryption to WPA via Template with wireless radio 2 5GHz mode


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
import logging
import copy
import re
from pprint import pformat

from RuckusAutoTest.common.utils import get_timestamp, compare_dict

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.fm.lib_FM import init_coms, log_trace, \
        wait4_ap_stable, get_ap_default_cli_cfg, \
        wait4_ap_up, try_times, set_ap_factory
from RuckusAutoTest.components import Helpers as lib


class FM_Dalmatian_CfgUpgrade(Test):
    def config(self, cfg):
        self.errmsg = self.passmsg = None
        self._cfg_test_params(cfg)

    def test(self):
        self._create_cfg_tmpl()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._create_task()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_result()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        logging.info('Cleaning up the test...')

        self._delete_test_cfg_tmpl()
        self._reset_ap_factory()
        self._set_fm_url()

        self.fm.logout()

    def _cfg_test_params(self, cfg):
        self.p = dict(
            ap_ip = '',
            model = 'ZF7962',
            input_cfg = {},
            test_type = 'create', # no use this now
            test_name = '',
            schedule = 0, # O to perform now, > 0 to perform later,
            provision_to = dict(
                device = 'ap ip', # or group = 'Group name'
            ),
        )
        self.p.update(cfg)

        time_stamp = get_timestamp()
        # Add basic param to do test cfg upgrade for
        # Basic param 1: create a config param for cfg template
        self.p.update(
            tmpl_cfg = dict(
                template_name = 'cfg_tmpl_%s_%s' % (self.p['model'], time_stamp),
                template_model = self.p['model'].upper(),
                cfg = self.p['input_cfg'],
            )
        )
        # Basic param 2: create a config param to create for cfg upgrade
        self.p.update(
            upgr_cfg = dict(
                task_name = 'cfg_upgrade_%s_%s' % (self.p['model'], time_stamp),
                template_name = self.p['tmpl_cfg']['template_name'],
                template_model = self.p['tmpl_cfg']['template_model'],
                provision_to = self.p['provision_to'],
                schedule = self.p['schedule'],
            )
        )
        init_coms(self, dict(tb=self.testbed, ap_ip=self.p['ap_ip']))
        logging.info('Test configs:\n%s' % pformat(self.p))

    def _create_cfg_tmpl(self):
        try:
            lib.fm.cfg_tmpl.create_cfg_tmpl_2(
                self.fm, self.p['tmpl_cfg']['template_name'],
                self.p['tmpl_cfg']['template_model'], self.p['tmpl_cfg']['cfg']
            )
            logging.info('Created a template "%s" successfully' % self.p['tmpl_cfg']['template_name'])
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())

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
            #config['ip_addr'] = ap_config['ip_addr']
            #config['username'] = ap_config['username'] if not change_username else change_username
            #config['password'] = ap_config['password'] if not change_password else change_password
            if not wait4_ap_up(**{'config': config, 'timeout': 6}):
                self.errmsg += 'Cannot login to AP via cli %s after 6 mins waiting' \
                                % (config['ip_addr'])

        self._wait_for_ap_cpu_free()

    def _create_task(self):
        try:
            ts, detail = lib.fm.cfg_upgr.create_task(self.fm, **self.p['upgr_cfg'])
            if not lib.fm.cfg_upgr.is_success_status(ts):
                self._fill_error_msg(
                    'Expect the task success but its status "%s". Detail: %s' %
                    (ts, pformat(detail))
                )
            else:
                logging.info('Created a cfg upgrade task "%s". \nStatus: %s. \nDetail:%s' %
                         (self.p['upgr_cfg']['task_name'], pformat(ts), pformat(detail)))
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())

    def _execute_restart_task_test(self):
        self._set_ap_mgmt_mode('snmp')
        if self.errmsg: return

        ts, detail = self._create_task()

        if self.errmsg: return
        elif not lib.fm.cfg_upgr.is_restartable_status(ts):
            self._fill_error_msg('Cannot do restart with this status: %s' % ts)
            return

        self._set_ap_mgmt_mode('auto')
        if self.errmsg: return

        self._restart_cfg_upgrade_task()
        if self.errmsg: return

        self._wait_for_ap_ready()

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
        # Remove unnecessary forr wlan 1 to 8
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
        logging.info('Verify AP web ui after provisioning cfg from FM')
        self._wait_for_ap_cpu_free()
        # TODO: currently, makefmtestbed only supports to add one ap for each test.
        # Hence, we need to consider supporting to verify more than one ap here
        fm_cfg, MAX_RETRIES = self.p['input_cfg'], 3
        fm_cfg = self._filter_unused_keys_on_ap(fm_cfg)
        radio_mode = {
            '2.4G': lib.ap.wlan.DUAL_BAND_RD_MODE_1,
            '5G': lib.ap.wlan.DUAL_BAND_RD_MODE_2,
        }[self.p['radio_mode'].upper()]

        self.ap.start(15)
        for k, fm_v in fm_cfg.iteritems():
            for i in try_times(MAX_RETRIES, 20):
                msg = None
                try:
                    if 'device_general' == k:
                        ap_v = lib.ap.dev.get(self.ap, fm_v.keys())
                    elif 'wlan_common' == k:
                        ap_v = lib.ap.wlan.getWLANCommon(
                            self.ap, fm_v.keys(), True, True, radio_mode
                        )
                    elif 'wlan' in k:
                        # for wlan 1 to 16
                        wlan_no = int(int(re.search('\d+', k).group(0)))
                        ap_v = lib.ap.wlan.getWLAN(
                            self.ap, wlan_no, fm_v.keys(), True, True, radio_mode
                        )
                    else:
                        raise Exception('Unsupport this key "%s"' % k)
                    logging.info('Verifying item: %s. \nInput cfg: %s. \nAP cfg: %s' %
                                 (k, pformat(fm_v), pformat(ap_v)))
                    msg = compare_dict(fm_v, ap_v, tied_compare=False)
                except Exception, e:
                    msg = e.__str__()
                    log_trace()
                if not msg:
                        break
                elif i < MAX_RETRIES:
                    logging.info('Found error: %s. Sleep a moment a try again...' %
                                 pformat(msg))
                else:
                    self._fill_error_msg(msg)

            if self.errmsg:
                break

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

    def _delete_test_cfg_tmpl(self):
        ''''''
        try:
            template_name = self.p['tmpl_cfg']['template_name']
            logging.info('Delete the test cfg template %s' % template_name)
            if not lib.fm.cfg_tmpl.delete_cfg_tmpl(self.fm, template_name):
                    logging.info('Warning: Cannot delete the template %s' % template_name)
        except Exception, e:
            log_trace()
            logging.info('Warning: Cannot delete the template %s. Error: %s' %
                         (template_name, e.__str__()))

