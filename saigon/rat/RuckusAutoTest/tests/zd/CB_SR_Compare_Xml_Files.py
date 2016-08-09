'''
this file is draft to compare xml files in two zds
by West.li
'''
import logging
from RuckusAutoTest.components.lib.zdcli import compare_file as cmpf
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import compare_xml_file_on_pc as com_pc_xml
from RuckusAutoTest.common.sshclient import sshclient

class CB_SR_Compare_Xml_Files(Test):
    def config(self, conf):
        self._retrive_carrier_bag()
        self._init_test_params(conf)
        
        pass
        
    def test(self):
        try:
            self.zdcli1.do_shell_cmd('')
        except:
            self.zdcli1.zdcli = sshclient(self.zdcli1.ip_addr, self.zdcli1.port,'admin','admin')
            self.zdcli1.login()
        try:
            self.zdcli2.do_shell_cmd('')
        except:
            self.zdcli2.zdcli = sshclient(self.zdcli2.ip_addr, self.zdcli2.port,'admin','admin')
            self.zdcli2.login()
            
        for filename in self.file_list:
            result,msg = cmpf.compare_file(self.zdcli1, self.zdcli2, self.zd_dir, self.zd_dir, filename, self.pc_dir, self.action )
            logging.info("result:%s, msg:%s, file:%s, source:%s, target:%s" % (result, msg, filename, self.zdcli1.ip_addr, self.zdcli2.ip_addr))
            if result:
#                self.passmsg += (msg+'(two zd after sync),')
                pass
            else:
                self.errmsg += (msg+'(two zd after sync),')
            
            #compare source side xml file is the same to the file before sync
            #if the file 'xxx.xml' is baked,the baked file is named 'bak-xxx.xml'
            if result:
                if self.conf.has_key('bakfile') and (self.conf['bakfile']=='Y'):
                    if not(filename in self.not_bak_file_list):
                        bak_filename=self.bak_prefix+'-'+filename
                        source_filename='source-'+filename
                        result_pc,msg_pc = com_pc_xml.compare_xml_file_on_pc(self.conf['pc_dir'],bak_filename, self.conf['pc_dir'], source_filename,filename+'bak')
                        logging.info("result_pc:%s, msg_pc:%s, file:%s, source:%s" % (result_pc, msg_pc, filename, self.zdcli1.ip_addr))
                        if result_pc:
#                            self.passmsg += (msg_pc+'(source side with file backup before sr enabled),')
                            pass
                        else:
                            self.errmsg += (msg_pc+'(source side with file backup before sr enabled),')
                
        if self.errmsg:
            return 'FAIL',self.errmsg
        return 'PASS',self.passmsg
        
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.file_list=self.carrierbag['xmlfile-list']
        if self.carrierbag.has_key('bakfile_prefix'):
            self.bak_prefix = self.carrierbag['bakfile_prefix']
        else:
            self.bak_prefix = 'bak'
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.errmsg=''
        self.passmsg=''
        self.conf = dict(
               zd_dir = '//etc//airespider//',
               pc_dir = 'D://compareXml//',
               action = 'Mod'
               )
        self.conf.update(conf)
        
        self.not_bak_file_list=['ap-list.xml',]
        
        if self.conf.has_key('zdcli1') and self.conf.has_key('zdcli2'):
            self.zdcli1 = self.carrierbag[conf['zdcli1']]
            self.zdcli2 = self.carrierbag[conf['zdcli2']]
        else:
            self.zdcli1 = self.testbed.components['ZDCLI1']
            self.zdcli2 = self.testbed.components['ZDCLI2']
            
        self.zd_dir = self.conf['zd_dir']
        self.pc_dir = self.conf['pc_dir']
        self.action = self.conf['action']
        
        