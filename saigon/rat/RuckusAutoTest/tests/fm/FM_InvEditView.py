'''
1.2.1 Inventory > Manage Devices
   'Edit view' can change device's group search

config
. delete the view (if exists)
test
. create a view with a specific group search
. select and edit that view
. make some change and save it
. make sure all the search params can be changed
  and the list of device display correctly
clean up
. delete this view
'''

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.tests.fm.lib_FM import *
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib import dev_features as ft
from RuckusAutoTest.models import Test

fmft = ft.FM

testcase = 0
test_cfg = [
    dict(
        view=dict(
            device_cate=fmft.device_cate['aps'],
            attr1=fmft.attrs['ip'],
            op1=fmft.ops['starts_with'],
            value_txt1='192.168', # all local aps, unless there's a change
            view_name='local_aps', # must match with saved_view
            view_desc='local_aps',
        ),
        saved_view='local_aps',
        updated_view=dict(
            device_cate=fmft.device_cate['aps'],
            attr1=fmft.attrs['ip'],
            op1=fmft.ops['starts_with'],
            value_txt1='192.168',

            combine_lnk1='and',
            attr2=fmft.attrs['model'],
            op2=fmft.ops['equals'],
            value_cb2='ZF7942', # check this on tb before adding in
            #update_view_name='local_aps',
        ),
        model='ZF7942',
    ),
][testcase]


class FM_InvEditView(Test):
    def config(self, cfg):
        self.errmsg = self.passmsg = ''
        self._cfg_test_params(cfg)
        self._delete_views()


    def test(self):
        self._create_view()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._select_view()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._edit_view()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._select_view()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._get_device_tbl()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_device_list()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)


    def cleanup(self):
        self._delete_views()
        self.fm.logout()


    def _cfg_test_params(self, cfg):
        self.p = cfg
        #self.p = test_cfg
        init_coms(self,dict(tb=self.testbed,))
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _delete_views(self):
        logging.info('Delete views')
        lib.fm.view.delete_all_views(self.fm)


    def _create_view(self):
        logging.info('Create view: "%s"' % self.p['saved_view'])
        log_cfg(self.p['view'], 'view')
        lib.fm.idev._create_view(self.fm, self.p['view'])


    def _select_view(self):
        logging.info('Select view: "%s"' % self.p['saved_view'])
        lib.fm.idev.__set_view(self.fm, self.p['saved_view'])


    def _edit_view(self):
        '''
        . after selecting view, clicking on 'edit view'
        . and update the view config
        '''
        logging.info('Edit view: "%s"' % self.p['saved_view'])
        log_cfg(self.p['updated_view'], 'updated view')
        lib.fm.idev._edit_view(self.fm, self.p['updated_view'])


    def _get_device_tbl(self):
        logging.info('Get this devices of this view: "%s"' % self.p['saved_view'])
        tbl_cfg = dict(get='all')
        self.p['tbl'] = lib.fm.idev._get_tbl(self.fm, 'view_tbl', tbl_cfg)
        log_cfg(self.p['tbl'], 'view tbl')


    def _test_device_list(self):
        '''
        . get ips out of testbed/displayed table
        . check the size first
        . then make sure all the ips in testbed are in tbl
        '''
        logging.info('Check if listed devices match new search criteria')
        tb_ips = [ap.ip_addr for ap in self.tb.get_ap_by_model(self.p['model'])]
        tbl_ips = [r['ip'].split(':')[0] for r in self.p['tbl']]
        log_cfg(tb_ips, 'testbed IPs')
        log_cfg(tbl_ips, 'displayed IPs')

        if len(tb_ips) != len(tbl_ips):
            self.errmsg = 'The number of IPs in the displayed table is not match with testbed'
            return

        for i in tb_ips:
            if i not in tbl_ips:
                self.errmsg = 'This device (%s) is not found in displayed list' % i
                return
        self.passmsg = 'The updated view works correctly'
        return

