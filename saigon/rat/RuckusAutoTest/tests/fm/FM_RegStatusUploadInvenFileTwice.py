'''
This test script is used for test cases:
1.2.3.7    Upload a device inventory file twice by pre-registration data with same serial number
1.2.3.8    Upload a device inventory file twice by Manufacturing data with same serial number


Test Procedure:
1. Log in Flex Master as administrator
2. Navigate to Inventory > Device Registration
3. Click on "Upload a Device Inventory File"
4. Choose option for Manufacturing/Pre-Registration Data then browse to the file
   for the device list.
5. Click ok to upload the file the first time.
6. Make sure all devices in the file uploaded successfully.
7. Re-upload that file again.
8. Make sure FM shows an error message to inform those devices already exist in
   the database.

Pass/Fail/Error Criteria (including pass/fail messages):
+ Pass: if all of the verification steps in the test case are met.
+ Fail: if one of verification steps is failed.
+ Error: Other unexpected events happen.
'''
import os
import logging
import re
from pprint import pformat

from RuckusAutoTest.common.utils import log_trace
from RuckusAutoTest.tests.fm.lib_FM import init_coms
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common.excelwrapper import writeexcel

MANUFACT_MODE = 'manufact'
PREREG_MODE   = 'pre_regist'

EXPECTED_ERR_MSG_PAT = ".*successfully.*data.*exist.*"
EXPECTED_ERR_MSG = "The inventory file was imported successfully, " \
                    "but some data already exist on the database."

class FM_RegStatusUploadInvenFileTwice(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = None
        self._cfg_test_params(conf)

    def test(self):
        self._write_data_to_excel_file(self.p['upload_mode'])
        if self.errmsg: return ('FAIL', self.errmsg)

        self._upload_inventory_file_first()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._find_uploaded_devices()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._upload_inventory_file_second()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        self._remove_uploaded_devices()
        self.fm.logout()

    def _cfg_test_params(self, cfg):
        self.p = dict(
            data_matrix = [],
            upload_mode = MANUFACT_MODE, # 'manufact'|'prereg' manufacturing data
            no_devices = 2,
        )
        self.p.update(cfg)

        init_coms(self, dict(tb=self.testbed))

        # if data_matrix is empte, generate a new one
        if not self.p['data_matrix']:
            self.p['data_matrix'] = \
                self.fm.lib.dreg.generate_manufact_data(self.fm, self.p['no_devices'])\
                if self.p['upload_mode'] == MANUFACT_MODE else\
                self.fm.lib.dreg.generate_prereg_data(self.fm, self.p['no_devices'])

        self.p['file_path'] = os.getcwd() + '\\' + self.p['upload_mode'] + '_data_file.xls'

        logging.debug('Test Configs:\n%s' % pformat(self.p))

    def _write_data_to_excel_file(self, upload_mode):
        '''
        '''
        msg = writeexcel(self.p['file_path'], self.p['data_matrix'])
        if msg:
            logging.info('Created an inventory data file %s successfully' % self.p['file_path'])
        else:
            self._fill_error_msg('Fail to create inventory data file')

    def _upload_inventory_file_first(self):
        try:
            cfg = dict(upload_device_mode=self.p['upload_mode'], file_path=self.p['file_path'])
            # upload the first time
            msg = self.fm.lib.dreg.upload_inventory_file(self.fm, cfg)
            if msg:
                self._fill_error_msg('Fail to upload inventory the file first time. Detail: %s' % msg)
            else:
                logging.info('Uploaded inventory file the first time successfully')
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())

    def _find_uploaded_devices(self):
        try:
            serial_list, SERIAL_COL = [], 0
            # get serial_list from matrix data
            for r in self.p['data_matrix']:
                # the first column is serial
                serial_list.append(r[SERIAL_COL])

            for serial in serial_list:
                data, index = self.fm.lib.dreg.find_device_serial(self.fm, serial)
                if data:
                    logging.info('Found device with serial %s in Device Registration table' % serial)
                else:
                    self._fill_error_msg(
                        "Not found device with serial %s in Device Registration table" % serial)
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())

    def _upload_inventory_file_second(self):
        try:
            cfg = dict(upload_device_mode=self.p['upload_mode'], file_path=self.p['file_path'])
            # Do upload the second time
            msg = self.fm.lib.dreg.upload_inventory_file(self.fm, cfg)
            # Expect error message here.
            # if do twice, the function returns success, it means fail
            if msg and not re.search(EXPECTED_ERR_MSG_PAT, msg, re.I):
                self._fill_error_msg(
                    'Not found expected message. Expect: %s. Actual: %s' %
                    (EXPECTED_ERR_MSG, msg)
                )
            else:
                logging.info('Found expected error message: %s' % msg)
                self._fill_pass_msg()
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())

    def _remove_uploaded_devices(self):
        SERIAL_COL = 0
        for r in self.p['data_matrix']:
            try:
                self.fm.lib.dreg.remove_device(self.fm, r[SERIAL_COL])
                logging.info(
                    'Removed device with serial %s from Registration Status list'
                    % r[SERIAL_COL]
                )
            except Exception:
                log_trace()
                logging.info(
                    'Warning: Cannot remove device with serial %s from '
                    'Registration Status table' % r[SERIAL_COL]
                )

    def _fill_error_msg(self, errmsg):
        self.errmsg = 'The test upload "%s" data twice has error:" %s' % (self.p['upload_mode'], errmsg)
        logging.info(self.errmsg)

    def _fill_pass_msg(self):
        self.passmsg = 'The test upload "%s" data twice works correctly' % self.p['upload_mode']
        logging.info(self.passmsg)

if __name__ == "main":
    my_class = FM_RegStatusUploadInvenFileTwice()
    my_class.config(dict())