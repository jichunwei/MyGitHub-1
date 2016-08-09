'''
West.li 2012.2.7
after backup the file,write the file path in the file 'upgrade_parameter_def.py',which is used to do upgrade test
'''

import logging
from RuckusAutoTest.models import Test
import os

class CB_ZD_Cmb_Write_File_Path_To_File(Test):

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        return ('PASS', 'skip this step currently')
        f=open(self.para_file,'r+')
        s_file=f.read()
        s_find="\'config_file\':\'"
        position = s_file.find(s_find)
        nn=0#'\n' number
        for i in range(0,position):
            if s_file[i]=='\n':
                nn+=1
        position += nn #need move twice if meet a '\n'
        position += len(s_find) 
        f.seek(position,0)
        self.cfg_file=self.cfg_file.replace('\\','\\\\')
        f.write(self.cfg_file)
        f.write("\'}")
        f.write(' '*100)
        f.close()
        if self.errmsg:
            return ('FAIL', self.errmsg)
        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        return
        self.conf = {'related_bak': 'unspecific',}
        self.conf.update(conf)
        self.cfg_file=self.carrierbag['bak_files'][self.conf['related_bak']]
        current_path=os.getcwd()
        self.para_file = os.path.join(current_path,'RuckusAutoTest\\tests\\zd\\lib\\upgrade_parameter_def.py')
        self.errmsg = ''
        self.passmsg = 'write path to file successfully'

