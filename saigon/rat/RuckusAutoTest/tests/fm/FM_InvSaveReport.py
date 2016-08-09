'''
1.2.1 Inventory > Manage Devices
  Save report as xls

Config
. delete the downloaded file (if exists)

Test
. navigate to Inventory > Reports
. selecting these: report_cate=device_view, device_view=aps, report_type=aps
. click on 'generate'
. click on 'advanced reports options'
. save the report as xls
. get the table info
. re-open the xls file
. make sure the xls file is the same as report on the table

Clean up
. delete the downloaded xls file
'''
import logging
from pprint import pformat

from RuckusAutoTest.tests.fm.lib_FM import remove_file, init_coms, log_cfg
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.dev_features import FM as fmft
from RuckusAutoTest.models import Test


testcase = 0
test_cfg = [
    dict(
        report=dict(
            report_cate=fmft.report_cates['device_view'],
            view=fmft.predef_views['aps'],
            report_type=fmft.report_types['aps'],
            #generate_btn='report_type',
            #advanced_ops_btn='report_type',
            #save_report_btn=None, # for clicking on this
        ),
        #report_file='report.xls',
    ),
][testcase]


class FM_InvSaveReport(Test):
    def config(self, cfg):
        self.errmsg = self.passmsg = ''
        self._cfg_test_params(cfg)


    def test(self):
        self._gen_n_save_report()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._get_report_tbl()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._get_report_xls()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._compare_reports()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)


    def cleanup(self):
        if 'xslfile' in self.p:
            try:
                remove_file(self.p['xslfile'])
            except:
                pass
        self.fm.logout()


    def _cfg_test_params(self, cfg):
        self.p = cfg
        #self.p = test_cfg
        init_coms(self,dict(tb=self.testbed,))
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _gen_n_save_report(self):
        logging.info('Generate and Save the report as excel file')
        self.p['xlsfile']=lib.fm.ireports.save_as_xls(self.fm, self.p['report'])


    def _get_report_tbl(self):
        logging.info('Get the report generated table')
        self.p['tbl'] = lib.fm.ireports.get_tbl(self.fm, 'report_tbl', {})


    def _get_report_xls(self):
        '''
        . get the report on xls file and remove the 'conn'
          as well as the first line (titles)
        '''
        logging.info('Get the report from excel file')
        self.p['xls'] = lib.fm.ireports.read_report_xls(self.p['xlsfile'],
                                                             self.p['report']['report_cate'])


    def _compare_reports(self):
        '''
        for now, compare the 'mac' only
        '''
        logging.info('Compare the excel report with displayed')
        log_cfg(self.p['xls'], 'xls')
        log_cfg(self.p['tbl'], 'tbl')
        tbl = [r['mac'] for r in self.p['tbl']]
        xls = [r['mac'] for r in self.p['xls']]

        if not len(self.p['tbl']) and not len(self.p['xls']):
            self.errmsg = 'There was no item on this report'
            return

        not_in_tb = list(set(xls)- set(tbl))
        if not_in_tb:
            self.errmsg = 'These devices are not in testbed - %s' % not_in_tb
            return

        not_in_xls = list(set(tbl) - set(xls))
        if not_in_xls:
            self.errmsg = 'These devices are not xls - %s' % not_in_xls
            return
        self.passmsg = 'The save function works correctly'
        return


