'''
NOTES:
This script is created with intention to replace old test scripts of Auto
Configuration Upgrade test cases FM_AutoCfgUpgrade.py when having free time to do it.

Hence, this test script is currently support one below test case:
1.2.3.13    Auto configuration test for ZF7962 by AP8.1
'''

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.fm.lib_FM import *
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.fm.config_mapper_fm_old import *

class FM_AutoCfgTest_2(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = None
        self._cfg_test_params(**conf)

    def test(self):
        self._create_cfg_tmpl()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._create_auto_cfg_rule()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._change_ap_serial()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._set_ap_fm_url()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._is_device_marked_auto_config()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._is_device_auto_configured_by_rule()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._verify_ap_webui()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        logging.info('Cleaning up the test...')
        self._stop_auto_cfg_rule()
        self._disable_auto_configured_device()
        self._restore_ap_serial()
        self._reset_ap_factory()
        self._set_ap_fm_url()
        self.fm.logout()

    def _cfg_test_params(self, **kwa):
        self.p = dict(
            ap_ip = '',
            radio_mode = '2.4G',
            model = 'ZF7962',
            input_cfg = {},
            #test_type = 'restart',
            test_name = 'Test auto config upgrade',
            device_group = 'All Standalone APs',
        )
        self.p.update(kwa)

        time_stamp = get_timestamp()
        # Add basic param to do test cfg upgrade for
        # Basic param 1: create a config param for cfg template
        # Add basic param to do test cfg upgrade for
        # Basic param 1: create a config param for cfg template
        self.p.update(
            tmpl_cfg = dict(
                template_name = 'auto_cfg_tmpl_%s_%s' % (self.p['model'], time_stamp),
                template_model = self.p['model'].upper(),
                options = self.p['input_cfg'],
            )
        )
        # cfg for the rule
        self.p.update(
            rule_cfg = dict(
                cfg_rule_name = 'auto_cfg_%s_%s' % (self.p['model'], time_stamp),
                device_group = self.p['device_group'],
                model = self.p['model'].upper(),
                cfg_template_name = self.p['tmpl_cfg']['template_name'],
                create_time = '', # will be updated in _create_auto_cfg_rule
            )
        )
        init_coms(self, dict(tb=self.testbed, ap_ip=self.p['ap_ip']))
        # generate one new serial
        self.p['new_serial'] = self.fm.generate_unique_ap_serials(**{'no': 1, 'prefix': 'ZF'})[0]
        self.p['ori_serial'] = get_ap_serial(**{'config':{'ip_addr': self.p['ap_ip']}})

        logging.info('Test configs:\n%s' % pformat(self.p))

    def _create_cfg_tmpl(self):
        try:
            lib.fm.cfg_tmpl.create_cfg_tmpl_2(
                self.fm, self.p['tmpl_cfg']['template_name'],
                self.p['tmpl_cfg']['template_model'], self.p['tmpl_cfg']['options']
            )
            logging.info('Created a template "%s" successfully' % self.p['tmpl_cfg']['template_name'])
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())

    def _create_auto_cfg_rule(self):
        '''
        Create an auto configuration rule for this group
        '''
        # logging.info('Create an Auto Config Rule for model %s' % self.p['model'])
        delta = 0
        try:
            r_cfg = self.p['rule_cfg']
            self.p['rule_cfg']['create_time'] = lib.fm.auto_cfg.create_auto_cfg_rule(
                self.fm, r_cfg['cfg_rule_name'], r_cfg['device_group'],
                r_cfg['model'], r_cfg['cfg_template_name'], advance_return=True
            )
            logging.info('Created an auto config rule "%s" for the test' % r_cfg['cfg_rule_name'])
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())

    def _change_ap_serial(self):
        ''''''
        config= {
            'ip_addr': self.ap.get_cfg()['ip_addr']
        }
        logging.info('Change serial of AP %s to %s' % (config['ip_addr'], self.p['new_serial']))
        if not set_ap_serial(**{'serial': self.p['new_serial'], 'config': config}):
            self._fill_error_msg(
                'Cannot set a new serial %s for AP %s' %
                (self.p['new_serial'], config['ip_addr'])
            )
            return

        # just reboot to make new serial take effect to save time, don't need to set factory
        #logging.info('Reboot the AP %s to make new serial take effect' % ap['ip_addr'])
        if not reboot_ap(config):
            self._fill_error_msg(
                'Cannot reboot AP %s after change its serial' % (config['ip_addr'])
            )
            return

        if not wait4_ap_up(**{'config':config}):
            self._fill_error_msg(
                 'The AP %s is not boot up...' % (config['ip_addr'])
            )
            return

    def _set_ap_fm_url(self):
        '''
        This function is to set FM server url for each AP
        '''
        fm_url = 'https://%s/intune/server' % self.fm.get_cfg()['ip_addr']
        self._wait_for_ap_cpu_free()
        try:
            self.ap.start(15)
            #self.ap.set_fm_url(url=fm_url, validate_url=False)
            lib.ap.acc.set(
                    self.ap,
                    cfg=dict(remote_mode='auto', fm_url=fm_url, inform_interval='5ms')
                )
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())

        self.ap.stop()

    def _is_device_marked_auto_config(self):
        '''
        This function is to test whether FM marks a device as "Auto Configured" with "check" symbol
        '''
        logging.info('Test to make sure tested devices marked as Auto Configured')
        try:
            lib.fm.auto_cfg.is_device_marked_auto_config(self.fm, self.p['new_serial'])
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())

    def _is_device_auto_configured_by_rule(self):
        '''
        This function is to test whether FM marks a device as "Auto Configured" with "check" symbol
        '''
        logging.info('Test to make sure tested devices are auto configured by the expected rule')
        try:
            if not lib.fm.auto_cfg.is_device_auto_configured_by_rule(
                self.fm, self.p['new_serial'],
                self.p['rule_cfg']['cfg_rule_name'], self.p['rule_cfg']['create_time']
            ):
                self._fill_error_msg(
                    'ERROR: The device with serial %s is not auto configured by the rule %s' %
                    (self.p['new_serial'], self.p['rule_cfg']['cfg_rule_name'])
                )
            else:
                logging.info('CORRECT! The device with serial %s is auto configured by the first rule %s' %\
                                 (self.p['new_serial'], self.p['rule_cfg']['cfg_rule_name']))
        except Exception, e:
            self._fill_error_msg(e.__str__())

    def _stop_auto_cfg_rule(self):
        '''
        To delete/stop an auto cfg rule
        '''
        try:
            r_cfg = self.p['rule_cfg']
            logging.info('Trying to delete the rule %s' % r_cfg['cfg_rule_name'])
            lib.fm.auto_cfg.delete_auto_cfg_rule(
                self.fm, r_cfg['cfg_rule_name'], r_cfg['create_time']
            )
        except Exception, e:
            logging.info(
                'Warning: Cannot delete the rule %s. Error: %s. Try to stop it.' %
                (r_cfg['cfg_rule_name'], e.__str__())
            )
            try:
                lib.fm.auto_cfg.stop_auto_cfg_rule(
                    self.fm, r_cfg['cfg_rule_name'], r_cfg['create_time']
                )
            except Exception, e:
                logging.info(
                    'Warning: Cannot stop the rule %s. Error: %s' %
                    (r_cfg['cfg_rule_name'], e.__str__())
                )


    def _disable_auto_configured_device(self):
        '''
        After finish the test we need to disable tested APs with new serial
        so that they are not shown on Inventory > Manage Device
        '''
        try:
            # FM 9 allows removing the device in registration list so remove it.
            if lib.fm.dreg.remove_device(self.fm, self.p['new_serial']):
                logging.info(
                    'Removed the new device %s from registration list' %
                    self.p['new_serial']
                )
        except Exception, e:
            logging.debug(
                'Warning: Cannot remove the device %s. Disable it...' % self.p['new_serial']
            )
            lib.fm.dreg.set_device_status(
                self.fm, self.p['new_serial'], "Unavailable", 'Automation changed to Unavailable'
            )

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

        # NOTE: currently we will not change username/password of the test. To avoid
        # the test failed, it will affect other tcs so we don't need to check changed
        # username/password here.

        # change_username, change_password = None, None
        # If user changed user and password, need to assign new username and password to AP
        # if self.p['input_cfg'].has_key('device_general'):
        #    #if self.provisioned_cfg_options['device_general'].has_key('username'):
        #    change_username = self.p['input_cfg']['device_general'].get('username', None)
        #    change_password = self.p['input_cfg']['device_general'].get('password', None)

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

    def _set_ap_mgmt_mode(self, mode):
        ''''''
        try:
            logging.info('Set management type of ap %s to %s' % (self.p['ap_ip'], mode))
            self._wait_for_ap_cpu_free()
            self.ap.start(15)
            lib.ap.acc.set(self.ap, cfg=dict(remote_mode=mode))
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())
        # Sleep a moment before stop ap to make sure the changes are submitted completely
        time.sleep(2.5)
        self.ap.stop()
        self._wait_for_ap_cpu_free()

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
        MAX_WLAN = 16
        # Remove unnecessary for wlan 1 to 8
        for i in range(1,MAX_WLAN+1):
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

    def _verify_ap_webui(self):
        ''''''
        logging.info('Verify AP web ui after provision cfg from FM')
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
        #tmp = ap._tmp_[self.timestamp]
        for k, v in fm_cfg.iteritems():
            print 'v: %s' % v
            for i in try_times(MAX_RETRIES, 20):
                msg, fm_v = None, copy.deepcopy(v)
                try:
                    if 'device_general' == k:
                        ap_v = lib.ap.dev.get(self.ap, fm_v.keys())
                    elif 'wlan_common' == k:
                        # ap_v = lib.ap.wlan.getWLANCommon(self.ap, fm_v.keys(), True, True)
                        ap_v = lib.ap.wlan.get_wlan_common(
                            self.ap, fm_v.keys(), True, True, radio_mode
                        )
                    elif 'wlan' in k:
                        # for wlan 1 to 8
                        print fm_v
                        wlan_no = int(int(re.search('\d+', k).group(0)))
                        #ap_v = lib.ap.wlan.getWLAN(self.ap, wlan_no, fm_v.keys(), True, True)
                        ap_v = lib.ap.wlan.get_wlan_detail(
                            self.ap, wlan_no, fm_v.keys(), True, True, radio_mode
                        )
                    else:
                        raise Exception('Unsupport this key "%s"' % k)
                    logging.info('Verifying option: %s. \nInput cfg: %s. \nAP cfg: %s' %
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
            logging.info('All APs are upgraded successully')
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
            self.ap.start(15)
            fm_url = 'http://%s/intune/server' % self.fm.get_cfg()['ip_addr']
            logging.info('Set fm url %s for the test ap' % fm_url)
            self._wait_for_ap_cpu_free()
            self.ap.start(15)
            lib.ap.acc.set(self.ap, dict(fm_url=fm_url))
            self.ap.stop()
        except Exception, e:
            log_trace()
            logging.info('Warning: Unexpected error happens: %s' % e.__str__())

    def _restore_ap_serial(self):
        '''
        Restore ogriginal serials for all APs
        '''
        logging.info(
            'Restoring original serial %s for AP %s' %
            (self.p['ori_serial'], self.p['ap_ip'])
        )
        config= {
            'ip_addr': self.p['ap_ip']
        }

        if not set_ap_serial(**{'serial': self.p['ori_serial'], 'config': config}):
            logging.info(
                'Warning: Cannot restore the original serial %s for AP %s' %
                (self.p['ori_serial'], self.p['ap_ip'])
            )
            return
