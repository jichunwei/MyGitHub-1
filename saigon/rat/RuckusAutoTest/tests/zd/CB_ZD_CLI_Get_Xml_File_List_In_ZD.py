'''
by West.li 2012.2.3
get xml file list in zd /etc/airespider/
'''

import logging
import string
from RuckusAutoTest.models import Test
from RuckusAutoTest.common.lib_List import list_minus_list
from RuckusAutoTest.common.sshclient import sshclient

class CB_ZD_CLI_Get_Xml_File_List_In_ZD(Test):
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        try:
            self.zdcli.do_shell_cmd('')
        except:
            self.zdcli.zdcli = sshclient(self.zdcli.ip_addr, self.zdcli.port,'admin','admin')
            self.zdcli.login()
            
        try:
            cmd = "ls %s |grep 'xml' |grep -v '.bak.'" % self.conf['dir']
            res = self.zdcli.do_shell_cmd(cmd)
            res = string.strip(res)
            self.xml_file_list = string.split(res)
            logging.info('get all xml list:%s' % self.xml_file_list )
            
            minus = list_minus_list(self.xml_file_list,self.used_file_list)
            logging.info('get no use xml list:%s' % minus)
            
            self.xml_file_list = list_minus_list(self.xml_file_list,minus)
            logging.info('get used xml list in zd:%s' % self.xml_file_list)
        except Exception, e:
            self.errmsg = 'get xml file list failed %s' % e.message
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        s_file = ''
        for file in self.xml_file_list:
            s_file += "%s," % file 
        self.passmsg = 'there are %d xml file exist,they are:%s' % (len(self.xml_file_list), s_file)
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)
    
    
    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = dict(
                         dir='/etc/airespider/'
                         )
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.carrierbag.has_key('active_zd_cli'):
            self.zdcli = self.carrierbag['active_zd_cli']
            
        if 'standby' in self.conf['build']:
            self.zdcli = self.carrierbag['standby_zd_cli']
        elif 'zd1' in self.conf['build']:
            self.zdcli = self.carrierbag['zdcli1']
        elif 'zd2' in self.conf['build']:
            self.zdcli = self.carrierbag['zdcli2']
            
        if conf.has_key('zdcli'):
            self.zdcli = self.carrierbag[conf['zdcli']]
            
        total_sync_file_list=['mgmtipacl-list.xml','mgmtipv6acl-list.xml','mesh-list.xml',
                               'acl-list.xml','policy-list.xml','policy6-list.xml',
                               'authsvr-list.xml','hotspot-list.xml','wlansvc-list.xml',
                               'wlangroup-list.xml','map-list.xml','apgroup-list.xml',
                               'ap-list.xml','dcert-list.xml','dpsk-list.xml',
                               'guest-list.xml','role-list.xml','user-list.xml',
                               'guestservice-list.xml']#201503 @ZJ ZF-12181
        part_sync_file_list=['system.xml']
        not_sync_file_list=['route-list.xml','route6-list.xml','license-list.xml']
        self.file_list_dict={'total_sync':total_sync_file_list,
                             'part_sync' :part_sync_file_list,
                             'not_sync'  :not_sync_file_list,
                             }
        self.used_file_list = self.file_list_dict['total_sync'] + self.file_list_dict['part_sync']+ self.file_list_dict['not_sync']
                
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']
            self.zdcli = self.carrierbag['active_zd_cli']
   
    def _update_carrier_bag(self):
        self.carrierbag['xmlfile-list'] = self.xml_file_list
        if self.conf.has_key('build'):
            if not self.carrierbag.has_key('xmlfile_list_dict'):
                self.carrierbag['xmlfile_list_dict'] = {}
            self.carrierbag['xmlfile_list_dict'][self.conf['build']] = self.xml_file_list
            
        
        
