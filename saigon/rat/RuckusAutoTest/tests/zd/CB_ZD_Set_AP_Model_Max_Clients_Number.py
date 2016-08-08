import logging
from random import randint

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.zd import ap_group
from RuckusAutoTest.components.lib.zdcli import configure_ap_group as apgcli
from RuckusAutoTest.common.lib_Constant import model_max_clients_mapping as model_max_client
from RuckusAutoTest.common import lib_Constant as const

class CB_ZD_Set_AP_Model_Max_Clients_Number(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        logging.info('set model max clients number in web UI')
        ap_group.set_multi_ap_model_max_client_by_name(self.zd, self.conf['grp_name'], self.model_client_number_cfg)
        
        logging.info('get model max clients number in CLI')
        self.get_cfg=apgcli.get_all_model_max_client_number(self.zdcli, self.conf['grp_name'])
        
        for model in self.model_client_number_cfg:
            if model not in self.get_cfg:
                self.errmsg+='model %s number not get from cli,'%model
            elif int(self.model_client_number_cfg[model])!=int(self.get_cfg[model]):
                self.errmsg+='model %s number not match web set %s cli get %s,'%(model,self.model_client_number_cfg[model],self.get_cfg[model])
        if self.errmsg:
            return self.returnResult('FAIL',self.errmsg)
        return self.returnResult('PASS', "set max clients number in web successfully and verify in cli ok")
    
    def cleanup(self):
        pass

    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf={'grp_name':'System Default',
                   'set_type':'Max',#Max/Min/Random/Lower/Higher
                   }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        #update model_max_client
        version = self.zdcli.get_version()
        if const.zd_ver_ap_model_mapping.has_key(version):
            exclude_ap_models = const.zd_ver_ap_model_mapping[version]
            for model in exclude_ap_models:
                if model_max_client.has_key(model):
                    model_max_client.pop(model)  
        
        self.model_client_number_cfg,self.model_list=self._get_max_client_number_be_set(self.conf['set_type'].title())
        if self.conf['set_type'].title() in ['Max','Min','Random']:
            self.update_carribag=True
        else:
            self.update_carribag=False
    
    def _get_max_client_number_be_set(self,type):
        res={}
        if type=='Max':
            res=model_max_client
        elif type=='Value':
            if self.conf.get('ap_tag'):
                active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
                monitor_ap_info = lib.zd.ap.get_ap_info_by_mac(self.zd, active_ap.base_mac_addr)
                res[monitor_ap_info['model']] = self.conf['number']
            else:
                for model in model_max_client:
                    res[model]=self.conf['number']
        elif type=='Min':
            for model in model_max_client:
                res[model]=1
        elif type=='Random':
            for model in model_max_client:
                res[model]=randint(2,model_max_client[model]-1)
        elif type=='Lower':
            for model in model_max_client:
                res[model]=0
        elif type=='Lower':
            for model in model_max_client:
                res[model]=0
        elif type=='Higher':
            for model in model_max_client:
                res[model]=randint(model_max_client[model]+1,65535)
        model_list=[]
        for model in res:
            model_list.append(model)
        return res,model_list
            
        
        
    def _update_carrierbag(self):
        self.carrierbag['max_client_number']=self.model_client_number_cfg
        pass
