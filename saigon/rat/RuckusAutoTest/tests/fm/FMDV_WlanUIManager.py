'''
This test script is to verify following authentication types:
3.1.8    Modify the wireless common parameters in Device View of FM
3.1.9    Modify the wireless parameters in Device View of FM

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
import time
import logging
import re
import copy
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.utils import compare_dict
from RuckusAutoTest.tests.fm.lib_FM import init_aliases, get_ap_default_cli_cfg, \
        wait4_ap_up, set_ap_factory, wait4_ap_stable
from RuckusAutoTest.components import Helpers as lib


class FMDV_WlanUIManager(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = None
        self._cfgTestParams(**conf)


    def test(self):
        self._cfgWlan()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testConsistentUI()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)


    def cleanup(self):
        self._restore_wlan_cfg()
        self.aliases.fm.cleanup_device_view(self.dv)
        self.aliases.fm.logout()


    def _cfgTestParams(self, **kwa):
        self.p = {
            'ap_ip':     '192.168.0.222',
            'cfg':  {},
            # NOTE: For test UI of Wireless Common only, if cannot configure with main cfg
            # "cfg" due to current cfg of dv is the same with the main cfg, it will test
            # with the backup_cfg
            'backup_cfg': {},
        }
        self.p.update(kwa)

        self.aliases = init_aliases(testbed=self.testbed)
        self.ap = self.aliases.tb.getApByIp(self.p['ap_ip'])
        self.dv = self.aliases.fm.get_device_view(ip=self.p['ap_ip'])

        # remove items, which are not available on AP web ui, in the test cfg
        ap_unsupported_items = ['client_isolation']
        for k in ap_unsupported_items:
            if k in self.p['cfg']: del self.p['cfg'][k]

        logging.info('Test configs:\n%s' % pformat(self.p))


    def _cfgWlan(self):
        for k, cfg in self.p['cfg'].iteritems():
            status, msg = None, None
            try:
                cfgFn = lib.fmdv.wlan.set_wlan_common \
                        if 'wlan_common' == k else \
                        lib.fmdv.wlan.set_wlan_detail
                status, msg = cfgFn(self.dv, cfg)
            except Exception, e:
                # If task not found
                if re.search('not found.*Task.*"', str(e), re.I):
                    # NOTE: when generate cfg for wireless common we may encounter a problem
                    # the cfg is the same with the current one on web UI. In this case, we cannot
                    # submit the change and we have to use a backup cfg to test
                    if 'wlan_common' == k:
                        logging.info('Use back up config to verify')
                        cfg = self.p['backup_cfg']['wlan_common']
                        self.p['cfg'][k] = cfg
                        status, msg = cfgFn(self.dv, cfg)
                    else:
                        self.errmsg = e.__str__()
                        logging.info(self.errmsg)
                        break
                else:
                    raise #Exception(str(e))

            if status != self.dv.TASK_STATUS_SUCCESS:
                    self.errmsg = msg
                    logging.info(msg)
                    break


    def _testConsistentUI(self):
        '''
        This function is to make sure Device View and AP web UI show
        the input cfg exactly
        '''
        logging.info('Test conistent FM Device View and AP Web UI')
        self._waitForAPReadyToTest()

        test_cfg = copy.deepcopy(self.p['cfg'])
        self.ap.start(15)
        timeout = 17 # minutes. Use a value greater than default interval 15
        end_time = time.time() + timeout*60

        for k, det in test_cfg.iteritems():
            is_different, retries = True, 1
            while is_different and time.time() < end_time:
                try:
                    # Get cfg from Device View in simple input values
                    if 'wlan_common' == k:
                        dv_ui_cfg = lib.fmdv.wlan.getWLANCommon(self.dv, det.keys())
                        ap_ks = lib.ap.wlan.convert_key_input_wlan_common_cfg_fm_ap(det.keys(), to_ap=True)
                        ap_ui_cfg = lib.ap.wlan.getWLANCommon(self.ap, ap_ks, fm_return=True)
                    else:
                        # only get the first time. If the error happens, it will not re-get
                        if retries <= 1:
                            wlan = int(det.pop('wlan_num'))
                        ap_ks = lib.ap.wlan.convert_key_input_wlan_det_cfg_fm_ap(det.keys(), to_ap=True)

                        dv_ui_cfg = lib.fmdv.wlan.getWLAN(self.dv, wlan, det.keys())
                        ap_ui_cfg = lib.ap.wlan.getWLAN(self.ap, wlan, ap_ks, fm_return=True)

                    logging.info('Got configs from Device View:\n%s' % pformat(dv_ui_cfg))
                    logging.info('Got configs from AP web UI:\n%s' % pformat(ap_ui_cfg))

                    # compare returned values from Device View with first
                    ret_msg_1 = compare_dict(dv_ui_cfg, det, tied_compare=False)

                    # Remove client_isolation key before compare returned values got from dv and ap.
                    # This key is not available on ap web ui
                    remove_keys = ['client_isolation']
                    for item in remove_keys:
                        if dv_ui_cfg.has_key(item): del dv_ui_cfg[item]
                    # Come here, two dv_ui_cfg and ap_ui_cfg will have the same keys
                    ret_msg_2 = compare_dict(dv_ui_cfg, ap_ui_cfg, tied_compare=False)

                    if ret_msg_1 or ret_msg_1:
                        logging.info('%s. Retry %s times...' % (ret_msg_1 if ret_msg_1 else ret_msg_2, retries))
                        retries +=1
                        # sleep a moment to wait
                        time.sleep(30)
                        continue

                    is_different = False
                    logging.info('Items of %s are consistent...' % k)
                except Exception, e:
                    retries +=1
                    logging.info('A strange error happened: %s. Ignore it and retry %s times!!!' % (e.__str__(), retries))
                    # sleep a moment to wait
                    time.sleep(30)
                    continue
            if is_different:
                self.errmsg = ('Error. Key: %s of Device View and AP display are still '
                              'different after %s minutes trying' % (k, timeout))
                break

        self.ap.stop()
        if self.errmsg:
            logging.info(self.errmsg)
        else:
            self.passmsg = 'Device View and AP Web UI is consistent'
            logging.info(self.passmsg)


    def _restore_wlan_cfg(self):
        for k, wlan_cfg in self.p['cfg'].items():
            try:
                # No need to restore for wlan common
                if 'wlan_common' in wlan_cfg:
                    logging.info('No need to restore for wlan common')
                    continue
                logging.info('Restore default config for %s' % k)
                default_cfg = copy.deepcopy(wlan_cfg)
                default_cfg.update(dict(
                    wlan_name         = 'Wireless %s' % wlan_cfg['wlan_num'],
                    wlan_ssid         = 'Wireless %s' % wlan_cfg['wlan_num'],
                    avail             = 'disabled',
                    encrypt_method = 'disabled'
                ))
                lib.fmdv.wlan.set_wlan_detail(self.dv, default_cfg)

                self._wait4_ap_stable()
            except Exception, e:
                logging.info('Warning: Cannot restore default config for this wlan. '
                             'Error: %s' % e.__str__())


    def _waitForAPReadyToTest(self):
        a = self.aliases
        time_to_sleep = 10
        k = 'wlan_common' #a.cfm['PRO_WLAN_COMMON_TITLE']
        item1 = 'wmode'
        item2 = 'country_code'

        logging.info('Wait for AP ready to test')

        if self.p['cfg'].has_key(k) and \
           (self.p['cfg'][k].has_key(item1) or\
           self.p['cfg'][k].has_key(item2)):
            # sleep to wait for the first AP enter into reboot progress.
            logging.info('Sleeping a moment to wait for AP to enter reboot status')
            time.sleep(20)

            # Next, wait for the test AP boot up
            ap_cli_cfg = get_ap_default_cli_cfg()
            ap_cli_cfg.update(self.ap.get_cfg())
            if not wait4_ap_up(**{'config': ap_cli_cfg, 'timeout': 6}):
                self.errmsg += 'Cannot login to AP via cli %s after 6 mins waiting' \
                                % (ap_cli_cfg['ip_addr'])
                return

        self._wait4_ap_stable()


    def _wait4_ap_stable(self):
        '''
        This function is to check CPU usage of AP and wait for each ready to test.
        Note: if provide username password, this function will use that username/password
        instead of username/password from ap instance to connect to AP and monitor its CPU usage.
        '''
        # monitor AP CPU usage to wait for its load < 40% after rebooting or provisioning
        MONITOR_CPU_USAGE = 0
        ap_cli_config = get_ap_default_cli_cfg()
        ap_cli_config.update(self.ap.get_cfg())

        monitor_cpu_cfg= {
            #'config': config,
            'monitor': MONITOR_CPU_USAGE,
            'threshold': 40, # default % CPU Usage
            'timeout': 20, # in minute
            'interval': 2,
            'times_to_check': 3,
        }

        monitor_cpu_cfg.update({'config': ap_cli_config})
        msg = 'The CPU of AP %s looks free for the test' % ap_cli_config['ip_addr']\
                if wait4_ap_stable(**monitor_cpu_cfg) else \
                ('WARNING: The CPU usage of AP %s is still too high' % ap_cli_config['ip_addr'])
        logging.info(msg)
