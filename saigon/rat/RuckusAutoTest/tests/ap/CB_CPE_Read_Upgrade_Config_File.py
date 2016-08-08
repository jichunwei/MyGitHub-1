'''
Author: Cherry Cheng
Email: cherry.cheng@ruckuswireless.com
Description: 
    This script is to ...

'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.Ratutils import load_config_file

class CB_CPE_Read_Upgrade_Config_File(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._get_config()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass    
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['ap_fw_upgrade_cfg'] = self.ap_fw_upgrade_cfg
        
    def _get_config(self):
        '''
        Read firmware upgrade configurations from config file.
        '''
        try:
            if self.conf.has_key('cfg_file_name'):
                cfg_file_name = self.conf['cfg_file_name']
            else:
                cfg_file_name = None
                
            cfg_dict = self._read_config_file_to_dict(cfg_file_name)        
            self.ap_fw_upgrade_cfg = cfg_dict
            
            self.passmsg = "Get config from file successfully."
            logging.info('Config details: %s' % cfg_dict)
            
        except Exception, ex:
            self.errmsg = ex.message
                    
    
    def _read_config_file_to_dict(self, file_name = None):
        '''
        Read config file and put setting to a dict.
        '''
        if file_name:
            cfg_info_file = file_name
        else: 
            cfg_info_file = "./RuckusAutoTest/common/CPE_Testbed_Info_Default.inf"
        
        #Set default config dict.
        cfg_dict = {'sta_ip_list': ['192.168.1.11'],
                    'target_ip_list': ['192.168.0.2'],
                    'ap_common_conf': {'username': 'super','password':'sp-admin', 'telnet':False},
                    'build_server': '192.168.0.10',
                    'up_cfg_common': {#'fw_path':'C:/rwqaauto/firmware/backup_d',
                                      'server_root_path':'C:/rwqaauto/firmware',
                                      'server_ip':'192.168.10.100',
                                      'ftp_user_name':'cherry',
                                      'ftp_password':'123456'},
                    'up_cfg': {},
                    }
        
        #Read config file to a dict.    
        cfg_info = load_config_file(cfg_info_file)
        
        if cfg_info.has_key('name'):
            del(cfg_info['name'])
        if cfg_info.has_key('location'):
            del(cfg_info['location'])
        if cfg_info.has_key('owner'):
            del(cfg_info['owner'])
        
        #Get setting from cfg_info dict. 
        if cfg_info.has_key('sta_ip_list'):
            cfg_dict['sta_ip_list'] = eval(cfg_info.pop('sta_ip_list'))
        if cfg_info.has_key('target_ip_list'):
            cfg_dict['target_ip_list'] = eval(cfg_info.pop('target_ip_list'))
        if cfg_info.has_key('ap_common_conf'):
            cfg_dict['ap_common_conf'] = eval(cfg_info.pop('ap_common_conf'))
            
        if cfg_info.has_key('build_server'):
            cfg_dict['build_server'] = eval(cfg_info.pop('build_server'))
        if cfg_info.has_key('up_cfg_common'):
            cfg_dict['up_cfg_common'] = eval(cfg_info.pop('up_cfg_common'))
        
        #Get upgrade config for each model.
        for item_key in cfg_info.keys():
            if item_key.lower().startswith('up_cfg'):
                model = item_key.split('_')[-1]
                cfg_dict['up_cfg'][model] = eval(cfg_info.pop(item_key))
                        
        return cfg_dict
        