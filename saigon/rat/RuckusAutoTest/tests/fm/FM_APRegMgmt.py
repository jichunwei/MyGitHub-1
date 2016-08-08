'''
This test script is to verify following authentication types:
4.4.6    "Auto" mode and option 43
4.4.7    "FlexMaster only" mode and DNS resolve.
4.4.8    "FlexMaster only" mode with HTTPS

Test Procedure:
Common note: To verify these tc we have to change its serial to make it
             register to FM
4.4.6 "Auto" mode and option 43
    1. Configure dhcp option 43 for the FM
    2. Log in ap via cli as super account
    3. Enter shell mode, use "rbd change" command to change its serial
    4. Reset factory the ap
    5. Wait for a moment for the AP boot up and make sure it registers
       to FM

4.4.7 "FlexMaster only" mode and DNS resolve.
    1. Disable dhcp option 43 for the FM to make it doesn't use option
       to register to FM and configure a DNS server to make it resolve
       fm url in domain nam format.
    2. Log in ap via cli as super account
    3. Enter shell mode, use "rbd change" command to change its serial
    4. Reset factory the ap and wait for a moment for the AP boot up
    5. Navigate to Management page, set the fm url in domain name format
       like http://itms.ruckus.com/intune/server.
    6. Make sure that it registers to FM successfully

4.4.8 "FlexMaster only" mode with HTTPS
    1. Disable dhcp option 43 for the FM to make it doesn't use option
       to register to FM.
    2. Log in ap via cli as super account
    3. Enter shell mode, use "rbd change" command to change its serial
    4. Reset factory the ap and wait for a moment for the AP boot up
    5. Navigate to Management page, set the fm url with https
       like https://itms.ruckus.com/intune/server or https://fm_ip/intune/server
    6. Make sure that it registers to FM successfully.

Pass/Fail/Error Criteria (including pass/fail messages):
+ Pass: if all of the verification steps in the test case are met.
+ Fail: if one of verification steps is failed.
+ Error: Other unexpected events happen.

Pre-config:
    - get original serial
    - generate a one new serial
Test:
    - Cfg option 43: disable option 43 if fm mode else enable option 43
    - change device serial
    - reset factory
    - set fm url
    - check register status to FM of this device
clean-up:
    - enable option 43
    - disable the new device on FM
    - restore original serial
    - reset factory
    - set fm url
'''

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.fm.lib_FM import *
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.fm.config_mapper_fm_old import *

ERR_MSGS = [
    'Error: Not found AP (serial, ip): (%s, %s) registered to FM',
    'Error: Waited for %s(s), the AP did not send any inform msg after set a new interval to %s.',
    'Error: Waited for %s(s), the AP sent the first inform but faild after set a new inform interval to %s.',
]

PASSMSG = [
    'Found AP (serial, ip): (%s, %s) registered to FM with this mode',
]

class FM_APRegMgmt(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = None
        self._cfg_test_params(**conf)
        self.p['ori_serial'] = self.ap_cli.get_serial()
        logging.info('Generating a new unique serial for this test')
        self.p['new_serial'] = lib.fm.dreg.generate_unique_serials(self.fm, no=1, prefix='ZF')[0]

        logging.info('Test configs:\n%s' % pformat(self.p))

    def test(self):
        self._cfg_dhcp_option_43(self.p['disable_dhcp_43'])
        if self.errmsg: return ('FAIL', self.errmsg)

        self._cfg_ap(self.p['ap_ip'], self.p['new_serial'], self.p['input_mgmt_cfg'])
        if self.errmsg: return ('FAIL', self.errmsg)

        self._clear_ap_cache()

        self._wait_for_the_first_inform()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_results()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        logging.info('Cleaning up the test...')
        if self.p['disable_dhcp_43']:
            self._cfg_dhcp_option_43(disable=False)
        self._disable_new_device()
        self._cfg_ap(self.p['ap_ip'], self.p['ori_serial'], self.p['restore_mgmt_cfg'])
        self._clear_ap_cache()
        del self.ap, self.ap_cli, self.srv_cli
        self.fm.logout()

    def _cfg_test_params(self, **kwa):
        self.p = dict(
            ap_ip = '192.168.0.222',
            input_mgmt_cfg = dict(
                remote_mode     = 'auto',
                fm_url          = '',
                inform_interval = '5ms'
            ),
            restore_mgmt_cfg = dict(
                fm_url      = '',
                remote_mode = 'auto',
            ),
            srv_cfg = dict(
                ip_addr      = '192.168.30.252',
                user        = 'lab',
                password      = 'lab4man1',
                root_password = 'lab4man1',
            ),
            disable_dhcp_43 = False,
            timeout = 10, # time to monitor the AP registers to FM in mins
        )
        self.p.update(kwa)

        init_coms(
            self,
            dict(
                 tb=self.testbed, ap_ip=self.p['ap_ip'],
                 apcli_cfg=dict(ip_addr=self.p['ap_ip']),
                 srv_cfg=self.p['srv_cfg'],
            )
        )
        if not self.p['restore_mgmt_cfg']['fm_url']:
            self.p['restore_mgmt_cfg']['fm_url'] = ('http://%s/intune/server' %
                                                   self.fm.get_cfg()['ip_addr'])

    def _cfg_dhcp_option_43(self, disable=True):
        MAX_TRIES = 10
        for i in try_times(MAX_TRIES, 10):
            try:
                if disable:
                    self.srv_cli.disable_option_43(product=self.srv_cli.PRODUCT_INFO_FM, vendor='ruckus_info')
                    logging.info('Disabled dhcp option 43...')
                else:
                    self.srv_cli.enable_option_43(product=self.srv_cli.PRODUCT_INFO_FM, vendor='ruckus_info')
                    logging.info('Enabled dhcp option 43...')
                break
            except Exception, e:
                self.errmsg = 'Cannot config dhcp server. Error: %s' % e.__str__()
                logging.info(self.errmsg)
                log_trace()
                if i < MAX_TRIES:
                    self.errmsg = None
                    logging.info('Sleep a moment and retry again...')


    def _cfg_ap(self, ap_ip, serial, mgmt_cfg):
        '''
        - change device serial
        - reset factory
        - set fm url
        '''
        try:
            logging.info('Set a serial %s for this AP' % serial)
            if not set_ap_serial(serial=serial, config=dict(ip_addr=ap_ip)):
                self.errmsg = ('Cannot set the new serial %s for this AP %s' %
                              (serial, ap_ip))
                return

            if not set_ap_factory(config=dict(ip_addr=ap_ip)):
                self.errmsg = 'Cannot reset factory for this AP %s' % ap_ip
                return

            self._wait_for_ap_cpu_free()

            self.ap.start(15)
            logging.info('Set cfg %s to AP %s' % (pformat(mgmt_cfg), ap_ip))
            lib.ap.acc.set(self.ap, mgmt_cfg)
            self.ap.stop()
        except Exception, e:
            self.errmsg = 'Error: %s' % e.__str__()
            log_trace()

        if self.errmsg: logging.info(self.errmsg)

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

    def _wait_for_the_first_inform(self):
        '''
        After we re-set call home interval, ap may take a little time to stop and
        start tr069 service. This function is to wait for the first call home
        successfully.
        '''
        logging.info('Waiting for AP send the first inform...')
        #self._wait_for_ap_cpu_free()

        status, msg, timeout = None, '', 60*5
        for i in try_interval(timeout=timeout, interval=20):
            try:
                self.ap.start(15)
                status, msg = lib.ap.acc.get_tr069_inform_status(self.ap)
                self.ap.stop()
                if lib.ap.acc.TR069_STATUS_INFORM_SUCCESS == status:
                    logging.info('It called home the first time successfully. \nStatus: %s' %
                                 pformat(msg))
                    break
                else:
                    logging.info('Not send yet. Sleep to wait...')
            except Exception:
                # sometimes, error happens due to cannot extract time from tr069 status table
                log_trace()
                time.sleep(10)

        print 'status, msg: %s, %s' % (status, msg)
        self.errmsg = {
            lib.ap.acc.TR069_STATUS_INFORM_SUCCESS:  None,
            lib.ap.acc.TR069_STATUS_NO_INFORM:       ERR_MSGS[1] % (timeout, self.p['input_mgmt_cfg']['inform_interval']),
            lib.ap.acc.TR069_STATUS_INFORM_FAIL:     ERR_MSGS[2] % (timeout, self.p['input_mgmt_cfg']['inform_interval']),
        }[status]
        if self.errmsg:
            logging.info('Tr069 status msg: %s' % pformat(msg))
            logging.info(self.errmsg)

    def _test_results(self):
        '''
        Test to make sure tr069 authentication username/password from web ui and cli
        are consistent
        '''
        logging.info('Checking registration of AP (serial, ip): (%s, %s) to FM' %
                     (self.p['new_serial'], self.p['ap_ip']))

        lib_f = lib.fm.dreg
        if lib_f.monitor_device_reg(self.fm, self.p['new_serial'], self.p['timeout']):
            msg = self.passmsg = PASSMSG[0] % (self.p['new_serial'], self.p['ap_ip'])
        else:
            msg = self.errmsg = ERR_MSGS[0] % (self.p['new_serial'], self.p['ap_ip'])

        logging.info(msg)

    def _clear_ap_cache(self):
        '''
        This function is to reboot AP after re-set inform interval. Sometimes,
        we set inform interval several times, it causes the AP CPU very high
        and crashed. This is to refresh AP and make sure it is in
        good status for next test case.
        '''
        ap_cfg = dict(config={'ip_addr': self.p['ap_ip']})
        reboot_ap({'ip_addr': self.p['ap_ip']})
        wait4_ap_up(**ap_cfg)
        self._wait_for_ap_cpu_free()

    def _disable_new_device(self):
        '''
        This function to disable a new device registered to FM
        '''
        logging.info('Disable the new device %s on FM' % self.p['new_serial'])
        try:
            lib.fm.dreg.set_device_status(self.fm, self.p['new_serial'],
                                             lib.fm.dreg.DEV_STATUS_UNAVAILABLE, 'Automation changed to Unavailable')
        except Exception, e:
            logging.info('Warning: Cannot disable the device (ip, serial):(%s, %s). '
                         'Error: %s' % (self.p['ap_ip'], self.p['new_serial'], e.__str__()))
