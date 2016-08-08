'''
Author: Cherry Cheng
Email: cherry.cheng@ruckuswireless.com
Description: 
    This script is to ...

'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP

class CB_AP_Get_Wlans_Config(Test):
    required_components = []
    parameter_description = {'ip_addr':'ip address of Active Point',
                             'wlan_if_list':'wlan if list will to get',                             
                             }
    
    def config(self, conf):        
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._get_wlan_config()
        
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
        if self.carrierbag.has_key('ap_fw_upgrade_cfg'):
            self.conf['ap_fw_upgrade_cfg'] = self.carrierbag['ap_fw_upgrade_cfg']
    
    def _update_carrier_bag(self):
        self.carrierbag['wlans_cfg_list'] = self.wlans_cfg_list
    
    def _get_wlan_config(self):
        logging.info('Get AP wlans configuration')
        
        try:
            if self.conf.has_key('ip_addr'):
                ap_ip_addr = self.conf['ip_addr']
            else:
                ap_ip_addr = '192.168.0.1'
            if self.conf.has_key('wlan_name_list'):
                wlan_name_list = self.conf['wlan_name_list']
            else:
                wlan_name_list = ['home']
                
            if self.conf.has_key('ap_fw_upgrade_cfg'):
                ap_fw_upgrade_cfg = self.conf['ap_fw_upgrade_cfg']
            else:
                ap_fw_upgrade_cfg = {}
                
            ap_cli_cfg = self._get_ap_cli_cfg(ap_fw_upgrade_cfg, ap_ip_addr)
            
            logging.info('AP CLI config: %s' % ap_cli_cfg)
            
            logging.info('Create AP CLI instance')
            ap_cli = RuckusAP(ap_cli_cfg)
            
            self.wlans_cfg_list = self._get_wlans_config(ap_cli, wlan_name_list)
                
            if self.wlans_cfg_list:
                self.passmsg = 'Get Home Wlan config successfully: %s' % (self.wlans_cfg_list)
            else:
                self.errmsg = 'Get wlan config failed for %s, result is %s' % (wlan_name_list, self.wlans_cfg_list)            
                    
        except Exception, ex:
            self.errmsg = ex.message
        finally:
            #pass
            if ap_cli:
                ap_cli.close()
                del(ap_cli)     
                
                
    def _get_wlans_config(self, ap_cli, wlan_name_list):
        '''
        Get wlans configuration via AP cli based on wlan if list.
        '''
        if not wlan_name_list:
            wlan_name_list = ap_cli.get_wlan_list()
        
        wlans_cfg_list = []
        for wlan_name in wlan_name_list:
            wlan_cfg = ap_cli.get_encryption(wlan_name, False)
            
            #Remove some items duplicate.
            if wlan_cfg.has_key('BeaconType'):
                wlan_cfg.pop('BeaconType')
            if wlan_cfg.has_key('WPA PassPhrase'):
                wlan_cfg.pop('WPA PassPhrase')
            if wlan_cfg.has_key('WPAEncryptionModes'):
                wlan_cfg.pop('WPAEncryptionModes')
            
            wlans_cfg_list.append(wlan_cfg)
            
        return wlans_cfg_list
                   
    
    def _get_ap_cli_cfg(self, ap_fw_upgrade_cfg, ap_ip_addr):
        '''
        Get ap config based on firmware upgrade configr, model, ap_ip_addr.
        '''
        ap_cli_cfg = {'ip_addr' : '192.168.0.1',
                      'username': 'super',
                      'password': 'sp-admin',
                      'port'    : 23,
                      'telnet'  : True,
                      'timeout' : 360,
                      }
        
        if ap_fw_upgrade_cfg:
            ap_common_conf = ap_fw_upgrade_cfg['ap_common_conf']
            ap_cli_cfg.update(ap_common_conf)
        ap_cli_cfg['ip_addr'] = ap_ip_addr
            
        return ap_cli_cfg