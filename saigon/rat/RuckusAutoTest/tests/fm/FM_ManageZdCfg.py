'''
NOTES:
This script is to obtain/edit a ZD config.

Hence, this test script is currently to test below test cases:
    1.1.9.8.1    Add ZD configuration to FM
    1.1.9.8.2    Editable Configuration file list

Test Procedure for 1.1.9.8.1:
    1. Log in FM as admin account
    2. Navigate to Configure > Manage ZD Configurations
    3. Click "Obtain New ZoneDirector Configuration" link and select a ZD to obtain
       a new cfg.
    4. Enter a description and save it
    5. Go to Configure > Manage ZD Configurations, make sure the new ZD cfg is present
       on this page.

Test Procedure for 1.1.9.8.2:
    1. Log in FM as admin account
    2. Navigate to Configure > Manage ZD Configurations
    3. Click "edit" link on the ZD cfg you want to edit it.
    4. Enter a new description and save it
    5. Go to Configure > Manage ZD Configurations, make sure the new ZD cfg is present
       on this page.

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

class FM_ManageZdCfg(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = None
        self._cfg_test_params(**conf)

    def test(self):
        self._obtain_zd_cfg()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._execute_test()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_result()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        logging.info('Cleaning up the test...')
        self._cleanup_test()
        self.fm.logout()

    def _cfg_test_params(self, **kwa):
        self.p = dict(
            zd_ip = '',
            test_type = 'add',
        )
        self.p.update(kwa)

        time_stamp = get_timestamp()

        init_coms(self, dict(tb=self.testbed, zd_ip=self.p['zd_ip']))
        # get zd serial
        self.zd.start()
        self.p['serial'] = self.zd.get_serial_number()
        self.zd.stop()

        # Add basic param to do test cfg upgrade for
        # Basic param 1: create a config param for cfg template
        self.p.update(
            new_cfg = dict(
                cfg_desc = 'zd_cfg_%s' % (time_stamp),
            ),
            new_match_expr = dict(
                internal_ip = self.p['zd_ip'],
                serial = self.p['serial']
            )
        )
        # update config for edit type
        # if self.p['test_type'] == 'edit':
        self.p.update(
            edit_cfg = dict(
                cfg_desc = 'zd_cfg_edit_%s' % (time_stamp),
            ),
            edit_match_expr = dict(
                cfg_desc = self.p['new_cfg']['cfg_desc'],
            )
        )

        logging.info('Test configs:\n%s' % pformat(self.p))

    def _obtain_zd_cfg(self):
        try:
            lib.fm.zd_cfg.obtain_zd_cfg(self.fm, self.p['new_match_expr'], self.p['new_cfg'])
            logging.info('Created a new ZD cfg "%s" successfully' % self.p['new_cfg']['cfg_desc'])
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())

    def _execute_test(self):
        ''''''
        cfg_test_fn = {
            'add': None, # no need to do more with "add" case
            'edit': self._edit_zd_cfg,
        }[self.p['test_type']]

        if cfg_test_fn: cfg_test_fn()

    def _edit_zd_cfg(self):
        '''
        Edit a ZD cfg
        '''
        try:
            lib.fm.zd_cfg.edit_zd_cfg(self.fm, self.p['edit_match_expr'], self.p['edit_cfg'])
            logging.info('Edited the ZD cfg from "%s" to "%s" successfully' %
                         (self.p['new_cfg']['cfg_desc'], self.p['edit_cfg']['cfg_desc']))
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())

    def _test_result(self):
        '''
        Test to make sure the ZD config added/edited successfully
        '''
        logging.info('Checking the result for the test "%s" ZD cfg' %
                     self.p['test_type'])

        test_result_fn, match_expr = {
            'add': (self._find_zd_cfg, dict(cfg_desc=self.p['new_cfg']['cfg_desc'])),
            'edit': (self._find_zd_cfg, dict(cfg_desc=self.p['edit_cfg']['cfg_desc'])),
        }[self.p['test_type']]

        if test_result_fn: test_result_fn(match_expr)

        if self.errmsg is None: self._fill_pass_msg()

    def _find_zd_cfg(self, match_expr):
        '''
        This function is to find out a zd cfg matches "match_expr"
        '''
        try:
            lib.fm.zd_cfg.find_zd_cfg(self.fm, match_expr, 'equal')
            logging.info('Found the ZD cfg matches the expression "%s"' % match_expr)
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())

    def _fill_error_msg(self, errmsg):
        self.errmsg = 'The test "%s" ZD cfg has error:" %s' % (self.p['test_type'], errmsg)
        logging.info(self.errmsg)

    def _fill_pass_msg(self):
        self.passmsg = 'The test "%s" ZD configuration works correctly' % self.p['test_type']
        logging.info(self.passmsg)

    def _cleanup_test(self):
        cleanup_fn, match_expr = {
            'add':  (self._delete_zd_cfg, dict(cfg_desc=self.p['new_cfg']['cfg_desc'])),
            'edit': (self._delete_zd_cfg,
                         dict(cfg_desc=self.p['edit_cfg']['cfg_desc'])\
                         if self.errmsg is None else \
                         dict(cfg_desc=self.p['new_cfg']['cfg_desc']) # in case the test failed
                    ),
        }[self.p['test_type']]

        if cleanup_fn: cleanup_fn(match_expr)

    def _delete_zd_cfg(self, match_expr):
        '''
        This function is to delete a zd cfg matches "match_expr"
        '''
        try:
            lib.fm.zd_cfg.delete_zd_cfg(self.fm, match_expr)
            logging.info('Found the ZD cfg matches the expression "%s"' % match_expr)
        except Exception, e:
            log_trace()
            logging.info('Warning: Cannot find out any zd cfg matches the expression "%s"' %
                         match_expr)

