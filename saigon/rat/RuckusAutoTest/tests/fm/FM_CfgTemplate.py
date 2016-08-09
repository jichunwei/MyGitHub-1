'''
NOTES:
This script is created with intention to replace all old test scripts of Configuration
Template test cases such as FM_CreateConfTemplate.py, FM_DeleteConfTemplate.py when
there is free time to do it.

Hence, this test script is currently support two below test cases:

1.1.9.1.6    Configuration Templates: Make sure exist template could be copy
1.1.9.1.7    Configuration Templates: Make sure exist template could be export to xls file

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

Copy template.
Config:
    1. get cfg
Test
    1. Create template
    2. Do copy
    3. Check to make sure the copy has the same cfg
Clean up:
    Delete the created and the copied templates

Export template:
Config:
    1. get cfg
Test:
    1. create the template
    2. Do export
    3. Check to make sure the export has the same cfg
Clean up:
    1. Delete the created templates
    2. Delete the export file
'''

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.fm.lib_FM import *
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.fm.config_mapper_fm_old import *

class FM_CfgTemplate(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = None
        self._cfg_test_params(**conf)
        #self._create_cfg_tmpl()

    def test(self):
        self._create_cfg_tmpl()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._cfg_test()
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
            template_model = 'ZF2925',
            input_cfg = {},
            test_type = 'copy'
        )
        self.p.update(kwa)
        self.p['template_model'] = self.p['template_model'].upper()
        self.p['template_name'] = 'Test_cfg_tmpl_%s_%s' % (self.p['template_model'], get_timestamp())

        cfg_fn = {
            'copy': self._cfg_test_params_for_copy,
            'export': None
        }[self.p['test_type']]

        if cfg_fn: cfg_fn()
        init_coms(self, dict(tb=self.testbed))
        logging.info('Test configs:\n%s' % pformat(self.p))

    def _cfg_test_params_for_copy(self):
        '''This  function is to add params to do copy cfg template'''
        self.p['template_copy_name'] = 'Copy_of_' + self.p['template_name']

    def _cfg_test_params_for_export(self):
        '''This  function is to add params to do export cfg template'''
        pass

    def _create_cfg_tmpl(self):
        try:
            lib.fm.cfg_tmpl.create_cfg_tmpl(
                self.fm,
                dict(
                    template_name=self.p['template_name'],
                    template_model=self.p['template_model'], options=self.p['input_cfg']
                )
            )
            logging.info('Created tempalte "%s" for model "%s" successfully' %\
                         (self.p['template_name'], self.p['template_model']))
        except Exception, e:
            log_trace()
            self.fill_error_msg(e.__str__())

    def _cfg_test(self):
        ''''''
        cfg_test_fn = {
            'copy': self._do_copy_cfg_tmpl,
            'export': self._do_export_cfg_tmpl,
        }[self.p['test_type']]

        cfg_test_fn()

    def _do_copy_cfg_tmpl(self):
        ''''''
        logging.info('Create a copy of the template %s' % self.p['template_name'])
        if lib.fm.cfg_tmpl.copy_cfg_tmpl(self.fm, self.p['template_name'],
                                            self.p['template_copy_name']):
            logging.info('Copied template %s to new one %s' % (self.p['template_name'], self.p['template_copy_name']))
            return
        self.fill_error_msg('Cannot create a copy of %s' % self.p['template_name'])

    def _do_export_cfg_tmpl(self):
        try:
            logging.info('Export the template %s to excel file' % self.p['template_name'])
            self.p['export_file'] = lib.fm.cfg_tmpl.export_cfg_tmpl(self.fm, self.p['template_name'])
            logging.info('The exported file is saved to: %s' % self.p['export_file'])
        except Exception, e:
            log_trace()
            self.fill_error_msg(e.__str__())

    def _test_result(self):
        '''
        Test to make sure tr069 authentication username/password from web ui and cli
        are consistent
        '''
        logging.info('Checking the result for the test "%s" configuration template' %
                     self.p['test_type'])

        test_result_fn = {
            'copy': self._test_result_copy_cfg_tmpl,
            'export': self._test_result_export_cfg_tmpl,
        }[self.p['test_type']]
        test_result_fn()

    def _test_result_copy_cfg_tmpl(self):
        try:
            lib.fm.cfg_tmpl.verify_cfg_tmpl(self.fm,
                dict(
                     template_name=self.p['template_copy_name'],
                     template_model=self.p['template_model'],
                     options=self.p['input_cfg']
                )
            )
            self.fill_pass_msg()
        except Exception, e:
            log_trace()
            self.fill_error_msg(e.__str__())

    def _test_result_export_cfg_tmpl(self):
        try:
            input_cfg = lib.fm.cfg_tmpl.get_cfg_tmpl_view(self.fm, self.p['template_name'])
            export_cfg = lib.fm.cfg_tmpl.read_exported_cfg_tmpl(self.p['export_file'], ignore_case=True)
            msg = compare_dict(input_cfg, export_cfg)
        except Exception, e:
            log_trace()
            msg = e.__str__()

        if msg:
            self.fill_error_msg(msg)
        else:
            self.fill_pass_msg()

    def fill_error_msg(self, errmsg):
        self.errmsg = {
            'copy': 'The test "copy" configuration template has error:" %s' % errmsg,
            'export': 'The test "export" configuration template has error:" %s' % errmsg,
        }[self.p['test_type']]
        logging.info(self.errmsg)

    def fill_pass_msg(self):
        self.passmsg = {
            'copy': 'The test "copy" configuration template works correctly',
            'export': 'The test "export" configuration template works correctly',
        }[self.p['test_type']]
        logging.info(self.passmsg)

    def _cleanup_test(self):
        cleanup_fn = {
            'copy': self._cleanup_copy_cfg_tmpl,
            'export': self._cleanup_export_cfg_tmpl,
        }[self.p['test_type']]
        cleanup_fn()

#    def _cleanup_copy_cfg_tmpl(self):
#        try:
#            msg = ''
#            if not lib.fm.cfg_tmpl.delete_cfg_tmpl(self.fm, self.p['template_name']):
#                logging.info('Warning: Cannot delete the template %s' % self.p['template_name'])
#
#            if not lib.fm.cfg_tmpl.delete_cfg_tmpl(self.fm, self.p['template_copy_name']):
#                logging.info('Warning: Cannot delete the template %s' % self.p['template_copy_name'])
#        except Exception, e:
#            log_trace()
#            logging.info('Warning: Error happens while cleanup the test. Error: %s' % e.__str__())

    def _cleanup_copy_cfg_tmpl(self):
        try:
            if not lib.fm.cfg_tmpl.delete_cfg_tmpl(self.fm, self.p['template_name']):
                logging.info('Warning: Cannot delete the template %s' % self.p['template_name'])

            if not lib.fm.cfg_tmpl.delete_cfg_tmpl(self.fm, self.p['template_copy_name']):
                logging.info('Warning: Cannot delete the template %s' % self.p['template_copy_name'])
        except Exception, e:
            log_trace()
            logging.info('Warning: Error happens while cleanup the test %s. Error: %s' %
                         (self.p['test_type'], e.__str__()))

    def _cleanup_export_cfg_tmpl(self):
        try:
            if not lib.fm.cfg_tmpl.delete_cfg_tmpl(self.fm, self.p['template_name']):
                logging.info('Warning: Cannot delete the template %s' % self.p['template_name'])
            remove_file(self.p['export_file'])
        except Exception, e:
            log_trace()
            logging.info('Warning: Error happens while cleanup the test %s. Error: %s' %
                         (self.p['test_type'], e.__str__()))
