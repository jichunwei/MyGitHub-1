'''
2011.12.19
add a prefix to a file in ZD, and download the file
by West.li
'''
import logging
from RuckusAutoTest.components.lib.zdcli import download_file_from_zd_to_pc as downloadfile
from RuckusAutoTest.models import Test
from RuckusAutoTest.common.sshclient import sshclient

class CB_ZD_Download_File_From_Zd(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
        
        pass
        
    def test(self):
        try:
            self.zdcli.do_shell_cmd('')
        except:
            self.zdcli.zdcli = sshclient(self.zdcli.ip_addr, self.zdcli.port,'admin','admin')
            self.zdcli.login()
        succ_file=''
        not_exist_file=''
        failed_file=''    

        d_bak, file=downloadfile.download_file(self.zdcli,self.file_location_in_zd,self.file_list,self.tftp_svr_addr,self.prefix)

        if 0==d_bak:
            succ_file += '%s,' % self.file_list
        elif 2==d_bak:
            not_exist_file='%s,' % file
        elif 1==d_bak:
            failed_file='%s,' % file
        
        if failed_file:
            self.errmsg='file %s download failed' % failed_file
        elif not_exist_file:
            self.passmsg='file %s not exist,file %s downlad successfully' % (not_exist_file,succ_file)
        else:
            self.passmsg='file %s downlad successfully' % succ_file
            
        if self.errmsg:
            return 'FAIL',self.errmsg
        self.passmsg=self.passmsg+' from %s and add prefix \'%s\' in front of the file name' % (self.zdcli.ip_addr,self.prefix)   
        return 'PASS',self.passmsg
        
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.file_list=self.carrierbag['xmlfile-list']
        if self.carrierbag.has_key('base_build_version') and self.carrierbag.has_key('target_build_version'):
            self.prefix+='-%s-%s'%(self.carrierbag['base_build_version'],self.carrierbag['target_build_version'])
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf=conf
        if conf.has_key('zdcli'):
            self.zdcli=self.carrierbag[conf['zdcli']]
        elif conf.has_key('prefix') and 'standby' in conf['prefix']:
            self.zdcli = self.carrierbag['standby_zd_cli']
        elif conf.has_key('prefix') and 'zd1' in self.conf['prefix']:
            self.zdcli = self.carrierbag['zdcli1']
        elif conf.has_key('prefix') and 'zd2' in self.conf['prefix']:
            self.zdcli = self.carrierbag['zdcli2']
        else:
            self.zdcli=self.testbed.components['ZoneDirectorCLI']
        if conf.has_key('zdcli'):
            self.zdcli = self.carrierbag[conf['zdcli']]
        if conf.has_key('prefix'):
            self.prefix=conf['prefix']
        else:
            self.prefix='bak'
        self.tftp_svr_addr='192.168.0.10'
        self.file_location_in_zd='//etc//airespider//'
        self.errmsg=''
        self.passmsg=''
        
        