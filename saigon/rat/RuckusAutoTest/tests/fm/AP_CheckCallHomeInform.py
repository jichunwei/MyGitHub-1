'''
This test script is to verify following authentication types:
4.4.5    Device Periodically inform

Test Procedure:
1. Log in AP web UI by super account
2. Navigate to Management page
3. Set its inform interval to 1m/5ms or 15ms... then click Update Setting
4. Wait and check that after each interval AP send an inform to FM
5. Log out AP web UI

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

ERR_MSGS = [
    'Error: Waited for %s(s), the AP did not send any inform msg after set a new interval to %s.',
    'Error: Waited for %s(s), the AP sent the first inform but faild after set a new inform interval to %s.',
    'Error: Over interval %s, the AP did not call home. Last attempted contact: %s. Current time: %s.',
    'Error: Over interval %s, the AP cannot call home successfully. Last success: %s. Last attempted contact: %s. ',
]
PASSMSG = 'The AP always calls home with the interval %s'
# key to get returned value from get_tr069_status
TR069_STATUS_TITLE = [
    'lastattemptedcontact',
    'lastsuccessfulcontact',
    'currenttime',
]
class AP_CheckCallHomeInform(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = None
        self._cfg_test_params(**conf)

    def test(self):
        self._wait_for_ap_cpu_free()
        self.ap.start(15)
        self._cfg_inform_interval(self.p['inform_interval'])

        self._wait_for_the_first_inform()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_results()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        logging.info('Cleaning up the test...')
        self._cfg_inform_interval(self.p['default_interval'])
        self.ap.stop()
        self._clear_ap_cache()
        del self.ap
        del self.ap_cli
        self.fm.logout()

    def _cfg_test_params(self, **kwa):
        self.p = {
            'ap_ip': '',
            'inform_interval': '',
            'interval_in_sec': 60,
            'default_interval': '15ms',
            'times_to_check': 3,
        }
        self.p.update(kwa)

        init_coms(
            self,
            dict(tb=self.testbed, ap_ip=self.p['ap_ip'],
                 apcli_cfg=dict(ip_addr=self.p['ap_ip']),)
        )
        self.p['interval_in_sec'] = lib.ap.acc.interval_str_to_sec(self.p['inform_interval'])
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
            'threshold': 40, # default % CPU Usage
            'timeout': 20, # in minute
            'interval': 2,
            'times_to_check': 3,
        }

        monitor_cpu_cfg.update(dict(config={'ip_addr': self.p['ap_ip']}))
        msg = 'CPU of AP %s looks free for the test' % self.p['ap_ip']\
                if wait4_ap_stable(**monitor_cpu_cfg) else \
                ('WARNING: The CPU usage of AP %s is still too high' % self.p['ap_ip'])
        logging.info(msg)

    def _cfg_inform_interval(self, interval_str):
        logging.info('Set inform interval to %s' % interval_str)
        lib.ap.acc.set_inform_interval(self.ap, interval_str)

    def _wait_for_the_first_inform(self):
        '''
        After we re-set call home interval, ap may take a little time to stop and
        start tr069 service. This function is to wait for the first call home
        successfully.
        '''
        logging.info('Waiting for AP send the first inform...')
        self._wait_for_ap_cpu_free()

        status, msg, timeout = None, '', 60*5
        for i in try_interval(timeout=timeout, interval=20):
            try:
                status, msg = lib.ap.acc.get_tr069_inform_status(self.ap)
                if lib.ap.acc.TR069_STATUS_INFORM_SUCCESS == status:
                    logging.info('It called home the first time successfully. \nStatus: %s' %
                                 pformat(msg))
                    break
                else:
                    logging.info('Not send yet. Sleep to wait...')
            except Exception:
                # sometimes, error happens due to cannot extract time from tr069 status table
                print '----------Error: %s' % traceback.format_exc()
                time.sleep(10)

        self.errmsg = {
            lib.ap.acc.TR069_STATUS_INFORM_SUCCESS:  None,
            lib.ap.acc.TR069_STATUS_NO_INFORM:       ERR_MSGS[0] % (timeout, self.p['inform_interval']),
            lib.ap.acc.TR069_STATUS_INFORM_FAIL:     ERR_MSGS[1] % (timeout, self.p['inform_interval']),
        }[status]
        if self.errmsg:
            logging.info('Tr069 status msg: %s' % pformat(msg))
            logging.info(self.errmsg)

    def _test_results(self):
        '''
        Test to make sure tr069 authentication username/password from web ui and cli
        are consistent
        '''
        #self._wait_for_ap_cpu_free()
        lib_f = lib.ap.acc
        for i in try_times(self.p['times_to_check'], self.p['interval_in_sec']):
            logging.info('Checking ap call home in the interval %s...' % i)
            status, msg = None, ''
            for t in try_interval(timeout=self.p['interval_in_sec'], interval=10):
                try:
                    status, msg = lib_f.get_tr069_inform_status(self.ap)
                    if lib_f.TR069_STATUS_INFORM_SUCCESS == status:
                        logging.info('It successfully called home for interval %s. \nStatus: %s' %
                                     (i, pformat(msg)))
                        break
                    else:
                        logging.info('Not successful yet. Sleep to wait...')
                except Exception:
                    # sometimes, error happens due to cannot extract time from tr069 status table
                    log_trace()
                    time.sleep(10)
                    continue

            self.errmsg = {
                lib_f.TR069_STATUS_INFORM_SUCCESS:  None,
                lib_f.TR069_STATUS_NO_INFORM: (ERR_MSGS[2] % (self.p['inform_interval'],
                                               msg[TR069_STATUS_TITLE[0]], msg[TR069_STATUS_TITLE[2]])),
                lib_f.TR069_STATUS_INFORM_FAIL: (ERR_MSGS[3] % (self.p['inform_interval'],
                                                 msg[TR069_STATUS_TITLE[1]], msg[TR069_STATUS_TITLE[0]])),
            }[status]
            if self.errmsg:
                logging.info(self.errmsg)
                return

            if i == self.p['times_to_check']: break # break to avoid it sleeps the last time
            logging.info('Sleep %s(s) to wait for next inform' % self.p['interval_in_sec'])

        self.passmsg = PASSMSG % self.p['inform_interval']

    def _clear_ap_cache(self):
        '''
        This function is to reboot AP after re-set inform interval. Sometimes,
        we set inform interval several times, it causes the AP CPU very high
        and crashed. This function is to refresh AP and make sure it is in
        good status for next test case.
        '''
        ap_cfg = dict(config={'ip_addr': self.p['ap_ip']})
        reboot_ap({'ip_addr': self.p['ap_ip']})
        wait4_ap_up(**ap_cfg)
        self._wait_for_ap_cpu_free()
