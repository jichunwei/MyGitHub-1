'''
Author: Cherry Cheng
Email: cherry.cheng@ruckuswireless.com
Description: 
    This script is to edit ap wlans settings.

'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP

class CB_AP_Config_Wlans(Test):
    required_components = []
    parameter_description = {'ip_addr':'IP address of Active Point',
                             'wlan_cfg_list':'Wlan configuration will be set',                             
                             }
    
    def config(self, conf):        
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._config_wlans()
        
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
        pass
        #self.carrierbag['wlans_cfg_list'] = self.wlans_cfg_list
    
    def _config_wlans(self):
        logging.info('Config AP wlans with specified setting')
        
        try:    
            ap_cli= None
            
            self.wlans_cfg_list = []
            
            ap_ip_addr = '192.168.0.1'        
            if self.conf.has_key('ip_addr'):
                ap_ip_addr = self.conf['ip_addr']                
            if self.conf.has_key('wlan_cfg_list'):
                wlans_cfg_list = self.conf['wlan_cfg_list']
                
            ap_fw_upgrade_cfg = {}
            if self.conf.has_key('ap_fw_upgrade_cfg'):
                ap_fw_upgrade_cfg = self.conf['ap_fw_upgrade_cfg']
                
            ap_cli_cfg = self._get_ap_cli_cfg(ap_fw_upgrade_cfg, ap_ip_addr)
            logging.info('AP CLI config: %s' % ap_cli_cfg)
            
            logging.info('Create AP CLI instance')
            ap_cli = RuckusAP(ap_cli_cfg)
            
            res_wlans_cfg = {}
            new_wlans_cfg_list = []
            
            if not wlans_cfg_list:
                raise Exception("No wlan config need to config.")            
            
            for wlan_cfg in wlans_cfg_list:
                logging.info('Get wlan name and wlan interface')
                #If wlan config has wlan_name and no wlan_if, will convert name to if.
                if wlan_cfg.has_key('wlan_name'):                
                    wlan_name = wlan_cfg['wlan_name']
                    wlan_if = ap_cli.wlan_name_to_if(wlan_name)
                else:
                    wlan_if = wlan_cfg['wlan_if']
                    wlan_name = ap_cli.wlan_if_to_name(wlan_if)
                    
                if not wlan_cfg.has_key('wlan_if'):
                    wlan_cfg['wlan_if'] = wlan_if
                if not wlan_cfg.has_key('wlan_name'):
                    wlan_cfg['wlan_name'] = wlan_name
                
                logging.info('Configure wlan [%s] with setting %s' % (wlan_name,wlan_cfg))
                ap_cli.cfg_wlan(wlan_cfg)
                
                if wlan_cfg['wpa_ver'].lower().find('auto') > -1:
                    wlan_cfg['wpa_ver'] = 'Auto'
                    
                logging.info('Get wlan config for %s via CLI' % (wlan_name,))
                
                if wlan_cfg['auth'].lower() == 'eap':
                    rm_key_list = ['key_string', 'username', 'password']
                    for key in rm_key_list:
                        if wlan_cfg.has_key(key):
                            wlan_cfg.pop(key)

                new_wlan_cfg = self._get_wlan_config(ap_cli, wlan_name, wlan_if)
                new_wlans_cfg_list.append(new_wlan_cfg)
                
                logging.info('Verify wlan configuration between set and get')
                res_wlan = {}
                
                for key,value in wlan_cfg.items():
                    #For 7211, no encryption TKIP/AES in get encryption command response.
                    err_msg = ''
                    if key == 'encryption': continue
                    if new_wlan_cfg.has_key(key):
                        new_value = new_wlan_cfg[key]
                        if key == 'auth' and value.lower() == 'eap':
                            if new_value.lower().find('eap') < 0:
                                err_msg = 'Value is different: Set value: [%s], Get value: [%s]' % (value, new_value)
                        else:
                            if value.lower() != new_value.lower():
                                err_msg = 'Value is different: Set value: [%s], Get value: [%s]' % (value, new_value)
                    else:
                        err_msg = 'The key does not exist in get wlan cfg.'
                        
                    if err_msg:
                        res_wlan[key] = err_msg
                     
                if res_wlan:
                    res_wlans_cfg[wlan_name] = res_wlan
                    
            #self.wlans_cfg_list = new_wlans_cfg_list
            
            if res_wlans_cfg:
                self.errmsg = 'Some wlans are not configured successfully: %s' % (res_wlans_cfg,)
                logging.warning(self.errmsg + 'Wlan_cfg_list=%s, Result=[%s]' % (wlans_cfg_list, res_wlans_cfg))
            else:
                logging.info('All wlans are configured successfully: %s' % (wlans_cfg_list,) )
                #Reboot CPE to make wlan configuration take effect.
                ap_cli.reboot()
                
            self.passmsg = 'Configure all wlans successfully: %s' % (wlans_cfg_list)
            
        except Exception, ex:
            self.errmsg = ex.message
        finally:
            if ap_cli:
                ap_cli.close()
                del(ap_cli)
    
    
    def _get_wlan_config(self, ap_cli, wlan_name, wlan_if):
        '''
        Get wlan configuration via AP cli based on wlan if.
        '''
        wlan_cfg = ap_cli.get_encryption(wlan_name, False)
        wlan_cfg['wlan_if'] = wlan_if
        wlan_cfg['wlan_name'] = wlan_name
        
        #Remove some items duplicate.
        if wlan_cfg.has_key('BeaconType'):
            wlan_cfg.pop('BeaconType')
        if wlan_cfg.has_key('WPA PassPhrase'):
            wlan_cfg.pop('WPA PassPhrase')
        if wlan_cfg.has_key('WPAEncryptionModes'):
            wlan_cfg.pop('WPAEncryptionModes')
            
        return wlan_cfg
    
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