'''
This test script is to verify following authentication types:
4.4.2    TR069 in AUTO mode after factory default


Test Procedure:
This test case is to make sure that the remote mgmt mode of AP is in "auto" mode
after set factory default

1. Log in AP webui/cli by super account
2. Go to Maintenance > Reboot/Reset page, click "Reset now" to set factory it if
   log in via web ui. Or, execute "set factory" then "reboot" to set factory AP
   if in cli mode.
3. Wait for the AP boot up, navigate to Administration > Management page.
4. Make sure that the TR069 is in "auto" mode
5. Log out the AP

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

MSGS = [
    'Error: Expect tr069 mode: %s. Current tr069 mode: %s',
]
class AP_Tr069ModeAfterFactory(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = None
        self._cfg_test_params(**conf)

        #clear persistent data to avoid a case that tr069 mode is set in
        # persistent data
        self.ap_cli.clear_persistent_cfg()
        set_ap_factory(**dict(config={'ip_addr': self.p['ap_ip']}))

    def test(self):
        self.ap.start(15)
        self._get_results()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_results()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        logging.info('Cleaning up the test...')

        self._set_ap_fm_url()
        self.ap.stop()
        del self.ap
        del self.ap_cli
        self.fm.logout()

    def _cfg_test_params(self, **kwa):
        self.p = {
            'model': 'zf2925',
            'ap_ip': '',
            'test_name': 'Tr069 mode is in "auto" mode after factory default',
            'exp_mgmt_cfg': dict(remote_mode='auto'),
            'display_mgmt_cfg': {}, # key to get displayed cfg after do cfg it
        }
        self.p.update(kwa)
        init_coms(
            self,
            dict(tb=self.testbed, ap_ip=self.p['ap_ip'],
                 apcli_cfg=dict(ip_addr=self.p['ap_ip']),)
        )
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

    def _get_results(self):
        '''
        Get tr069 mode from AP webui
        '''
        logging.info('Getting tr069 mode...')
        self._wait_for_ap_cpu_free()
        self.p['display_mgmt_cfg'] = lib.ap.acc.get(self.ap, self.p['exp_mgmt_cfg'].keys())
        logging.info('Got tr069 cfg: %s' % self.p['display_mgmt_cfg'])

    def _test_results(self):
        '''
        Test to make sure tr069 mode in "auto" mode after factory default
        '''
        retries = 5
        for t in try_times(retries):
            if self.p['display_mgmt_cfg'] == self.p['exp_mgmt_cfg']:
                self.passmsg = self.p['test_name']
            else:
                self.errmsg = MSGS[0] % (self.p['exp_mgmt_cfg'], self.p['display_mgmt_cfg'])
            # sometimes it cannot get the remote mgmt so we need retry it several times.
            if self.errmsg is None:
                break
            elif t < retries:
                logging.info('Warning!! Cannot get remote mgmt mode. Retry %s times' % t)
                self.errmsg = None
                self._get_results()

    def _set_ap_fm_url(self):
        '''
        '''
        fm_url = 'https://%s/intune/server' % self.fm.get_cfg()['ip_addr']
        try:
            #self.ap.start(tries=15)
            #callhome_interval = ap['ap_webui'].set_call_home_interval(interval=ap['ap_webui'].CallHomeIntervalMin)
            self.ap.set_fm_url(url=fm_url, validate_url=False)
            logging.info('AP: %s, FM server url: %s'  % \
                          (self.ap.get_cfg()['ip_addr'], fm_url)) #, callhome_interval: %s, callhome_interval))
        except Exception, e:
            logging.info('Warning: there is an error while trying set fm url. Error: %s' % e.__str__())


