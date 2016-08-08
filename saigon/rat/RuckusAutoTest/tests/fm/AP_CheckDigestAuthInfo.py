'''
This test script is to verify following authentication types:
4.4.4    Digest-authentication Username and Password should be shown

Test Procedure:
1. Log in AP web UI by super account
2. Navigate to Management page
3. Get "Digest-authentication Username" and "Digest-authentication Password"
4. Use super account to connect to AP via CLI
5. Execute command "get tr069" and get the tr069 username/password from it
   output
5. Make sure the tr069/password from web ui and cli are the same.
6. Log out AP webui/cli

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

# define constant for each test type
TEST_TR069_MODE_AFTER_FACTORY = 0
TEST_USERNAME_PASSWORD_SHOWN  = 1
TEST_DEVICE_CALL_HOME_INFORM  = 2

ERR_MSGS = [
    'Error: tr069 authentication is not consistent. Web ui: %s. cli: %s',
]
PASSMSG = 'Digest authentication Username/Password shown correctly'
class AP_CheckDigestAuthInfo(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = None
        self._cfg_test_params(**conf)

    def test(self):
        self.ap.start(15)
        self._get_results()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_results()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        logging.info('Cleaning up the test...')
        self.ap.stop()
        del self.ap
        del self.ap_cli
        self.fm.logout()

    def _cfg_test_params(self, **kwa):
        self.p = {
            #'model': 'zf2925',
            'ap_ip': '',
            'pass_msg': PASSMSG,
            'webui_tr069_cfg': {'tr069_username': '', 'tr069_password': ''},
            'cli_tr069_cfg': {'tr069_username': '', 'tr069_password': ''},
        }
        self.p.update(kwa)
        self.p['tr069_auth_keys'] = self.p['webui_tr069_cfg'].keys()
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
        Get tr069 authentication username/password from AP webui and cli
        'exp_tr069_cfg': {},
            'display_tr069_cfg': {'tr069_username': '', 'tr069_username': ''},
        '''
        logging.info('Getting tr069 authentication username/password from webui...')
        self._wait_for_ap_cpu_free()

        self.p['webui_tr069_cfg'] = lib.ap.acc.get(self.ap, self.p['tr069_auth_keys'])
        logging.info('Got tr069 authentication from web ui: %s' % self.p['webui_tr069_cfg'])

        self.p['cli_tr069_cfg'] = dict(
            tr069_username = self.ap_cli.get_tr069()['cpe_user'].strip(),
            tr069_password = self.ap_cli.get_tr069()['cpe_pass'].strip(),
        )
        logging.info('Got tr069 authentication from cli: %s' % self.p['cli_tr069_cfg'])

    def _test_results(self):
        '''
        Test to make sure tr069 authentication username/password from web ui and cli
        are consistent
        '''
        retries = 5
        for t in try_times(retries):
            if self.p['webui_tr069_cfg'] == self.p['cli_tr069_cfg']:
                self.passmsg = PASSMSG
            else:
                self.errmsg = ERR_MSGS[0] % (self.p['webui_tr069_cfg'], self.p['cli_tr069_cfg'])
            # sometimes it cannot get the remote mgmt so we need retry it several times.
            if self.errmsg is None:
                break
            elif t < retries:
                logging.info('Warning!! Tr069 aunthentication is not consistent. Retry %s times' % t)
                self.errmsg = None
                self._get_results()


