'''
Author: Cherry Cheng
Email: cherry.cheng@ruckuswireless.com
Description: 
    This script is to ...

'''
import time
import re
import logging

from contrib.download import image_resolver as imgres

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components.lib.ap import upgrade_fw as up

class CB_AP_Verify_Firmware_Version(Test):
    def config(self, conf):        
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        logging.info("Sleep %s seconds before checking firmware version" % self.sleep_time)
        if self.sleep_time:
            time.sleep(self.sleep_time)
        self._verify_ap_fw_version()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {'sleep_time': 60 #seconds
                     }
        self.conf.update(conf)
        
        self.sleep_time = self.conf['sleep_time']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('image_file_path'):
            self.conf['image_file_path'] = self.carrierbag['image_file_path']
        if self.carrierbag.has_key('ap_fw_upgrade_cfg'):
            self.conf['ap_fw_upgrade_cfg'] = self.carrierbag['ap_fw_upgrade_cfg']
        if self.carrierbag.has_key('data_before_upgrade'):
            self.conf['data_before_upgrade'] = self.carrierbag['data_before_upgrade']
    
    def _update_carrier_bag(self):
        pass
    
    def _verify_ap_fw_version(self):
        logging.info('Verify AP firmware version')
        
        try:
            ap_cli = None
            if self.conf.has_key('ip_addr'):
                ap_ip_addr = self.conf['ip_addr']
            else:
                ap_ip_addr = '192.168.0.1'
                
            if self.conf.has_key('expect_version'):
                expect_version = self.conf['expect_version']
                ap_fw_upgrade_cfg = {}
            else:
                #For the upgrade case.
                ap_fw_upgrade_cfg = self.conf['ap_fw_upgrade_cfg']
                expect_version = self._get_version_from_image_file(self.conf['image_file_path'])
            
            self.passmsg = 'The AP version is correct %s' % expect_version    
            ap_cli_cfg = self._get_ap_cli_cfg(ap_ip_addr, ap_fw_upgrade_cfg)
            
            logging.info('AP CLI config: %s' % ap_cli_cfg)
            logging.info('Firmware config: %s' % expect_version)
            
            logging.info('Create ap cli and webui instance')
            ap_cli = RuckusAP(ap_cli_cfg)
            
            res_d = {}
            if self.conf.has_key('data_before_upgrade'):
                #Verify data before and after upgrade.
                data_before_upgrade = self.conf['data_before_upgrade']
                logging.info('Get data after upgrade')
                
                data_after_upgrade = up.get_verify_data(ap_cli)
                
                logging.info('Verify data before and after upgrade.')
                res_data_d = self._verify_data(data_before_upgrade, data_after_upgrade)
                if res_data_d:
                    res_d['DataValidation'] = res_data_d
                
            logging.info('Verify AP current version')
            res = up.verify_ap_fw_version(ap_cli, ap_cli_cfg, expect_version)
            if res:
                res_d['VersionValidation'] = res
                
            if res_d:
                self.errmsg = res_d
                    
        except Exception, ex:
            self.errmsg = ex.message
        finally:
            #pass
            if ap_cli:
                ap_cli.close()
                del(ap_cli)            
    
    def _verify_data(self, data_before_upgrade, data_after_upgrade):
        '''
        Verify data before and after upgrade:
        Running_image should be different if upgrade successfully.
        Other data should be same before and after upgrade. 
        '''
        res_data_d = {}
        if data_before_upgrade and data_after_upgrade:
            for key,value in data_before_upgrade.items():
                err_msg = ''
                if data_after_upgrade.has_key(key):
                    if key == 'running_image':
                        if value == data_after_upgrade[key]:
                            err_msg = 'The running_image is incorrect. [Value is same as before upgrade]'
                    else:
                        if not value:
                            err_msg = 'The value of %s is incorrect: %s' % (key,value)
                        elif value.lower() != data_after_upgrade[key].lower():
                            err_msg = '%s is changed after upgraded, Old Value: %s, New Value: %s.' % (key, value, data_after_upgrade[key])
                else:
                    err_msg = '%s does not exist in new data dict.' % key
                    
                if err_msg:
                    res_data_d[key] = err_msg
                    logging.warning(err_msg)
                    
        return res_data_d
    
    def _get_ap_cli_cfg(self, ap_ip_addr, ap_fw_upgrade_cfg):
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
    
    def _get_version_from_image_file(self, image_file_path):
        '''
        Get firmware version from image file. 
        Input: .tar.gz
        (zd1k_9.2.0.99.651.ap_9.2.0.99.698.img)
        Output: 9.2.0.0.99.651
        '''
        img_ptn = '[0-9]+.*[_uImage,\.Bl7]'
        fw_img_full_path = imgres.get_image(image_file_path, filetype = img_ptn)
        
        #filetype='(\d+\.){1,5}Bl7$' #'.+\.Bl7$',
        version_ptn_list = ['[0-9]+_(?P<version>.+)_uImage','[0-9]+_(?P<version>.+)\.Bl7','[0-9]+\.(?P<version>.+)\.Bl7']  
        #7211_4.5.0.0.61_uImage,2225_4.4.2.0.78.Bl7, 2225.77.Bl7
        is_match = False
        for ptn in version_ptn_list:
            matcher = re.search(ptn, fw_img_full_path, re.I)
            if matcher:
                is_match = True
                fw_version = matcher.groupdict()['version']
                break
        if not is_match:
            err_msg = 'Get firmware version error, file name is %s' % image_file_path
            logging.warning(err_msg)
            raise Exception(err_msg)
        
        #temp solve the version. The file name is 2255.78.Bl7.
        mainline_version = '0.0.0.0' #'4.4.2.0'
        if not fw_version.find('.') > -1:
            fw_version = '%s.%s' % (mainline_version, fw_version)    
    
        return fw_version 
        