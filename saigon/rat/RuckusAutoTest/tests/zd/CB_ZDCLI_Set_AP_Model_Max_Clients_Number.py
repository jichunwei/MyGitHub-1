import logging
from random import randint

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import ap_group
from RuckusAutoTest.components.lib.zdcli import configure_ap_group as apgcli
from RuckusAutoTest.common.lib_Constant import model_max_clients_mapping as model_max_client
from RuckusAutoTest.common import lib_Constant as const

class CB_ZDCLI_Set_AP_Model_Max_Clients_Number(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        logging.info('set model mex clients number in zd cli')
        apgcli.set_multi_model_max_clients_number(self.zdcli, self.conf['grp_name'], self.model_client_number_cfg)
        logging.info('get model mex clients number in web')
        self.get_cfg=ap_group.get_multi_ap_model_max_client_by_name(self.zd, self.conf['grp_name'], self.model_list)
        
        if not self.set_correct_value:
            self.model_client_number_cfg=self.carrierbag['max_client_number']
            
        for model in self.model_client_number_cfg:
            if model not in self.get_cfg:
                self.errmsg+='model %s number not get from web,'%model
            elif int(self.model_client_number_cfg[model])!=int(self.get_cfg[model]):
                self.errmsg+='model %s number not match cli set %s web get %s,'%(model,self.model_client_number_cfg[model],self.get_cfg[model])
        
        if self.set_correct_value:
            self._update_carrierbag()
        if self.errmsg:
            return self.returnResult('FAIL',self.errmsg)
        if not self.set_correct_value:
            return self.returnResult('PASS', "max clients number with wrong value can't be set")
        else:
            return self.returnResult('PASS', "set max clients number in cli successfully and verify in web ok")
    
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
            self.set_correct_value=True
        else:
            self.set_correct_value=False

    def _get_max_client_number_be_set(self,type):
        res={}
        if type=='Max':
            res=model_max_client
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
