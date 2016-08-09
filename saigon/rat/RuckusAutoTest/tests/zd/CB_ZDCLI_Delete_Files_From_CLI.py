'''
Description:Delete files from CLI at shell mode so that quick clean configuration,
for example: delete user-list.xml.

Created on 2010-8-13
@author: cwang@ruckuswireless.com
'''
import logging
import re
import time

from RuckusAutoTest.models import Test

class CB_ZDCLI_Delete_Files_From_CLI(Test):
    '''
    Delete files from CLI at shell mode, for example, user-list.xml.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):            
        for file in self.delete_file_list:
            file_loc = file['file_loc']
            file_name = file['file_name']
            self._delete(self.zdcli, file_loc, file_name)

        self.passmsg = 'Delete file [%s] successfully' % self.delete_file_list
        self._update_carrier_bag()
        
        return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(delete_file_list = [dict(file_loc='/writable/etc/airespider',
		file_name='user-list.xml'),])
        self.conf.update(conf)
        self.delete_file_list = self.conf['delete_file_list']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _delete(self, zdcli, dir, filename, timeout=60):
        zdcli.do_cmd(zdcli.login_shell_key)    
        zdcli.do_cmd('cd %s' % dir, timeout=10)    
        time.sleep(2)
        logging.info('pwd=[%s]' % zdcli.do_cmd('pwd', timeout=10))
	logging.info('Try to delete file [%s]' % filename)
        zdcli.do_cmd('rm %s' % filename, timeout=timeout)
        t0 = time.time()
        while True :
            res = zdcli.do_cmd('ls', timeout=10)
            if not re.findall('%s' % filename, res) :
                logging.info('Delete file %s successfully!' % filename)
		break
            elif time.time() - t0 > 30 :
                raise Exception('Delete file %s failure!' % filename)
            
            else:
                time.sleep(5)
                
        zdcli.re_login()     
    
