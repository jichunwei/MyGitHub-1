'''
This test script is used for test cases:
    + 1.1.7.2.5: Upload a device inventory file by Manufacturing data

Test Procedure:
1. Log in Flex Master as administrator
2. Navigate to Inventory > Device Registration
3. Get list of device serials, their inventory statuses
4. Click on "Upload a Device Inventory File"
5. Choose option for Manufacturing Data then browse to the file for the device list.
6. Click ok to upload the file.
7. Verify that new devices are contained in table Device Registration
5. Log out Flex Master

Pass/Fail/Error Criteria (including pass/fail messages):
+ Pass: if all of the verification steps in the test case are met.
+ Fail: if one of verification steps is failed.
+ Error: Other unexpected events happen.

Config:
    1. get cfg
    2. Get current serials and statuses
Test:
    1. Upload Inventory File
    2. Check to make sure new devices are contained in table Device Registration.
Clean up:
    Don't know how to delete registered device in table Device Registration
'''


from RuckusAutoTest.common.utils import *
from RuckusAutoTest.tests.fm.lib_FM import *
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common.excelwrapper import readexcel, writeexcel


class FM_RegStatusUploadInvenFile(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = ''
        self._cfg_test_params(conf)

        self._get_current_status()
        if self.errmsg: return ('FAIL', self.errmsg)


    def test(self):
        self._write_data_to_excel_file()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._upload_inventory_file()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._verify_registered_device()
        if self.errmsg: return ('FAIL', self.errmsg)
        self.passmsg = 'Upload inventory file with mode %s successful' % self.p['mode']
        return ('PASS', self.passmsg)


    def cleanup(self):
        self.fm.logout()


    def _cfg_test_params(self, cfg):
        '''
        - data_matrix for pre_regist mode:
            [
                ['serial number 1', 'its tag'], # line 1
                ['serial number 2', 'its tag'], # line 2
                ....
            ]
        - data_matrix for manufact mode:
            [
                ['serial number 1', 'model', 'number', 'special string'], # line 1
                ['serial number 1', 'model', 'number', 'special string'], # line 2
                ....
            ]
        '''
        self.p = dict(
            file_path = '',
            data_matrix = [],
            mode = 'manufact',
            no_devices = 3,
        )
        self.p.update(cfg)
        self.p['file_path'] = os.getcwd() + '\\' + self.p['mode'] + '_data_file.xls'

        init_coms(self, dict(tb=self.testbed))
        if not self.p['data_matrix']:
            self.p['data_matrix'] = \
                self.fm.lib.dreg.generate_manufact_data(self.fm, self.p['no_devices'])

        logging.info('Test Configs:\n%s' % pformat(self.p))


    def _upload_inventory_file(self):
        try:
            cfg = dict(upload_device_mode=self.p['mode'], file_path=self.p['file_path'])
            self.fm.lib.dreg.upload_inventory_file(self.fm, cfg)
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())

    def _write_data_to_excel_file(self):
        '''
        '''
        msg = writeexcel(self.p['file_path'], self.p['data_matrix'])
        if msg:
            logging.info('Created an inventory data file %s successfully' % self.p['file_path'])
        else:
            self._fill_error_msg('Fail to create inventory data file')

    def _get_list_serials_from_excel(self):
        try:
#            import xlrd
#            work_book = xlrd.open_workbook(self.p['file_path'])
#            first_sheet = work_book.sheet_by_index(0)
#            list_serials = first_sheet.col_values(0)
            obj_excel = readexcel(self.p['file_path'], True)
            list_serials = obj_excel.getColumn(True)
            return list_serials
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())


    def _get_dict_serials_models_from_excel(self):
        try:
#            import xlrd
#            work_book = xlrd.open_workbook(self.p['file_path'])
#            first_sheet = work_book.sheet_by_index(0)
#            list_serials = first_sheet.col_values(0)
#            list_models = first_sheet.col_values(1)
            obj_excel = readexcel(self.p['file_path'], True)
            list_serials = obj_excel.getColumn(True)
            list_models = obj_excel.getColumn(True, column=1)
            result = {}
            for i in range(len(list_serials)):
                result[list_serials[i]] = list_models[i]
            return result
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())


    def _verify_registered_device(self):
        try:
            #list_serials = self._get_list_serials_from_excel()
            dict_serials_models = self._get_dict_serials_models_from_excel()
            for serial in dict_serials_models :
                data, index = self.fm.lib.dreg.find_device_serial(self.fm, serial)
                if not data:
                    self._fill_error_msg("Not found device with serial %s in Device Registration table"
                                  % serial)
                    return
                # check model
                if data['model'] != dict_serials_models[serial]:
                    self._fill_error_msg("Device with serial %s has model %s, expected %s"
                                  % (serial, data['model'], dict_serials_models[serial]))
                    return

                logging.info(
                    'Found device serial %s with model %s in Device Registration table' %
                    (serial, data['model'])
                )
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())


    def _get_current_status(self):
        try:
            serials_statuses = self.fm.lib.dreg.get_device_serials_and_status(self.fm)
            self.p.update(serials_statuses)

            dict_licenses_info = self.fm.lib.dreg.get_licenses_info(self.fm)
            self.p.update(dict_licenses_info)
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())


    def _fill_error_msg(self, errmsg):
        self.errmsg = 'Error: %s\n' % errmsg
        logging.info(self.errmsg)


if __name__ == "main":
    my_class = FM_RegStatusUploadInvenFile()
    my_class.config(dict())