'''
    Check channel table consistency between ZD and AP.
'''
import logging
import os

from RuckusAutoTest.models import Test

linux_file_path = r'/home/kevin/yokohama9.6/check_channels/'
linux_tftp_path = r'/var/www/channel_power_check/'
local_file_path = 'C:\\tmp\\'
#1st file---country-list.xml
#2nd file---regdomain
#3rd file---countries

class CB_ZD_Check_Channel_Table(Test):
    
    def config(self, conf):
        self._init_test_params(conf)

    def test(self):
        #upload file from local to TFTP server path
        for file in self.conf['file_name_list']:
            res = os.system(r'tftp -i 192.168.0.252 PUT %s%s' % (local_file_path, file))
            if res != 0:
                self.errmsg = 'upload file[%s] from local to TFTP server failed' % file
                return 'FAIL',self.errmsg
            
            #'Transfer successful', move file from TFTP server path to program path
            self.server.cmd("mv -f %s%s %s" % (linux_tftp_path, file, linux_file_path))

        self.server.cmd("cd %s" % linux_file_path)
        self.server.cmd("chmod +x regdomain")

        data = self.server.cmd("sh check_channels.sh", return_as_list=False)
        if 'No mismatch found' not in data:
            self.errmsg += 'Mismach found while checking channel consistency'
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
