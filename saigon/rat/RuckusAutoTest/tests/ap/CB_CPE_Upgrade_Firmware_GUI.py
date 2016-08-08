'''
Author: Cherry Cheng
Email: cherry.cheng@ruckuswireless.com
Description: 
    This script is to ...

'''
import os, re, time
import logging

from contrib.download import image_resolver as imgres

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components import create_metro_by_model
from RuckusAutoTest.components.lib.ap import upgrade_fw as up
from RuckusAutoTest.components.lib.mf import upgrade_fw as mfup

class CB_CPE_Upgrade_Firmware_GUI(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._upgrade_cpe_fw_gui()
        
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
        if self.carrierbag.has_key('image_file_path'):
            self.conf['image_file_path'] = self.carrierbag['image_file_path']
    
    def _update_carrier_bag(self):
        self.carrierbag['data_before_upgrade'] = self.data_before_upgrade
    
    def _upgrade_cpe_fw_gui(self):
        logging.info('Starting upgrading CPE firmware via GUI')
        
        try:
            logging.info('Getting config from self.conf')
            model = 'mf2211'
            ap_ip_addr = '192.168.0.1'
            test_type = 'gui'
            
            ap_cli = None
            ap_webui = None
            self.data_before_upgrade = {}
            
            if self.conf.has_key('model'):
                model = self.conf['model']
            if self.conf.has_key('ip_addr'):
                ap_ip_addr = self.conf['ip_addr']
            if self.conf.has_key('test_type'):
                test_type = self.conf['test_type']
                
            ap_fw_upgrade_cfg = self.conf['ap_fw_upgrade_cfg']
            
            logging.info('Get AP CLI config, firmware config and upgrade config.')
            ap_cli_cfg = self._get_ap_cli_cfg(ap_fw_upgrade_cfg, ap_ip_addr)
            fw_cfg = self._get_fw_cfg(ap_fw_upgrade_cfg, test_type)
            upgrade_cfg = self._get_upgrade_cfg(ap_fw_upgrade_cfg, model)
            
            logging.info('CPE CLI config: %s' % ap_cli_cfg)
            logging.info('Firmware config: %s' % fw_cfg)
            logging.info('Upgrade config: %s' % upgrade_cfg)
            
            logging.info('Creating AP CLI and WebUI instance')
            ap_cli = RuckusAP(ap_cli_cfg)            
            if not ap_cli:
                raise Exception("Can't create AP CLI for %s, %s" % (model,ap_ip_addr))
            
            ap_webui = create_metro_by_model(model, ap_ip_addr)
            if not ap_webui:
                raise Exception("Can't create AP CLI for %s, %s" % (model,ap_ip_addr))
            
            logging.info('Getting AP data before upgrade')            
            self.data_before_upgrade = up.get_verify_data(ap_cli)
            logging.info('AP data before upgrade is %s' % self.data_before_upgrade)
            
            logging.info('Comparing current firmware version with target version')
            current_fw_version = ap_cli.get_version().strip()
            
            self.passmsg = 'AP firmware was upgraded to %s via %s.' % (fw_cfg['fw_version'], test_type)
            
            if current_fw_version == fw_cfg['fw_version']:
                msg_same_version = 'Firmware version is same as target version: %s' % current_fw_version
                logging.warning(msg_same_version)
                self.passmsg = msg_same_version
            else:
                logging.info('Current fw version: %s, target version: %s' % (current_fw_version, fw_cfg['fw_version']))
                
                fw_cfg['fw_file_full_path'] = '%s/%s' % (fw_cfg['fw_path'], fw_cfg['fw_file_name'])
                if upgrade_cfg['proto'].lower() in ['tftp', 'ftp', 'http']:
                    logging.info('Creating control file for firmware file.')
                    fw_cfg['ctrl_file_full_path'] = up.create_control_file(ap_cli, fw_cfg['fw_file_full_path'])
                
                    logging.info('Remove ctrl and firmware file from server root path')
                    up.remove_file(fw_cfg['server_root_path'], fw_cfg['fw_file_name'])
                    up.remove_file(fw_cfg['server_root_path'], '%s.rcks' % fw_cfg['fw_file_name'])
                
                    if not fw_cfg['ctrl_file_full_path']:
                        self.errmsg = 'The control file was not created successfully. Firmware file: %s' % (fw_cfg['fw_file_full_path'])
                    else:
                        fw_cfg['ctrl_file_name'] = os.path.split(fw_cfg['ctrl_file_full_path'])[1]
                        
                logging.info('Firmware control config: %s' % (fw_cfg,))
                upgrade_cfg['control'] = self._gen_control_file_info(upgrade_cfg, fw_cfg)
                    
                if not upgrade_cfg['control']:
                    self.errmsg = 'The control file setting is incorrect. Upgrade config: %s, Fw ctrl config: %s' % (upgrade_cfg, fw_cfg)
                else:
                    timeout = ap_cli_cfg['timeout']   
                    timeout = 4000                       
                    res = self._upgrade_fw(ap_cli, ap_webui, upgrade_cfg, fw_cfg, timeout, False)
                    if res:
                        res_msg = "".join(res.values()) if type(res) == dict else res
                        if res_msg.find('No Upgrade') >-1:
                            self.passmsg = res
                        else:
                            self.errmsg = res
                        
        except Exception, ex:
            self.errmsg = ex.message
        finally:
            #pass
            if ap_cli:
                ap_cli.close()
                del(ap_cli)   
            
    def _upgrade_fw(self, ap_cli, ap_webui, upgrade_cfg, fw_cfg, timeout, is_first_check = False):
        '''
        Upgrade firmware via cli/gui.        
        '''
        test_type = fw_cfg['test_type']
        if not upgrade_cfg['auto'] or (upgrade_cfg['auto'] and is_first_check):    
            logging.info('Copy ctrl and firmware file to server root dir.')
            up.copy_file(fw_cfg['server_root_path'], fw_cfg['fw_file_full_path'], fw_cfg['fw_file_name'])
            up.copy_file(fw_cfg['server_root_path'], fw_cfg['ctrl_file_full_path'], fw_cfg['ctrl_file_name'])
            
        logging.info('Upgrading AP firmware to %s via %s' % (fw_cfg['fw_version'], test_type))
        
        #Change firstcheck via cli.
        if upgrade_cfg['auto']:
            ap_cli.change_fw_setting({'firstcheck': upgrade_cfg['firstcheck']})
        
        res = mfup.upgrade_fw_via_gui(ap_webui, upgrade_cfg)
                
        if upgrade_cfg['auto']:
            logging.info('Waiting for first check: %s minutes' % upgrade_cfg['firstcheck'])
            #Wait for firstcheck minutes, then copy files.        
            time.sleep(int(upgrade_cfg['firstcheck'])*60+20)
            
            if not is_first_check:
                logging.info('Copying ctrl and firmware file to server root dir.')
                up.copy_file(fw_cfg['server_root_path'], fw_cfg['fw_file_full_path'], fw_cfg['fw_file_name'])
                up.copy_file(fw_cfg['server_root_path'], fw_cfg['ctrl_file_full_path'], fw_cfg['ctrl_file_name'])
                
                logging.info('Waiting interval: (%s) minutes' % upgrade_cfg['interval'])
                time.sleep(int(upgrade_cfg['interval'])*60)
                
                #Wait 3 mins when ap is upgrading.
                logging.info('Waiting 5 minutes for AP upgrading')
                time.sleep(5*60)
                
        return res    

    def _gen_control_file_info(self, upgrade_cfg, fw_cfg):
        '''
        Generate control file name.
        For tftp and ftp, it is ctrl_file_name.
        For http, the format is http://<server_ip>/<ctrl_cfile_name>
        For local, it is fw file path in local.
        '''
        full_fw_file_path = fw_cfg['fw_file_full_path']
        protocol = upgrade_cfg['proto']         
        control = ''
        
        if protocol.lower() == 'local':
            #For local methods, need to add local_file_name parameter.
            control = full_fw_file_path
        else:
            server_ip = upgrade_cfg['host']
            ctrl_file_name = fw_cfg['ctrl_file_name']
            if protocol.lower() == 'http':
                control = 'http://%s/%s' % (server_ip, ctrl_file_name)        
            else:
                control = ctrl_file_name
            
        return control
    
    def _get_ap_cli_cfg(self, ap_fw_upgrade_cfg, ap_ip_addr):
        '''
        Get ap config based on firmware upgrade config, model, ap_ip_addr.
        '''
        ap_cli_cfg = {'ip_addr' : '192.168.0.1',
                      'username': 'super',
                      'password': 'sp-admin',
                      'port'    : 23,
                      'telnet'  : True,
                      'timeout' : 360,
                      }
        
        ap_common_conf = ap_fw_upgrade_cfg['ap_common_conf']
        ap_cli_cfg.update(ap_common_conf)
        ap_cli_cfg['ip_addr'] = ap_ip_addr
        
        return ap_cli_cfg
    
    def _get_fw_cfg(self, ap_fw_upgrade_cfg, test_type):
        '''
        Get firmware config based on image_file_path. 
        '''
        fw_cfg = {'fw_path': '',
                  'fw_file_name': '',
                  'fw_version': '',
                  'server_root_path': '',
                  'test_type': 'cli'}
        
        up_cfg_common = ap_fw_upgrade_cfg['up_cfg_common']
        
        fw_cfg['fw_path'] = os.getcwd()
        fw_cfg['server_root_path'] = up_cfg_common['server_root_path']
        fw_cfg['test_type'] = test_type        
        fw_cfg['fw_file_name'] = self._get_image_file(self.conf['image_file_path'])
        #image_file_path = self.conf['image_file_path']
        #image_file_path = self._get_image_file(image_file_path)
            
        version_ptn_list = ['(?<=_)\S+(?=_uImage)','(?<=_)\S+(?=\.Bl7)','(?<=\.)\S+(?=\.Bl7)']  #7211_4.5.0.0.61_uImage,2225_4.4.2.0.78.Bl7, 2225.77.Bl7
        is_match = False
        for ptn in version_ptn_list:
            matcher = re.search(ptn, fw_cfg['fw_file_name'], re.I)
            if matcher:
                is_match = True
                fw_cfg['fw_version'] = matcher.group(0)
                break
        
        if not is_match:
            err_msg = 'Get firmware version error, file name is %s' % fw_cfg['fw_file_name']
            logging.warning(err_msg)
            
        #temp solve the version. The file name is 2255.78.Bl7.
        mainline_version = '0.0.0.0' #'4.4.2.0'
        if not fw_cfg['fw_version'].find('.') > -1:
            fw_cfg['fw_version'] = '%s.%s' % (mainline_version, fw_cfg['fw_version'])    
    
        return fw_cfg
    
    def _get_upgrade_cfg(self, ap_fw_upgrade_cfg, model):
        '''
        Get upgrade config based on ap_fw_upgrade_cfg, model.
        '''
        upgrade_cfg = {'control': '',
                       'proto':'tftp',
                       'host':'',
                       'user':'', # use for ftp only
                       'password':'', # use for ftp only
                       'auto': True,
                       'firstcheck':'3',
                       'interval':'60',
                       }
        
        if self.conf.has_key('up_cfg'):
            upgrade_cfg.update(self.conf['up_cfg'])
            
        up_cfg_common = ap_fw_upgrade_cfg['up_cfg_common']
        upgrade_cfg['host'] = up_cfg_common['server_ip']
        upgrade_cfg['user'] = up_cfg_common['ftp_user_name']
        upgrade_cfg['password'] = up_cfg_common['ftp_password']
        
        return upgrade_cfg
    
    def _get_image_file(self, image_file_path):
        '''
        Get image file name from tar.gz file.
        '''
        img_ptn = '[0-9]+.*[_uImage,\.Bl7]'
        fw_img_full_path = imgres.get_image(image_file_path, filetype = img_ptn)
        fw_img_filename = fw_img_full_path.split("/")[-1]
        
        return fw_img_filename
