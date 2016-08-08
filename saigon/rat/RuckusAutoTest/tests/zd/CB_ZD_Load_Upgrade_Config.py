'''
Author: Cherry Cheng
Email: cherry.cheng@ruckuswireless.com
Description: 
    This script is to ...

'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.Ratutils import load_config_file

class CB_ZD_Load_Upgrade_Config(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._load_config()
        
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
        self.carrierbag['zd_fw_upgrade_cfg'] = self.zd_fw_upgrade_cfg
        
    def _load_config(self):
        '''
        Read ZD firmware upgrade configurations from config file.
        '''
        try:
            if self.conf.has_key('cfg_file_name'):
                cfg_file_name = self.conf['cfg_file_name']
            else:
                cfg_file_name = './RuckusAutoTest/common/ZD_Upgrade_Info_Default.inf'
                
            logging.info('Read upgrade information from file [%s]' % cfg_file_name)
            cfg_dict = self._read_config_file_to_dict(cfg_file_name)        
            self.zd_fw_upgrade_cfg = cfg_dict
            
            self.passmsg = "Get config from file successfully."
            logging.info('ZD upgrade configurations: %s' % cfg_dict)
            
        except Exception, ex:
            self.errmsg = ex.message
                    
    
    def _read_config_file_to_dict(self, file_name):
        '''
        Read config file and put setting to a dict.
        '''
        cfg_info_file = file_name
        
        #Set default config dict.
        cfg_dict = {'build_server': '192.168.0.252',
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
        if cfg_info.has_key('build_server'):
            cfg_dict['build_server'] = eval(cfg_info.pop('build_server'))
        if cfg_info.has_key('up_cfg_common'):
            cfg_dict['up_cfg_common'] = eval(cfg_info.pop('up_cfg_common'))
        if cfg_info.has_key('target_ip_list'):
            cfg_dict['target_ip_list'] = eval(cfg_info.pop('target_ip_list'))
        
        #Get upgrade config for each model.
        for item_key in cfg_info.keys():
            if item_key.lower().startswith('up_cfg'):
                model = item_key.split('_')[-1]
                cfg_dict['up_cfg'][model] = eval(cfg_info.pop(item_key))
                        
        return cfg_dict       