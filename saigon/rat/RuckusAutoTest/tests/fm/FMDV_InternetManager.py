'''
3.1.5    Internet/WAN parameters
3.1.6    Modify the Device View Internet/WAN status with STATIC IP address
3.1.7    Modify the Device View Internet/WAN status with DYNAMIC IP address

Test procdure:
3.1.5:
    1. Log in FM as admin
    2. According to each model, open their Device View
    3. Navigate to Details > Internet/WAN on Device View
    4. Get follwing params:
        1. connection_status
        2. connection_type
        3. gateway
        4. ip
        5. mac
        6. net_mask
        7. ntp_server
        9. pri_dns
        10. sec_dns
    5. Open web ui of that model
    6. Navigate to Status > Internet
    7. Get the those items
    8. Compare it to make sure that they are consistent

    Pass/Fail/Error Criteria (including pass/fail messages):
    + Pass: if all of the verification steps in the test case are met.
    + Fail: if one of verification steps is failed.
    + Error: Other unexpected events happen.

3.1.6 and 3.1.7:
    1. Log in FM as admin
    2. According to each model, open their Device View
    3. Navigate to Details > Internet/WAN on Device View
    4. Set the ip to dynamic or static and wait for the task completed successfully
    5. Click refresh button and make sure the DV shows new configuration
    6. Open AP web UI of that model
    7. Navigate to Status > Internet
    8. Make sure the AP also show the new configuration

    Pass/Fail/Error Criteria (including pass/fail messages):
    + Pass: if all of the verification steps in the test case are met.
    + Fail: if one of verification steps is failed.
    + Error: Other unexpected events happen.
'''

import time
import logging
from pprint import pformat

from RuckusAutoTest.common.utils import compare_dict, log_trace, try_interval
from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.fm.lib_FM import init_aliases
from RuckusAutoTest.components import Helpers as lib

class FMDV_InternetManager(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = None
        self._cfgTestParams(**conf)


    def test(self):
        if 'display' == self.p['test_type']:
            self._testParamDisplay()
        else:
            self._testModifyIP()
        if self.errmsg: return ('FAIL', self.errmsg)

        return('PASS', self.passmsg)


    def cleanup(self):
        if self.dv:
            if self.p['test_type'] in ['dhcp', 'static']:
                self._restoreOriginalCfg()
            self.aliases.fm.cleanup_device_view(self.dv)

        self.aliases.fm.logout()


    def _cfgTestParams(self, **kwa):
        self.p = {
            #'model': 'ZF2925',
            'ap_ip': '',
            'test_name': 'Internet/WAN parameters',
            'test_type': 'display', # dhcp, static
        }
        self.p.update(kwa)

        self.aliases = init_aliases(testbed=self.testbed)

        # get device view of the first ap in the test bed
        self.dv = self.aliases.fm.get_device_view(ip=self.p['ap_ip'])
        self.ap = self.aliases.tb.getApByIp(self.p['ap_ip'])

        if self.p['test_type'] in ['dhcp', 'static']:
            self._defineTest_RestoreCfg()

        logging.info('Test configs:\n%s' % pformat(self.p))


    def _testParamDisplay(self):
        '''
        TODO:
        1. We have a bug 9386 for connection status "connection_status"
           so we temporarily don't verify this item now.
        2. There is another bug 6270 for ntp server "ntp_server" problem so we temporarily
           don't verify this param also.
        We verify following items:
            1. connection_status
            2. connection_type
            3. gateway
            4. ip
            5. mac
            6. net_mask
            7. ntp_server
            9. pri_dns
            10. sec_dns
        '''
        logging.info('Testing Internet params display...')
        timeout = 17 # minutes. Use a value greater than default interval 15
        end_time = time.time() + timeout*60

        is_different, retries = True, 1
        self.ap.start(15)
        while is_different and time.time() < end_time:
            try:
                dv_cfg = lib.fmdv.net.get_cfg(self.dv)
                ap_cfg = lib.ap.net.get_cfg(self.ap, fm_return=True)

                del dv_cfg['connection_status']
                del ap_cfg['connection_status']
                del dv_cfg['ntp_server']
                del ap_cfg['ntp_server']

                logging.info('Summary display: %s' % pformat(dv_cfg))
                logging.info('AP display: %s' % pformat(ap_cfg))
                self.errmsg = compare_dict(dv_cfg, ap_cfg, tied_compare=False)

                # two dictionaries are different
                if self.errmsg:
                    logging.info('%s. Retry %s time(s)...' % (self.errmsg, retries))
                    retries +=1
                    # sleep a moment to wait
                    time.sleep(30)
                    continue

                is_different = False
            except Exception, e:
                log_trace()
                logging.info('A strange error happened: %s. Ignore it and retry again!!!' % e.__str__())

        self.ap.stop()
        if is_different:
            self.errmsg = 'Error: FM DV and AP Internet param display are still '\
                          'different after %s minutes trying' % timeout
            logging.info(self.errmsg)

        if not self.errmsg: self.passmsg = "FM Device View and AP Internet UI are consistent"


    def _defineTest_RestoreCfg(self):
        '''
        This function is to define cfg to set and restore
        '''
        # get current config from Device View
        self.original_cfg = lib.fmdv.net.get_cfg(self.dv, ['connection_type', 'ip', 'net_mask'])

        self.test_cfg = dict(connection_type = 'dhcp',) \
              if self.p['test_type'] == 'dhcp' else \
              dict(connection_type = 'static', ip=self.original_cfg['ip'], net_mask=self.original_cfg['net_mask'])

        self.restore_cfg = dict(connection_type = 'dhcp',) \
              if self.original_cfg['connection_type'] == 'dhcp' else \
              dict(connection_type = 'static', ip=self.original_cfg['ip'], net_mask=self.original_cfg['net_mask'])


    def _testModifyIP(self):
        '''
        This function is to test set dynamic ip (dhcp) and static ip from device view
        '''
        logging.info('Testing: %s' % self.p['test_name'])
        current_connection_type = self.original_cfg['connection_type']

        if current_connection_type.lower() != self.p['test_type']:
            status, self.errmsg = lib.fmdv.net.set_cfg(self.dv, self.test_cfg)
            if self.dv.TASK_STATUS_SUCCESS != status:
                logging.info(self.errmsg)
                return

        self.ap.start(15)
        #while is_different and time.time() < end_time:
        for i in try_interval(timeout=17*60, interval=5):
            try:
                # get connection type and ip address of dv, ap to compare
                dv_cfg = lib.fmdv.net.get_cfg(self.dv, ['connection_type', 'ip'])
                ap_cfg = lib.ap.net.get_cfg(self.ap, ['connection_type', 'ip'], fm_return=True)

                logging.info('Summary display: %s' % pformat(dv_cfg))
                logging.info('AP display: %s' % pformat(ap_cfg))
                self.errmsg = compare_dict(dv_cfg, ap_cfg, tied_compare=False)

                if self.errmsg:
                    logging.info('Error: %s. Retry again!!!' % self.errmsg)
                    continue

                self.passmsg = 'FM Device > Internet works correctly with "%s" type' % self.p['test_type']
                break
            except Exception, e:
                log_trace()
                logging.info('An error happened: %s. Ignore it and retry again!!!' % e.__str__())

        self.ap.stop()

    def _restoreOriginalCfg(self):
        '''
        This function is to restore original type for the tested ap
        '''
        # only restore if original_connection_type is different from the test_type
        logging.info('Restoring original type "%s"...' % self.original_cfg['connection_type'])
        if self.original_cfg['connection_type'] != self.p['test_type']:
            status, msg = lib.fmdv.net.set_cfg(self.dv, self.restore_cfg)
            if self.dv.TASK_STATUS_SUCCESS != status:
                logging.info('Warning: Cannot restore "%s" type for this ip. Error: %s' % \
                             (self.original_connection_type, msg))

