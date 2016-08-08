'''
1.2.1 Inventory > Manage Devices
  Filter AP/ZD report works > split this to 2 testcases

1.2.2    1.1.7.4    Reports
1.2.2.1    1.1.7.4.1    All ZoneDirectorr report
1.2.2.2    1.1.7.4.2    ZoneDiector associated clients
1.2.2.3    1.1.7.4.3    ZoneDirector Managed APs report


Config
. nothing

Test
. navigate to Inventory > Reports
. selecting these: report_cate=device_view,
    1. device_view=aps report_type=aps
    2. device_view=zds report_type=zds
. click on 'generate'
. get the table info
. make sure only aps/zds displayed on the table accordingly

Clean up
. log out fm
'''
import logging
from pprint import pformat

from RuckusAutoTest.common.utils import log_cfg
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.dev_features import FM as fmft
from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.fm.lib_FM import init_coms


class FM_InvFilterView(Test):
    def config(self, cfg):
        self.errmsg = self.passmsg = ''
        self._cfg_test_params(cfg)


    def test(self):
        self._gen_report()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._get_report()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_report()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)


    def cleanup(self):
        self.fm.logout()


    def _cfg_test_params(self, cfg):
        self.p = cfg

        init_coms(self,dict(tb=self.testbed,zd_ip='192.168.0.101'))
        self.p['device_ips'] = dict(
            aps=self.tb.get_all_ap_ips,
            zds=self.tb.get_all_zd_ips,
        )[self.p['testcase']]() if self.p['testcase'] in ['aps', 'zds'] else None
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _gen_report(self):
        lib.fm.ireports.set(self.fm, self.p['report'])


    def _get_info(self, tbl, key='ip'):
        return [r[key] for r in tbl]


    def _get_report(self):
        # a bit of hack here
        lib.fm.ireports.locators['tbl'].cfg['hdrs'] = fmft.report_ths[self.p['testcase']]
        if self.p['testcase'] == 'zd_client':
            self.p['tbl_ips'] = [
                r['row']['mac']
                  for r in lib.fm.ireports.get_tbl(self.fm, 'tbl', dict(get='iter'))
            ]
        else:
            self.p['tbl_ips'] = [
                r['row']['ip'].split(':')[0]
                  for r in lib.fm.ireports.get_tbl(self.fm, 'tbl', dict(get='iter'))
            ]
        log_cfg(self.p['tbl_ips'], 'tbl_ips')
#        lib.fm.ireports.locators['tbl'].cfg['hdrs'] = fmft.report_ths[self.p['testcase']]
#        self.p['tbl_ips'] = [
#            r['row']['ip'].split(':')[0]
#              for r in lib.fm.ireports.get_tbl(self.fm, 'tbl', dict(get='iter'))
#        ]


    def _compare(self, list1, list2):
        if len(list1) and not len(list2):
            self.errmsg = 'There was no item on this report while there are %s devices' % \
                          len(list1)
            return

        not_in_tb_ips = list(set(list1)- set(list2))
        if not_in_tb_ips:
            self.errmsg = 'These devices are not in testbed - %s' % not_in_tb_ips
            return

        not_in_report_ips = list(set(list2) - set(list1))
        if not_in_report_ips:
            self.errmsg = 'These devices are not reported - %s' % not_in_report_ips
            return
        self.passmsg = 'The filter works correctly'
        return


    def _test_report(self):
        '''
        . the gen tbl can not be blank and total devices must = testbed > devices
        . for each device (ap/zd accordingly) on testbed, make sure it is in the tbl
        '''
        if self.p['testcase'] == 'zd_ap':
            return self._test_zd_ap_report()
        if self.p['testcase'] == 'zd_client':
            return self._test_zd_client_report()
        return self._compare(self.p['device_ips'], self.p['tbl_ips'])


    def _test_zd_ap_report(self):
        self.zd.start()
#        self.p['device_ips'] = lib.zd.ma.get_tbl(self.zd, 'ap_tbl', None, True, 'default')
        self.p['device_ips'] = self._get_info(
            lib.zd.ma.get_tbl(self.zd, 'ap_tbl', {}, True, 'default')
        )
        self.zd.stop()
        return self._compare(self.p['device_ips'], self.p['tbl_ips'])


    def _test_zd_client_report(self):
        self.zd.start()
        try:
            self.p['device_ips'] = self._get_info(
                lib.zd.mc.get_tbl(self.zd, 'client_tbl', {}, True, 'default'),
                key='mac',
            )
        except Exception, e:
            if 'Element not found' in str(e) and '/tbody/tr' in str(e):
                logging.info('no client assoc than, the table can NOT be found')
                self.p['device_ips'] = []
            else:
                raise
        self.zd.stop()
        log_cfg(self.p['device_ips'])
        return self._compare(self.p['device_ips'], self.p['tbl_ips'])
#        self.zd.start()
#        self.p['device_ips'] = lib.zd.mc.get_tbl(self.zd, 'ap_tbl', None, True, 'default')
#        self.zd.stop()
#        self.p['device_ips'] = self.p['tbl_ips']
#        return self._compare(self.p['device_ips'], self.p['tbl_ips'])
