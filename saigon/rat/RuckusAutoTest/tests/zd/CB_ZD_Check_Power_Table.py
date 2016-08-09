'''
    Download HTTP URL file to TestEngine local disk.
'''
import logging
import os

from RuckusAutoTest.models import Test
from contrib.download import multi_threads_downloader as download_hlp

linux_file_path = r'/home/kevin/yokohama9.6/check_power/'
linux_tftp_path = r'/var/www/channel_power_check/'
local_file_path = 'C:\\tmp\\'
#1st file---country_matrix.xls
#2nd file---regdmn_chan.h

class CB_ZD_Check_Power_Table(Test):
    
    def config(self, conf):
        self._init_test_params(conf)

    def test(self):
        #upload file from local to TFTP server path
        for file in self.conf['file_name_list']:
            res = os.system(r'tftp -i 192.168.0.252 PUT %s%s' % (local_file_path, file))
            if res != 0:
                self.errmsg = 'upload file[%s] from local to TFTP server failed' % file
                return 'FAIL',self.errmsg

            #'Transfer successful'
            self.server.cmd("mv -f %s%s %s" % (linux_tftp_path, file, linux_file_path))

        self.server.cmd("cd %s" % linux_file_path)

        data = self.server.cmd("python check_powers.py", return_as_list=False)
        if '0 mismatch(es) found' not in data:
            self.errmsg += 'Mismach found while checking power consistency'
            logging.info(data)
        
        if self.errmsg:
            return 'FAIL',self.errmsg
        return "PASS", self.passmsg

    def cleanup(self):
        self._update_carrier_bag()

    def _retrive_carrier_bag(self):
        pass

    def _update_carrier_bag(self):
        pass

    def _init_test_params(self, conf):
        self.conf={'local_file_path': local_file_path}
        self.conf.update(conf)

        self.server = self.testbed.components['LinuxServer']

        self.errmsg = ''
        self.passmsg = ''
