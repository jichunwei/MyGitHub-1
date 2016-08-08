'''
1.1.4      Firmware Status
1.1.4.1    Model type and firmware version display
1.1.4.2    Consistency between number of display devices
           and actual connected devices

Config
. get and init all ap webUIs
Test
. get all the rows in the firmware status table (filter ZDs)
. get all devices on testbed, for each of them
  . get the model type, go and get software version
  . put these info in a dict, if they are the same then increase the
    number of devices
. get the diffs of 2 dicts and report success/fail accordingly
> Test on AP side only, will extend to ZD later

Clean up
. log out FM
'''
import logging
from pprint import pformat

from RuckusAutoTest.common.utils import log, log_cfg
from RuckusAutoTest.tests.fm.lib_FM import init_coms
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.models import Test


class FM_InvZDDetails(Test):
    def config(self, cfg):
        self.errmsg = self.passmsg = ''
        self._cfg_test_params(cfg)


    def test(self):
        self._get_fm_fws()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._get_testbed_fws()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_fws()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)


    def cleanup(self):
        self.fm.logout()


    def _cfg_test_params(self, cfg):
        self.p = cfg
        init_coms(self,dict(tb=self.testbed,ap_ips=self.testbed.get_all_ap_ips()))

        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _get_fm_fws(self):
        logging.info('Get all the firmware info (model, firmware, total_devices) on FM')
        fm_fws = [dict(model=i['model'].lower(), firmware=i['firmware'],
                       total_devices=i['total_devices'])
                      for i in lib.fm.fw_status.get_all(self.fm)]
        log_cfg(fm_fws, 'fm_fws')

        # temporarily filter ZD firmwares
        for i in reversed(range(len(fm_fws))):
            if 'zd' in fm_fws[i]['model'].lower():
                del fm_fws[i]

        self.p['fm_fws'] = fm_fws
        log_cfg(self.p['fm_fws'], "self.p['fm_fws']")


    def _get_ap_fw(self, ap):
        logging.info('Get the AP firmware of %s' % ap.config['ip_addr'])
        ap.start()
        fw = lib.ap.sttd.get_all(ap)['firmware']
        ap.stop()
        return fw


    def _inc_total_devices(self, fws, fw, model):
        for i in range(len(fws)):
            if fws[i]['model'] == model and fws[i]['firmware'] == fw:
                log('Same model & firmware, increase the total devices')
                fws[i]['total_devices'] += 1
                return True
        return False


    def _get_testbed_fws(self):
        logging.info('Get all the firmware info of each device')
        ap_fws = []
        for ap in self.aps:
            fw = self._get_ap_fw(ap)
            model = ap.config['model'].lower()
            if not self._inc_total_devices(ap_fws, fw, model):
                ap_fws.append(dict(model=model, firmware=fw, total_devices=1))

        for i in range(len(ap_fws)):
            ap_fws[i]['total_devices'] = str(ap_fws[i]['total_devices'])

        self.p['device_fws'] = ap_fws
        log_cfg(self.p['device_fws'], "self.p['device_fws']")


    def _filter(self, list1, list2):
        return [i for i in list1 if i not in list2]


    def _test_fws(self):
        '''
        . the fm fws can not be blank when there is aps
        . make sure 2 lists are the same
        '''
        if len(self.aps) and not len(self.p['fm_fws']):
            self.errmsg = 'There is %s APs while no firmware reported on FM' % len(self.aps)
            return

        fm_only = self._filter(self.p['fm_fws'], self.p['device_fws'])
        if fm_only:
            self.errmsg = 'These devices are not in testbed - %s' % fm_only
            return

        ap_only = self._filter(self.p['device_fws'], self.p['fm_fws'])
        if ap_only:
            self.errmsg = 'These devices are not in FM - %s' % ap_only
            return

        self.passmsg = 'Model type and firmware version display correctly'
        return

