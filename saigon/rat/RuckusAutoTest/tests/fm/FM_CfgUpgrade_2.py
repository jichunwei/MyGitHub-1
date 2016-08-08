'''
NOTES:
This script is created with intention to replace old test scripts of Configuration
Upgrade test cases FM_CfgUpgrade.py when having free time to do it.

Hence, this test script is currently support one below test case:
1.1.9.2.15    Configuration Upgrade: Failed task could be restart


Test Procedure:
    1. Log in FM as admin account
    2. Create a configuration template
    3. Log in AP web ui by super account
    4. Go to Management page, change remote management mode to "snmp" to
       make it no longer contact FM
    5. Go to Configure > Configuration Upgrade, create a config upgrade to
       provision the config template to that AP.
    6. Wait until the task show "expired" (around 20 mins),
    7. Back to AP Management page again, change remote mgmt mode to "Auto"
       or "Flexmaster"
    8. Back to FM > Configure > Configuration Upgrade page, click "Restart"
       to restart the expired task.
    7. Make sure the task is success and all configured items provisioned
       to that AP.

Pass/Fail/Error Criteria (including pass/fail messages):
+ Pass: if all of the verification steps in the test case are met.
+ Fail: if one of verification steps is failed.
+ Error: Other unexpected events happen.

Copy template.
Config:
    1. get cfg
Test
    1. Create template
    2. Do copy
    3. Check to make sure the copy has the same cfg
Clean up:
    Delete the created and the copied templates

Export template:
Config:
    1. get cfg
Test:
    1. create the template
    2. Do export
    3. Check to make sure the export has the same cfg
Clean up:
    1. Delete the created templates
    2. Delete the export file
'''

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.fm.lib_FM import *
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.fm.config_mapper_fm_old import *

class FM_CfgUpgrade_2(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = None
        self._cfg_test_params(**conf)
        #self._create_cfg_tmpl()

    def test(self):
        self._create_cfg_tmpl()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._execute_test()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_result()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        logging.info('Cleaning up the test...')
        self._cleanup_test()
        self.fm.logout()

    def _cfg_test_params(self, **kwa):
        self.p = dict(
            ap_ip = '',
            model = 'ZF2925',
            input_cfg = {},
            test_type = 'restart',
            test_name = 'Test restart config upgrade',
            schedule = 0, # O to perform now, > 0 to perform later,
            provision_to = dict(
                device = 'ap ip', # or group = 'Group name'
            ),
        )
        self.p.update(kwa)

        time_stamp = get_timestamp()
        # Add basic param to do test cfg upgrade for
        # Basic param 1: create a config param for cfg template
        self.p.update(
            tmpl_cfg = dict(
                template_name = 'cfg_tmpl_%s_%s' % (self.p['model'], time_stamp),
                template_model = self.p['model'].upper(),
                options = self.p['input_cfg'],
            )
        )
        self.p.update(
            restore_tmpl_cfg = dict(
                template_name = 'restore_cfg_tmpl_%s_%s' % (self.p['model'], time_stamp),
                template_model = self.p['model'].upper(),
                options = self.p['restore_cfg'],
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
        # Basic param 2: create a config param to create for cfg upgrade
        self.p.update(
            restore_upgr_cfg = dict(
                task_name = 'restore_cfg_upgrade_%s_%s' % (self.p['model'], time_stamp),
                template_name = self.p['restore_tmpl_cfg']['template_name'],
                template_model = self.p['restore_tmpl_cfg']['template_model'],
                provision_to = self.p['provision_to'],
                schedule = self.p['schedule'],
            )
        )
        # Add more params for each test if needed
        cfg_fn = {
            'restart': None,
            'create': None,
        }[self.p['test_type'].lower()]

        if cfg_fn: cfg_fn()
        init_coms(self, dict(tb=self.testbed, ap_ip=self.p['ap_ip']))
        logging.info('Test configs:\n%s' % pformat(self.p))

    def _cfg_test_params_for_restart_task(self):
        '''This  function is to add params to do copy cfg template'''
        pass

    def _create_cfg_tmpl(self):
        try:
            lib.fm.cfg_tmpl.create_cfg_tmpl_2(
                self.fm, self.p['tmpl_cfg']['template_name'],
                self.p['tmpl_cfg']['template_model'], self.p['tmpl_cfg']['options']
            )
            logging.info('Created a template "%s" successfully' % self.p['tmpl_cfg']['template_name'])

            lib.fm.cfg_tmpl.create_cfg_tmpl_2(
                self.fm, self.p['tmpl_cfg']['template_name'],
                self.p['tmpl_cfg']['template_model'], self.p['tmpl_cfg']['options']
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

    def _create_task(self):
        try:
            ts, detail = lib.fm.cfg_upgr.create_task(self.fm, **self.p['upgr_cfg'])
            logging.info('Created a cfg upgrade task "%s". \nStatus: %s. \nDetail:%s' %
                         (self.p['upgr_cfg']['task_name'], pformat(ts), pformat(detail)))
            return ts, detail
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())

    def _restart_cfg_upgrade_task(self):
        ''''''
        MAX_RETRIES = 3
        for i in try_times(MAX_RETRIES, 5):
            try:
                ts, detail = lib.fm.cfg_upgr.restart_task(
                    self.fm,
                    dict(task_name=self.p['upgr_cfg']['task_name'])
                )
                if lib.fm.cfg_upgr.is_success_status(ts):
                    logging.info('The task %s is restarted succesfully' %
                                 self.p['upgr_cfg']['task_name'])
                    break
                else:
                    self._fill_error_msg('Expect success but its status: %s' % ts)
                logging.info('Task status: %s. Detail: %s' % (ts, detail))
            except Exception, e:
                log_trace()
                if i >= MAX_RETRIES:
                    self._fill_error_msg(e.__str__())
                    raise
                else:
                    logging.info('Found error: %s. Try again...' % e.__str__())

    def _execute_test(self):
        ''''''
        cfg_test_fn = {
            'restart': self._execute_restart_task_test,
            'create': self._execute_create_task_test,
        }[self.p['test_type'].lower()]

        cfg_test_fn()

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

    def _execute_create_task_test(self):
        ts, detail = self._create_task()
        if self.errmsg: return
        elif not lib.fm.cfg_upgr.is_success_status(ts):
            self._fill_error_msg('Expect the task success but its status: %s' % ts)
            return

        self._wait_for_ap_ready()


    def _test_result(self):
        '''
        Test to make sure tr069 authentication username/password from web ui and cli
        are consistent
        '''
        logging.info('Checking the result for the test "%s" configuration template' %
                     self.p['test_type'].lower())

        test_result_fn = {
            'restart': self._verify_ap_webui,
            'create': self._verify_ap_webui,
        }[self.p['test_type'].lower()]

        if test_result_fn: test_result_fn()

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

        # Remove unnecessary for wlan 1 to 8
        for i in range(1,9):
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
        #pprint (fm_cfg)
        #for ap in tested_aps:
        #    logging.info('Testing for AP with config: %s' % ap.config)

        self.ap.start(15)
        #tmp = ap._tmp_[self.timestamp]
        for k, fm_v in fm_cfg.iteritems():
            for i in try_times(MAX_RETRIES, 20):
                msg = None
                try:
                    if 'device_general' == k:
                        ap_v = lib.ap.dev.get(self.ap, fm_v.keys())
                    elif 'wlan_common' == k:
                        ap_v = lib.ap.wlan.getWLANCommon(self.ap, fm_v.keys(), True, True)
                    elif 'wlan' in k:
                        # for wlan 1 to 8
                        wlan_no = int(int(re.search('\d+', k).group(0)))
                        ap_v = lib.ap.wlan.getWLAN(self.ap, wlan_no, fm_v.keys(), True, True)
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

    def _cleanup_test(self):
        cleanup_fn = {
            'restart': self._cleanup_restart_upgrade_cfg,
            'create': self._cleanup_create_upgrade_cfg,
        }[self.p['test_type'].lower()]

        cleanup_fn()


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

            template_name = self.p['restore_tmpl_cfg']['template_name']
            logging.info('Delete the restore cfg template %s' % template_name)
            if not lib.fm.cfg_tmpl.delete_cfg_tmpl(self.fm, template_name):
                    logging.info('Warning: Cannot delete the template %s' % template_name)
        except Exception, e:
            log_trace()
            logging.info('Warning: Cannot delete the template %s. Error: %s' %
                         (template_name, e.__str__()))


    def _restore_default_ap_config(self):
        '''
        Restore default config for tested aps
        '''
        try:
            logging.info('Restore default config...')
            ts, detail = lib.fm.cfg_upgr.create_task(
                                self.fm, **self.p['restore_upgr_cfg']
                         )
            logging.info(
                'Created a restore cfg upgrade task "%s". \nStatus: %s. \nDetail:%s' %
                (self.p['restore_upgr_cfg']['task_name'], pformat(ts), pformat(detail))
            )

            if not a.fm.lib.cfg_upgr.is_success_status(ts):
                logging.info(
                    'Warning: Cannot restore default config. Status: %s. Detail: %s' %
                    (ts, detail)
                )
        except Exception, e:
            logging.info('Warning: Exception while restore. Error: %s' % e.__str__())


    def _cleanup_restart_upgrade_cfg(self):
        self._restore_default_ap_config()
        self._delete_test_cfg_tmpl()
        self._set_fm_url()

    def _cleanup_create_upgrade_cfg(self):
        self._restore_default_ap_config()
        self._delete_test_cfg_tmpl()
        self._set_fm_url()
