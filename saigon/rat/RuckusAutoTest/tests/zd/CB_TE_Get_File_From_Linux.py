'''
Created on Nov 5, 2014
@author: chen.tao@odc-ruckuswireless.com
'''
import os
import re
import logging
from RuckusAutoTest.models import Test

class CB_TE_Get_File_From_Linux(Test):

    def config(self, conf):        
        self._initTestParameters(conf)
            
    def test(self):
        try:
            file_path = self.get_file_from_linux_server()
            if not file_path:
                self.errmsg = 'Failed to get file from linux server'
        except Exception, ex:
            self.errmsg = ex.message
        if not self.errmsg:
            return self.returnResult('PASS', 'Get file from linux server successfully.')
        else:
            return self.returnResult('FAIL', self.errmsg)
    def oncleanup(self):
        pass
        
    def _initTestParameters(self, conf):
        self.conf = {
                     'src_file_dir':'/home/lab/zd_sr_license',
                     'src_file_name':'',
                     }
        self.conf.update(conf)
        self.server_ip = self.conf.get('server_ip')
        if not self.server_ip:
            self.server = self.testbed.components['LinuxServer']
            self.server_ip = self.server.ip_addr
        else:
            self.server = None
        self.errmsg = ''
        self.passmsg = ''

    def get_file_from_linux_server(self):

        src_file_name = self.conf.get('src_file_name')
        src_file_dir  = self.conf.get('src_file_dir')
        if not src_file_name or not src_file_dir:
            raise Exception('No source file name or directory is given.')
        if not src_file_dir.endswith('/'):
            src_file_dir += '/'
        src_file_path = src_file_dir+src_file_name
        if self.server:
            file_exist = self.server.verify_file_exist(src_file_dir,src_file_name)
            if not file_exist:
                raise Exception('File %s does not exist in linux server.'%src_file_path)

        if not self.conf.get('dst_file_name'):
            dst_file_name = src_file_name

        dst_file_path = r"d:\%s"%dst_file_name

        if os.path.isfile(dst_file_path):
            os.remove(dst_file_path)

        cmd = 'pscp -pw lab4man1 root@%s:%s %s'%(self.server_ip,src_file_path,dst_file_path)
        os.system(cmd)
        if os.path.isfile(dst_file_path):
            logging.info('Get file from linux server successfully!')
            logging.info('Destination file is:'+dst_file_path)
            return dst_file_path
