'''
This test script is to verify following authentication types:
3    Device View status in FM
3.1    Detail of ZF2925 8.0
#3.1.1    Device Summary page in FM Device View.
3.1.2    Search by Serial number in 12 digits and MAC address in Device View of FM.


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
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.fm.lib_FM import init_aliases, get_ap_default_cli_cfg
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.RuckusAP import RuckusAP


class FMDV_DeviceSearch(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = None
        self._cfgTestParams(**conf)


    def test(self):
        self._testFindDevice()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)


    def cleanup(self):
        self.aliases.fm.cleanup_device_view(self.dv)
        self.aliases.fm.logout()


    def _cfgTestParams(self, **kwa):
        self.p = {
            'test_name': 'Search by Serial Number and MAC address',
            'ip_list': [],
            'mac_list': [],
            'serial_list': [],
        }
        self.p.update(kwa)

        self.aliases = init_aliases(testbed=self.testbed)
        # get all ip addr in the test bed
        for ap in self.aliases.aps:
            self.p['ip_list'].append(ap.get_cfg()['ip_addr'])

        self._getList_MAC_Serial()
        # get device view of the first ap in the test bed
        self.dv = self.aliases.fm.get_device_view(ip=self.p['ip_list'][0])

        logging.info('Test configs:\n%s' % pformat(self.p))


    def _getList_MAC_Serial(self):
        '''
        Get all MACs and Serials of ap in the testbed
        '''
        config = get_ap_default_cli_cfg()
        for ip in self.p['ip_list']:
            config['ip_addr'] = ip
            try:
                ap_cli = RuckusAP(config)
            except:
                time.sleep(10)
                ap_cli = RuckusAP(config)

            self.p['mac_list'].append(ap_cli.get_base_mac())
            self.p['serial_list'].append(ap_cli.get_serial())


    def _testFindDevice(self):
        for idx, serial in enumerate(self.p['serial_list']):
            if not lib.fmdv.summary.findDevice(self.dv, serial, True):
                self.errmsg = 'Cannot find a device serial %s of the testbed' % serial
                logging.info(self.errmsg)
                break

            if not lib.fmdv.summary.findDevice(self.dv, self.p['mac_list'][idx], False):
                self.errmsg = 'Cannot find a device MAC %s of the testbed' % self.p['mac_list'][idx]
                logging.info(self.errmsg)
                break

        self.passmsg = 'FM Device View can search all devices by: \nSerials:%s. \nMACs:%s' % \
                        (pformat(self.p['serial_list']), pformat(self.p['mac_list']))
        logging.info(self.passmsg)

