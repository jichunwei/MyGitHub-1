'''
this file is draft to compare xml files in two pcs
by West.li
'''
import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import compare_xml_file_on_pc as com_pc_xml
from RuckusAutoTest.common.lib_List import list_minus_list

class CB_ZD_Compare_Xml_Files_On_Pc(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
        
        pass
        
    def test(self):
        res=list_minus_list(self.base_file_list,self.target_file_list)
        if res:
            s_file_list=''
            for s in res:
                s_file_list+=(s+'//')
            self.errmsg += ('basebuid has more xml files then target:%s' % s_file_list)
        self.file_list=list_minus_list(self.base_file_list,res)
        not_cmp_list = self.conf.get('not_cmp_file')
        if not_cmp_list:
            for file_name in not_cmp_list:
                try:
                    self.file_list.remove(file_name)
                except:
                    pass
            
        for filename in self.file_list:
            base_filename=self.conf['prefix1']+'-'+filename
            target_filename=self.conf['prefix2']+'-'+filename
            if self.conf['scenario']=='upgrade':
                part_sync_file={'ap-list.xml':()}
            if self.conf['scenario']=='upgrade_and_sr':
                part_sync_file={'ap-list.xml':(),
                                'system.xml':("identity","mgmt-ip","mgmt-vlan","dhcps","cluster",
                                                         "realtime-monitor","time","portlet-pref","remote-access"),
                                'license-list.xml':("license-list",),
                                }
            if self.conf['scenario']=='sr':
                part_sync_file={'system.xml':("identity","mgmt-ip","mgmt-vlan","dhcps","cluster",
                                                         "realtime-monitor","time","portlet-pref","remote-access"),
                                'license-list.xml':("license-list",),
                                }
            result_pc,msg_pc = com_pc_xml.compare_xml_file_on_pc(self.conf['pc_dir'],base_filename, 
                                                                 self.conf['pc_dir'], target_filename,
                                                                 filename,part_sync_file=part_sync_file)
            if result_pc:
                self.passmsg += (msg_pc+',')
            else:
                self.errmsg += (msg_pc+',')
                
        if self.errmsg:
            return 'FAIL',self.errmsg
        return 'PASS',self.passmsg
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.base_file_list=self.carrierbag['xmlfile_list_dict'][self.conf['prefix1']]
        self.target_file_list=self.carrierbag['xmlfile_list_dict'][self.conf['prefix2']]
        
        not_sync_file_list=['route-list.xml','route6-list.xml']
        if self.conf['scenario']=='upgrade_and_sr' or self.conf['scenario']=='sr':
            self.base_file_list = list_minus_list(self.base_file_list,not_sync_file_list)
            self.target_file_list = list_minus_list(self.target_file_list,not_sync_file_list)
    
        if self.carrierbag.has_key('base_build_version') and self.carrierbag.has_key('target_build_version'):
            self.conf['prefix1']+='-%s-%s'%(self.carrierbag['base_build_version'],self.carrierbag['target_build_version'])
            self.conf['prefix2']+='-%s-%s'%(self.carrierbag['base_build_version'],self.carrierbag['target_build_version'])
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.errmsg=''
        self.passmsg=''
        self.conf = dict(
               zd_dir = '//etc//airespider//',
               pc_dir = 'D://compareXml//',
               action = 'Mod',
               prefix1='base',
               prefix2='target',
               scenario='sr' #upgrade,SR,upgrade_and_sr
               )
        self.conf.update(conf)
        
        self.not_bak_file_list=['ap-list.xml',]
            
        self.pc_dir = self.conf['pc_dir']
        self.action = self.conf['action']
        
        
        
