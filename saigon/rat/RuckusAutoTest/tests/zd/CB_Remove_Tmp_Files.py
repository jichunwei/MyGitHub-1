'''
Created on 2011-6-14

@author: serena.tan@ruckuswireless.com

Decription: 

'''


import os
import logging

from RuckusAutoTest.models import Test


class CB_Remove_Tmp_Files(Test):
        
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._removeTmpFiles()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.filename_list = conf['filename_list']
        self.errmsg = ''
        self.passmsg = ''

    def _removeTmpFiles(self):
        try:
            logging.info('Remove files: %s' % self.filename_list)
            for file in self.filename_list:
                if os.path.exists(file):
                    os.remove(file)
                    
            self.passmsg = "Remove files%s successfully" % self.filename_list
            
        except Exception, e:
            self.errmsg = e.message
            
