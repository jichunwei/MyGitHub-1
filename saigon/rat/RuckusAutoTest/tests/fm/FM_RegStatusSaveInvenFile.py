'''
This test script is used for test cases:
    + 1.1.7.2.5: Upload a device inventory file by Manufacturing data

Test Procedure:
1. Log in Flex Master as administrator
2. Navigate to Inventory > Device Registration
3. Get list of device serials, their inventory statuses
4. Click on "Save This Inventory as XLS"
5. Save the file in local disk
6. Verify that all devices in Inventory table are the same with devices in xls file
7. Delete file in local disk
8. Log out Flex Master

Pass/Fail/Error Criteria (including pass/fail messages):
+ Pass: if all of the verification steps in the test case are met.
+ Fail: if one of verification steps is failed.
+ Error: Other unexpected events happen.

Config:
    1. get cfg
    2. Get current serials and statuses
Test:
    1. Save Inventory file in local disk
    2. Check to make sure devices in Inventory table are the same with devices in xls file
Clean up:
    1. Delete xls file in local disk
'''
import os
import logging
from pprint import pformat

from RuckusAutoTest.common.utils import log_trace
from RuckusAutoTest.tests.fm.lib_FM import init_coms

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common.excelwrapper import readexcel


class FM_RegStatusSaveInvenFile(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = ''
        self._cfg_test_params(conf)

        self._get_current_status()
        if self.errmsg: return ('FAIL', self.errmsg)


    def test(self):
        self._save_inventory_file()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._verify_devices_in_xls_file()
        if self.errmsg: return ('FAIL', self.errmsg)
        self.passmsg = 'Save inventory file successful'
        return ('PASS', self.passmsg)


    def cleanup(self):

        self.fm.logout()


    def _cfg_test_params(self, cfg):
        self.p = dict(
            file_name = 'inventory.xls'
        )
        self.p.update(cfg)
        file_path = os.path.join(os.path.expanduser('~'), r"Desktop\%s" % self.p['file_name'])
        self.p['file_path'] = file_path

        init_coms(
            self,
            dict(tb=self.testbed),
        )
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _save_inventory_file(self):
        try:
            self.fm.lib.dreg.save_inventory_file(self.fm, self.p['file_name'])
        except Exception, e:
            log_trace()
            self.fill_error_msg(e.__str__())

    def _get_list_serials_from_excel(self):
        try:
#            import xlrd
#            work_book = xlrd.open_workbook(self.p['file_path'])
#            first_sheet = work_book.sheet_by_index(0)
#            list_serials = first_sheet.col_values(1)
#            del list_serials[0]

            obj_excel = readexcel(self.p['file_path'])
            list_serials = obj_excel.getColumn(column=1)
            return list_serials

        except Exception, e:
            log_trace()
            self.fill_error_msg(e.__str__())


    def _get_dict_serials_models_from_excel(self):
        try:
#            import xlrd
#            work_book = xlrd.open_workbook(self.p['file_path'])
#            first_sheet = work_book.sheet_by_index(0)
#            list_serials = first_sheet.col_values(1)
#            del list_serials[0]
#            list_models = first_sheet.col_values(2)
#            del list_models[0]
            obj_excel = readexcel(self.p['file_path'])
            list_serials = obj_excel.getColumn(column=1)
            list_models = obj_excel.getColumn(column=2)
            result = {}
            for i in range(len(list_serials)):
                serial_str = str(list_serials[i])
                if '.' in serial_str:
                    serial_str = serial_str[:len(serial_str) - 2]
                result[serial_str] = list_models[i]
            return result

        except Exception, e:
            log_trace()
            self.fill_error_msg(e.__str__())


    def _verify_devices_in_xls_file(self):
        try:
            dict_serials_models = self._get_dict_serials_models_from_excel()

            for serial in dict_serials_models:
                data, index = self.fm.lib.dreg.find_device_serial(self.fm, serial)
                if not data:
                    self.fill_error_msg("Device with serial %s don't have in Device Registration table"
                                  % serial)
                # check model
                if data['model'] != dict_serials_models[serial]:
                    self.fill_error_msg("Device with serial %s have model %s, expected %s"
                                  % (serial, data['model'], dict_serials_models[serial]))
        except Exception, e:
            log_trace()
            self.fill_error_msg(e.__str__())


    def _get_current_status(self):
        try:
            serials_statuses = self.fm.lib.dreg.get_device_serials_and_status(self.fm)
            self.p.update(serials_statuses)

            list_licenses = self.fm.lib.dreg.get_licenses_info(self.fm)
            self.p.update(list_licenses)
        except Exception, e:
            log_trace()
            self.fill_error_msg(e.__str__())


    def _delete_xls_file(self):
        if os.path.isfile(self.p['file_path']):
            os.remove(self.p['file_path'])


    def fill_error_msg(self, errmsg):
        self.errmsg = 'Error: %s\n' % errmsg
        logging.info(self.errmsg)
