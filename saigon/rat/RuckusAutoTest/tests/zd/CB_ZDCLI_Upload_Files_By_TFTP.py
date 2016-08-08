'''
Description:
Created on 2010-8-13
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging
import re
import time

from RuckusAutoTest.models import Test

class CB_ZDCLI_Upload_Files_By_TFTP(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):            
        for file in self.upload_file_list:
            file_loc = file['file_loc']
            file_name = file['file_name']
            self._upload(self.zdcli, file_loc, file_name, self.conf['tftpserver'])

        self.passmsg = 'upload file [%s] successfully' % self.upload_file_list
        self._update_carrier_bag()
        
        return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(tftpserver = '192.168.0.20',
                         upload_file_list = [dict(file_loc='/writable/etc/airespider',
                                                  file_name='user-list.xml'),])
        self.conf.update(conf)
        self.upload_file_list = self.conf['upload_file_list']
        self.tftpserver = self.conf['tftpserver']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _upload(self, zdcli, dir, filename, ipaddr, timeout=60, chmod=False):
        zdcli.do_cmd(zdcli.login_shell_key)    
        zdcli.do_cmd('cd %s' % dir, timeout=10)    
        time.sleep(2)
        logging.info('pwd=[%s]' % zdcli.do_cmd('pwd', timeout=10))
        zdcli.do_cmd('tftp -g -r %s %s' % (filename, ipaddr), timeout=timeout)
        t0 = time.time()
        while True :
            res = zdcli.do_cmd('ls', timeout=10)
            if re.findall('%s' % filename, res) :
                logging.info('upload file %s successfully!' % filename)
                if chmod :
                    zdcli.do_cmd('chmod 777 %s' % filename)
                break
            
            elif time.time() - t0 > 30 :
                raise Exception('upload file %s failure!' % filename)
            
            else:
                time.sleep(5)
                
        zdcli.re_login()        
    
