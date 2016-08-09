"""
Description: rename the file in linux PC
by west
"""

from RuckusAutoTest.models import Test
import logging


class CB_ZD_Rename_File_On_Linux_Server(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        logging.info("rename file [%s] to [%s]" %(self.conf['src_name'],self.conf['dst_name']))
        if not self.pc.rename_file(src_name=self.conf['src_name'],dst_name=self.conf['dst_name'],folder=self.conf['folder']):
            return self.returnResult("FAIL", self.errmsg) 
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'src_name':'',
                     'dst_name':'users',
                     'folder':'/etc/raddb'}
        self.conf.update(conf)
        self.pc = self.testbed.components['LinuxServer']

        self.pc.re_init()
        logging.info('Telnet to the server at IP address %s successfully' % \
                     self.pc.ip_addr)
        self.passmsg = "rename file [%s] to [%s] successfully" %(self.conf['src_name'],self.conf['dst_name'])
        self.errmsg = 'some error occur during rename file [%s] to [%s]'%(self.conf['src_name'],self.conf['dst_name'])
