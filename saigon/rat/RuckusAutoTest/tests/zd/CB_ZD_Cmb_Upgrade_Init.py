'''
by west.li 2012.02.06
read information from upgrade_parameter and put them in the carrierbag
'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd.lib import upgrade_parameter_def
import logging
import os

class CB_ZD_Cmb_Upgrade_Init(Test):
    
    def config(self, conf):
        reload(upgrade_parameter_def)
        self.upgrade_parameter=upgrade_parameter_def.upgrade_parameter
        self._init_test_params(conf)

    def test(self):
        index=self.upgrade_parameter['upgrade_index']
        if index+1>len(self.upgrade_parameter['upgrade_test_list']):
            return 'FAIL','index out of range(%d>%d)' % (index+1,len(self.upgrade_parameter['upgrade_test_list']))
        self.upgrade_parameter_this_round = self.upgrade_parameter['upgrade_test_list'][index]
        
        build_stream=self.upgrade_parameter_this_round['base_build_stream'].split('_')[1]
        self.base_build_version=build_stream+'.'+self.upgrade_parameter_this_round['base_build_no']
        
        build_stream=self.upgrade_parameter_this_round['target_build_stream'].split('_')[1]
        self.target_build_version=build_stream+'.'+self.upgrade_parameter_this_round['target_build_no']
        need_update_index=False
        if self.upgrade_parameter_this_round['number_of_test_suite']==self.upgrade_parameter_this_round['test_suite_index']:
            logging.info('this is the last stream of the upgrade')
            new_test_suite_index=1
            need_update_index=True
            if index+1 == len(self.upgrade_parameter['upgrade_test_list']):
                new_index=0
            else:
                new_index=index+1
        else:
            logging.info('this is not the last suite of the upgrade number_of_test_suite:%d,test_suite_index:%d' % (self.upgrade_parameter_this_round['number_of_test_suite'],self.upgrade_parameter_this_round['test_suite_index']))
            new_test_suite_index=self.upgrade_parameter_this_round['test_suite_index']+1
        #modify the the test_suite_index and upgrade_index in file upgrade_parameter_def.py
        f=open(self.para_file,'r+')
        s_file=f.read()
        position=-1
        for find_time in range(1,index+2):
            s_find="\'test_suite_index\':"
            position = s_file.find(s_find,position+len(s_find))
        nn=0#'\n' number
        for i in range(0,position):
            if s_file[i]=='\n':
                nn+=1
        position += nn #need move twice if meet a '\n'
        position += len(s_find) 
        f.seek(position,0)
        f.write(str(new_test_suite_index))
        f.write(",")
        if need_update_index:
            s_find="\'upgrade_index\':"
            position = s_file.find(s_find)
            nn=0#'\n' number
            for i in range(0,position):
                if s_file[i]=='\n':
                    nn+=1
            position += nn #need move twice if meet a '\n'
            position += len(s_find) 
            f.seek(position,0)
            f.write(str(new_index))
            f.write(",}")
            f.write(' '*100)
        f.close()
        
        self._update_carrier_bag()
        if self.errmsg:
            return 'FAIL',self.errmsg
        return "PASS", self.passmsg

    def cleanup(self):
        pass

    def _retrive_carrier_bag(self):
        pass

    def _update_carrier_bag(self):
        self.carrierbag['base_build_stream']    = self.upgrade_parameter_this_round['base_build_stream']
        self.carrierbag['base_build_no']        = self.upgrade_parameter_this_round['base_build_no']
        self.carrierbag['target_build_stream']  = self.upgrade_parameter_this_round['target_build_stream']
        self.carrierbag['target_build_no']      = self.upgrade_parameter_this_round['target_build_no']
        self.carrierbag['restore_file_path']    = self.upgrade_parameter_this_round['config_file']
        if self.upgrade_parameter_this_round.has_key('base_build_file'):
            self.carrierbag['base_build_file']      = self.upgrade_parameter_this_round['base_build_file']
        if self.upgrade_parameter_this_round.has_key('target_build_file'):
            self.carrierbag['target_build_file']    = self.upgrade_parameter_this_round['target_build_file']
        if self.upgrade_parameter_this_round.has_key('skip_download'):
            self.carrierbag['skip_download']        = self.upgrade_parameter_this_round['skip_download']
        if self.upgrade_parameter_this_round.has_key('upgrade_keep'):
            self.carrierbag['upgrade_keep']        = self.upgrade_parameter_this_round['upgrade_keep']
            
#Chico, 2014-8-14, ZF-9675 sync upgrade codes from P4          
#        if self.upgrade_parameter_this_round.has_key('base_simap_version'):
#            self.carrierbag['base_simap_version']= self.upgrade_parameter_this_round['base_simap_version']
#        if self.upgrade_parameter_this_round.has_key('target_simap_version'):
#            self.carrierbag['target_simap_version']= self.upgrade_parameter_this_round['target_simap_version']
#        if self.upgrade_parameter_this_round.has_key('base_simap_file'):
#            self.carrierbag['base_simap_file']= self.upgrade_parameter_this_round['base_simap_file']
#        if self.upgrade_parameter_this_round.has_key('target_simap_file'):
#            self.carrierbag['target_simap_file']= self.upgrade_parameter_this_round['target_simap_file']
#        if self.upgrade_parameter_this_round.has_key('tftp_dir'):
#            self.carrierbag['tftp_dir']= self.upgrade_parameter_this_round['tftp_dir']
#        if self.upgrade_parameter_this_round.has_key('tftp_server'):
#            self.carrierbag['tftp_server']= self.upgrade_parameter_this_round['tftp_server']
#        else: 
#            self.carrierbag['tftp_server'] = '192.168.0.10'
#        if self.upgrade_parameter_this_round.has_key('skip_packet_sim_ap'):
#            self.carrierbag['skip_packet_sim_ap']= self.upgrade_parameter_this_round['skip_packet_sim_ap']
#Chico, 2014-8-14, ZF-9675 sync upgrade codes from P4   
           
        self.carrierbag['remove_img_after_test']= self.upgrade_parameter['remove_img_after_test']
        self.carrierbag['base_build_version']   = self.base_build_version
        self.carrierbag['target_build_version'] = self.target_build_version
        
        self.carrierbag['sw'] = self.testbed.components['L3Switch']

    def _init_test_params(self, conf):
        self.conf={}
        self.conf.update(conf)
        current_path=os.getcwd()
        self.para_file = os.path.join(current_path,'RuckusAutoTest\\tests\\zd\\lib\\upgrade_parameter_def.py')
        self.errmsg = ''
        self.passmsg = 'read parameter successfully'
        
