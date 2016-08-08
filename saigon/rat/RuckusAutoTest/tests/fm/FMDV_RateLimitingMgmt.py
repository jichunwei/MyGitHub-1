'''
This test script is to verify following authentication types:
5    ZF2925 8.0 wireless Authentication
3.1.10    Modify the Rate limiting in Device View

Test Procedure:
1.    Login the FlexMaster webUI by admin account.
2.    Go to Inventory page, click on a device to enter Device View page.
3.    Go to Details > Wireless tab and configure a wlan with above any authentication type
4.    Go to Details > Rate Limiting tab and configure a r with above any authentication type
5.    Log out the FlexMaster web UI.

Pass/Fail/Error Criteria (including pass/fail messages):
+ Pass: if all of the verification steps in the test case are met.
+ Fail: if one of verification steps is failed.
+ Error: Other unexpected events happen.

'''
import os, time, logging, re, random, traceback
from datetime import *
from pprint import pprint, pformat

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.fm.lib_FM import *
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.fm.config_mapper_fm_old import *


class FMDV_RateLimitingMgmt(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = None
        self._cfgTestParams(**conf)

    def test(self):
        self._cfgWlan()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._cfgRateLimiting()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._assoc_client()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testConsistentUI()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testConnectionStatus()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testRateLimitingThreshold()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        self._unassoc_client()
        self._uncfgWlan()
        self._uncfgRateLimiting()
        self.aliases.fm.cleanup_device_view(self.dv)
        self.aliases.fm.logout()

    def _cfgTestParams(self, **kwa):
        self.p = {
            'ap_ip':     '192.168.0.222',
            'client_ip': '192.168.1.11',
            'traffic_srv_ip': '192.168.0.124',
            'wlan_cfg':  {},
            'rl_cfg':  {}, #  rate limiting config
            'rad_cfg': dict(
                username = 'user.eap',
                password = '123456',
            ),
            'error_margin': 0.04,
            'test_name': '',
        }
        self.p.update(kwa)

        self.aliases = init_aliases(testbed=self.testbed)
        self.ap = self.aliases.tb.getApByIp(self.p['ap_ip'])
        self.dv = self.aliases.fm.get_device_view(ip=self.p['ap_ip'])
        self.client = self.aliases.tb.get_clientByIp(self.p['client_ip'])
        self._calcRateValue()
        self.traffic_srv_ip = self.p['traffic_srv_ip']
        self.client_wifi_ip = '' # will be gotten in _testConnectionStatus
        # remove items, which are not available on AP web ui, in the test cfg
        ap_unsupported_items = ['client_isolation']
        for k in ap_unsupported_items:
            if k in self.p['wlan_cfg']: del self.p['wlan_cfg'][k]

        logging.info('Test configs:\n%s' % pformat(self.p))

    def _calcThrputThresholdFromThrputStr(self, thrput_str, error_margin, std_weight=1024.0):
        '''
        This function is to calculate uplink/donwlink throughput threshold in mb from input Rate Limiting
        setting.
        E.g: - thrput_str = '250kbps' --> thrput_threshold = 250/1024
             - thrput_str = '500kbps' --> thrput_threshold = 500/1024
             - thrput_str = '1mbps' --> thrput_threshold = 1
        '''
        # Get unit which is used for thrput_str: kbps, mbps, gbps
        unit_ui_setting = [unit for unit in ['k', 'm', 'g'] if unit in thrput_str.lower()]
        # Get the end position of a number from input uplink, downlink string
        # E.g: uplink = '250kbps' -> weight = 1024, end_num_pos = 3
        end_num_pos = thrput_str.lower().find(unit_ui_setting[0])
        # get number from thrput string
        num_ui_setting = float(thrput_str[0:end_num_pos].strip())
        # calculate weight according to its unit setting
        weight = {
            'k': 1.0, # kbps
            'm': 1024.0, # # mbps: standard unit to calculate for rate limiting
            'g': 1024.0*1024.0, # gbps
        }[unit_ui_setting[0]]

        # return thrput_threshold
        return (num_ui_setting * (weight/std_weight) * (1.0 + error_margin))

    def _calcRateValue(self):
        '''
        This function is to calculate threshold for uplink and downlink in mbps.
        Need to convert from kbps to mbps before calculate Rate Limiting
        '''
        STD_THRPUT = 1024.0 # standard throuput for uplink/downlink in mb
        self.uplink_threshold = self._calcThrputThresholdFromThrputStr(self.p['rl_cfg']['uplink'],
                                self.p['error_margin'], STD_THRPUT)
        self.downlink_threshold = self._calcThrputThresholdFromThrputStr(self.p['rl_cfg']['downlink'],
                                  self.p['error_margin'], STD_THRPUT)

    def _cfgWlan(self):
        try:
            ret, msg = lib.fmdv.wlan.cfgWLANDet(self.dv, self.p['wlan_cfg'])
            if ret != self.dv.TASK_STATUS_SUCCESS:
                self.errmsg = msg
                logging.info(msg)
        except Exception, e:
            if re.search('Element ".*Task.*" is not found', str(e)):
                logging.info('This wlan may be already configured. No need to config again.')
                return
            else:
                raise

    def _cfgRateLimiting(self):
        try:
            wlan = int(self.p['wlan_cfg']['wlan_num'])
            ret, self.errmsg = lib.fmdv.rl.set_cfg(self.dv, wlan, self.p['rl_cfg'])
            if ret != self.dv.TASK_STATUS_SUCCESS:
                logging.info(self.errmsg)
        except Exception:
            self.errmsg = 'Cannot config rate limting. Error: %s' % traceback.format_exc()

    def _assoc_client(self):
        client_cfg = copy.deepcopy(self.p['wlan_cfg'])
        client_cfg.update(self.p['rad_cfg'])
        # remove all wlan on client before doing associate
        self.client.remove_all_wlan()

        client_cfg = map_station_cfg(client_cfg)
        logging.info('Client config: %s' % pformat(client_cfg))
        assoc_client(self.client, client_cfg)

    def _testConsistentUI(self):
        '''
        This function is to make sure Device View and AP web UI show
        the rate limiting cfg exactly
        '''
        logging.info('Test conistent FM Device View and AP Web UI')
        self._wait4_ap_stable()
        self.ap.start(15)

        timeout = 17 # minutes. Use a value greater than default interval 15
        end_time = time.time() + timeout*60
        is_different, retries = True, 1
        wlan = int(self.p['wlan_cfg']['wlan_num'])

        while is_different and time.time() < end_time:
            try:
                dv_ui_display = lib.fmdv.rl.get_cfg(self.dv, wlan, self.p['rl_cfg'].keys())
                ap_ui_display = lib.ap.wlan.getWLAN(self.ap, wlan,
                                                self.p['rl_cfg'].keys(), True)
                logging.info('Got rate limiting setting from Device View:\n%s' % pformat(dv_ui_display))
                logging.info('Got rate limiting setting from AP web UI:\n%s' % pformat(ap_ui_display))

                # compare returned values from Device View with input rate limiting cfg first
                ret_msg_1 = compare_dict(dv_ui_display, self.p['rl_cfg'], tied_compare=False)
                # Compare two dv_ui_cfg and ap_ui_cfg
                ret_msg_2 = compare_dict(dv_ui_display, ap_ui_display, tied_compare=False)
                if ret_msg_1 or ret_msg_1:
                    self.errmsg = ret_msg_1 if ret_msg_1 else ret_msg_2
                    retries +=1
                    logging.info('%s. Retry %s times...' % (self.errmsg, retries))
                    # sleep a moment to wait
                    time.sleep(30)
                    continue

                # Come here, all the things are correct
                is_different, self.errmsg = False, None
                logging.info('Display of %s are consistent...' % ', '.join(self.p['rl_cfg'].keys()))
            except Exception, e:
                retries +=1
                self.errmsg = 'A strange error happened: %s' % (e.__str__())
                logging.info(self.errmsg + '. Ignore it and retry %s times!!!' % (retries))
                # sleep a moment to wait
                time.sleep(30)

        self.ap.stop()
        if self.errmsg:
            logging.info(self.errmsg)
            return
        logging.info('Device View and AP Web UI is consistent')

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

    def _testConnectionStatus(self):
        '''
        '''
        logging.info('Verify connection status for the client')
        end_time = time.time() + 180 # second
        while time.time() < end_time:
            self.client_wifi_ip, mac = self.client.get_wifi_addresses()
            if self.client_wifi_ip and not '0.0.0.0' in self.client_wifi_ip and not '169.254' in self.client_wifi_ip:
                logging.info('Got client wifi ip: %s' % self.client_wifi_ip)
                break
            time.sleep(1)

        if '0.0.0.0' in self.client_wifi_ip or '169.254' in self.client_wifi_ip:
            self.errmsg = ('Current ip: %s. The client could not get IP'
                          ' address from DHCP server.' % self.client_wifi_ip)
            logging.info(self.errmsg)
            return

        logging.info("Verify connection from the wifi client to the traffic server")
        ping_result = self.client.ping(self.traffic_srv_ip, 5*1000)
        if ping_result.find("Timeout") != -1:
            self.errmsg = 'The client could not ping to %s' % self.traffic_srv_ip
            logging.info(self.errmsg)
        else:
            logging.info("Ping OK. Correct behavior")

    def _sendTraffic(self, src_ip, des_ip):
        '''
        '''
        zap_res, msg = None, None
        try:
            zap_res = self.client.send_zap(sip=src_ip, dip=des_ip, period=50000,
                                          payload_len=300, time_run=30, test_tcp=True)
        except Exception, e:
            if e.message.find("Test result file was not created") != -1:
                # Resend traffic if it was not done properly
                zap_res = self.client.send_zap(sip=src_ip, dip=des_ip, period=50000,
                                          payload_len=300, time_run=30, test_tcp=True)
            else:
                msg = e.__str__()

        return zap_res, msg

    def _testRateLimitingThreshold(self):
        logging.info("Send traffic from the client to the traffic srv to verify uplink")
        zap_res, self.errmsg = self._sendTraffic(self.client_wifi_ip, self.traffic_srv_ip)
        if zap_res is None: return

        logging.info("The percentile 50%% of uplink is %.3f mbps" % zap_res["50.0"])
        logging.info("The allowed rate limit of uplink is %.3f mbps" % self.uplink_threshold)
        if zap_res["50.0"] > self.uplink_threshold:
            self.errmsg = ("The measured rate %.3f mbps is higher than expected"
                           " (%.3f mbps) on WLAN %s" %
                           (zap_res["50.0"], self.uplink_threshold, self.p['wlan_cfg']['wlan_ssid']))
            return

        logging.info("Send traffic from the traffic srv to the client to verify downlink")
        zap_res, self.errmsg = self._sendTraffic(self.traffic_srv_ip, self.client_wifi_ip)
        logging.info("The percentile 50%% of downlink is %.3f mbps" % zap_res["50.0"])
        logging.info("The allowed rate limit of downlink is %.3f mbps" % self.downlink_threshold)
        if zap_res["50.0"] > self.downlink_threshold:
            self.errmsg = ("The measured rate %.3f mbps is higher than expected"
                           " (%.3f mbps) on WLAN %s" %
                           (zap_res["50.0"], self.downlink_threshold, self.p['wlan_cfg']['wlan_num']))
            return

        self.passmsg = ('The wlan %s works correctly with setting: %s' %
                        (self.p['wlan_cfg']['wlan_num'], pformat(self.p['test_name'])))

    def _unassoc_client(self):
        self.client.remove_all_wlan()

    def _uncfgWlan(self):
        # We should copy to another variable to avoid changing the input cfg. In case
        # the test fail, the input cfg will be used again so if we change the input
        # cfg here it causes the rat failed to re-run again.
        default_cfg = copy.deepcopy(self.p['wlan_cfg'])
        default_cfg.update(dict(
            wlan_name         = 'Wireless %s' % self.p['wlan_cfg'].get('wlan_num', ''),
            wlan_ssid         = 'Wireless %s' % self.p['wlan_cfg'].get('wlan_num', ''),
            avail             = 'disabled',
            encrypt_method = 'disabled',
            client_isolation  = 'disabled',
        ))
        try:
            lib.fmdv.wlan.cfgWLANDet(self.dv, default_cfg)
        except Exception, e:
            logging.info('Warning: Cannot restore default config for this wlan. '
                         'Error: %s' % e.__str__())

    def _uncfgRateLimiting(self):
        try:
            wlan = int(self.p['wlan_cfg']['wlan_num'])
            ret, self.errmsg = lib.fmdv.rl.set_cfg(self.dv, wlan, dict(uplink='disabled', downlink='disabled'))
            if ret != self.dv.TASK_STATUS_SUCCESS:
                logging.info(self.errmsg)
        except Exception, e:
            logging.info('Warning: Cannot disable rate limting for the wlan %s. '
                         'Error: %s' % (wlan, e.__str__()))

