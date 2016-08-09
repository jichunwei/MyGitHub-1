'''
This test script is to verify following authentication types:
3    Device View status in FM
3.1    Detail of ZF2925 8.0
3.1.3    4/8/16 SSIDs summary displays in Summary page of FM Device View.


Test Procedure: (update later)
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
import copy
from pprint import pformat

from RuckusAutoTest.models import Test

from RuckusAutoTest.common.utils import get_timestamp, compare_dict
from RuckusAutoTest.tests.fm.lib_FM import init_aliases, \
        get_ap_default_cli_cfg, wait4_ap_up, \
        wait4_ap_stable, set_ap_factory
from RuckusAutoTest.components import Helpers as lib


class FMDV_SsidSummary(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = None
        self._cfgTestParams(**conf)

        self._wait4_ap_stable()
        #remove set AP call  home interval time

        # after provisioning successfully, get dv object for the test
        self.dv = self.aliases.fm.get_device_view(ip=self.ap.get_cfg()['ip_addr'])


    def test(self):
        self._cfg_wlan()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._waitForAPReadyToTest()

        self._testConsistentUIDisplay()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', 'Device View Summary and AP display are the same')


    def cleanup(self):
        self._restore_wlan_cfg()
        if self.dv: self.aliases.fm.cleanup_device_view(self.dv)
        self.aliases.fm.logout()


    def _cfgTestParams(self, **kwa):
        self.p = {
            'model': 'ZF2925',
            'cfg': {},
            'ap_ip': '',
            'test_name': 'SSID Summary in Summary page',
        }
        self.p.update(kwa)

        self.aliases = init_aliases(testbed=self.testbed)

        self.p['taskname'] = '%s_%s' % (self.p['model'], get_timestamp())
        self.p['template']= 'CfgUpgrade_' + self.p['taskname']
        self.timeout = 20 #minutes
        self.dv, self.ap = None, None
        self.ap = self.aliases.tb.getApByIp(self.p['ap_ip'])

        logging.info('Test configs:\n%s' % pformat(self.p))


    def _cfg_wlan(self):
        for k, wlan_cfg in self.p['cfg'].items():
            ret, msg = lib.fmdv.wlan.set_wlan_detail(self.dv, wlan_cfg)
            logging.info(msg)
            if ret != self.dv.TASK_STATUS_SUCCESS:
                self.errmsg = msg
                break


    def _setAPCallHomeInterval(self):
        self.ap.start(15)
        try:
            callhome_int = self.ap.set_call_home_interval(
                                interval=self.ap.CallHomeIntervalMin
                           )
            logging.debug(
                'AP: %s, callhome_interval: %s'  % (self.ap.ip_addr, callhome_int)
            )
        except Exception, e:
            logging.info(
                'Warning: Fail to set call home interval to %s minute. Error %s' %
                (self.ap.CallHomeIntervalMin, e.__str__())
            )
        self.ap.stop()


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
            time.sleep(30)

            # Next, wait for the test AP boot up
            config = get_ap_default_cli_cfg()
            config.update(self.ap.get_cfg())
            if not wait4_ap_up(**{'config': config, 'timeout': 6}):
                self.errmsg += 'Cannot login to AP via cli %s after 6 mins waiting' \
                                % (config['ip_addr'])
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


    def _testConsistentUIDisplay(self):
        '''
        '''
        #self._wait4_ap_stable()
        self.ap.start(10)
        timeout = 17 # minutes. Use a value greater than default interval 15
        end_time = time.time() + timeout*60

        for k in self.p['cfg'].iterkeys():
            is_different, retries = True, 1
            while is_different and time.time() < end_time:
                try:
                    if 'wlan_common' == k:
                        dv_display = lib.fmdv.summary.getWLANCommon(self.dv)
                        ap_display = lib.ap.wlan.getWLANCommon(self.ap, dv_display.keys(), fm_return=True)
                    else:
                        # get wlan detail
                        wlan_no = int(self.p['cfg'][k]['wlan_num'])
                        dv_display = lib.fmdv.summary.getWLAN(self.dv, wlan_no)
                        apKs = lib.ap.wlan.convert_key_input_wlan_det_cfg_fm_ap(dv_display.keys(), to_ap=True)
                        ap_display = lib.ap.wlan.getWLAN(self.ap, wlan_no, apKs, fm_return=True)

                    logging.info('Key: %s.\nSSID cfg: %s.\nAP cfg: %s' % (k, pformat(dv_display), pformat(ap_display)))
                    ret_msg = compare_dict(dv_display, ap_display)
                    # two dictionaries are different
                    if ret_msg:
                        logging.info('%s. Retry %s time(s)...' % (ret_msg, retries))
                        retries +=1
                        # sleep a moment to wait
                        time.sleep(30)
                        continue

                    is_different = False
                except Exception, e:
                    logging.info('A strange error happened: %s. Ignore it and retry again!!!' % e.__str__())
            if is_different:
                self.errmsg = 'Error: Device Summary SSID and AP display are still '\
                              'different after %s minutes trying' % timeout
                logging.info(self.errmsg)
                break

        self.ap.stop()


    def _setAPFactory(self):
        ap_cli_config = get_ap_default_cli_cfg()
        ap_cli_config.update(self.ap.get_cfg())
        logging.info('Setting factory to restore default config for AP %s' % (ap_cli_config['ip_addr']))

        if not set_ap_factory(config=ap_cli_config):
            logging.info('Warning: Cannot set default factory for AP %s' % (ap_cli_config['ip_addr']))
            return

        # Wait for ap resource stable for next test
        # after setfactory default, it has defaul username, password. No need to provide them
        self._wait4_ap_stable()
        logging.info('Restored default config for all APs')


    def _restore_wlan_cfg(self):
        for k, wlan_cfg in self.p['cfg'].items():
            try:
                logging.info('Restore default config for %s' % k)
                default_cfg = copy.deepcopy(wlan_cfg)
                default_cfg.update(dict(
                    wlan_name         = 'Wireless %s' % wlan_cfg['wlan_num'],
                    wlan_ssid         = 'Wireless %s' % wlan_cfg['wlan_num'],
                    avail             = 'disabled',
                    encrypt_method = 'disabled'
                ))
                lib.fmdv.wlan.set_wlan_detail(self.dv, default_cfg)
            except Exception, e:
                logging.info('Warning: Cannot restore default config for this wlan. '
                             'Error: %s' % e.__str__())
