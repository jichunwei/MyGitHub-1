# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""Description:

    Prerequisite (Assumptions about the state of the testbed/DUT):

    Required components:
    Test parameters:
    Result type: PASS/FAIL
    Results: PASS
             FAIL otherwise

    Messages:
        - If PASS,
        - If FAIL, prints out the reason for failure

    Test procedure:
    1. Config:
        -
    2. Test:
        -
    3. Cleanup:
        -

    How is it tested: (to be completed by test code developer)
    
"""
import logging
import os
import re

from RuckusAutoTest.models import Test

from contrib.download import image_resolver as imgres

class CB_AP_Download_Image(Test):
    required_components = []
    parameter_description = {'ap_build_stream':'build stream of Active Point',
                             'ap_bno':'build no of Active Point',                             
                             }

    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()        
    
    def test(self):
        self._download_ap_image()
        
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
        self.carrierbag['image_file_path'] = self.image_file_path

    def _download_ap_image(self):
        '''
        Download ap image from yanming server.
        '''
        try:
            logging.info('Get the image information build server, build stream and build no')
            
            if self.conf.has_key('ap_fw_upgrade_cfg'):
                ap_fw_upgrade_cfg = self.conf['ap_fw_upgrade_cfg']
                model = 'mf2211'
                if self.conf.has_key('model'):
                    model = self.conf['model']
                up_flag = True
                if self.conf.has_key('up_flag'):
                    up_flag = self.conf['up_flag']
                
                all_models_up_cfg = ap_fw_upgrade_cfg['up_cfg']
                build_server = ap_fw_upgrade_cfg['build_server']
                
                if all_models_up_cfg.has_key(model):
                    model_up_cfg = all_models_up_cfg[model]
                    if up_flag:
                        ap_build_stream = model_up_cfg['target_build_stream']
                        ap_bno = int(model_up_cfg['target_bno'])
                    else:
                        ap_build_stream = model_up_cfg['baseline_build_stream']
                        ap_bno = int(model_up_cfg['baseline_bno'])                                
                else:
                    model_up_cfg = {}
                    self.errmsg = 'No upgrade config for specified model %s' % (model,)
            else:
                ap_build_stream = self.conf['ap_build_stream']
                ap_bno = self.conf['ap_bno']
                if self.conf.has_key('build_server'):
                    build_server = self.conf['build_server']
                else:
                    build_server = None
                    
            self.image_file_path = self._download_image(build_server, ap_build_stream, ap_bno)
                                       
            logging.info('Firmware config: %s' % self.image_file_path)
            self.passmsg = "Download and get image files for %s: location[%s], Build stream[%s], Build no[%s]" % \
                                (model, os.getcwd(), ap_build_stream, ap_bno)  
        except Exception, ex:
            self.errmsg = ex.message        

    def _escape(self, file_path):
        expr = "[/|\\^\\\\]"
        return re.sub(expr, "\\\\", file_path)        
    
    def _download_image(self, build_server, build_stream, fw_bno):
        '''
        Download ap image from build server based on build stream and build no,
        and save as <Build stream>.<Build no>.tar.gz
        '''      
        chk_name_list = ["%s.%s.tar.gz" % (build_stream, fw_bno),  #MM2225_mainline.85.tar.gz                         
                         "%s.%s.bl7" % (build_stream, fw_bno),     #MM2225_mainline.85.bl7
                         ]
        
        exist, file_name = self._chk_img_file_local(chk_name_list)
        
        if not exist:
            logging.info('Download image from server: [%s:%s:%s]' % (build_server, build_stream, fw_bno))
            if build_server:            
                fname = imgres.download_build(build_stream, fw_bno, build_server)
            else:
                fname = imgres.download_build(build_stream, fw_bno)
        else:
            logging.info('Image exist in local computer: %s' % (file_name))
            fname = file_name            
        fw_tar_filename = self._escape(os.path.realpath(fname))
        
        #filetype='(\d+\.){1,5}Bl7$' #'.+\.Bl7$', 
        #fw_img_full_path = imgres.get_image(fw_tar_filename, filetype = filetype)
        #fw_img_filename = fw_img_full_path.split("/")[-1]
        
        return fw_tar_filename  
    
    def _chk_img_file_local(self, chk_name_list):
        result = False
        file_name = ''
        for chk_name in chk_name_list:
            if os.path.exists(chk_name):
                file_name = chk_name            
                result = True
                break
            
        return result, file_name
        